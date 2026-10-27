"""Zetaris client: mock by default; live via UI-proxy (preferred) or direct REST.

Preferred live path — official getting-started helpers
(https://github.com/zetaris/getting-started):

  POST {ZETARIS_BASE_URL}/api/proxy/sql-editor/sqls/run-query
  Headers: Authorization: Bearer <key>, X-Org-ID, X-Request-ID
  Body: {"sql": "...", "limit": N}  # optional engineId

  GET  {ZETARIS_BASE_URL}/api/proxy/lightning-database/databases

Fallback direct REST (older KB / OpenSqlQuery style):
  POST {ZETARIS_REST_URL}/...  with {"select": "...", "pageLimit": N}

Env:
  USE_MOCK=1 (default)
  ZETARIS_CHANNEL=proxy|direct   (default proxy when live)
  ZETARIS_BASE_URL, ZETARIS_ORG_ID, ZETARIS_API_KEY
  ZETARIS_REST_URL (direct only)
  ZETARIS_QUERY_LIMIT, ZETARIS_ENGINE_ID
"""

from __future__ import annotations

import os
import re
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

import httpx

from whytrace.mock_data import all_tables


class ZetarisError(RuntimeError):
    """User-facing Zetaris failure with a fix hint."""


@dataclass
class QueryResult:
    sql: str
    rows: list[dict[str, Any]]
    source: str  # mock | zetaris-proxy | zetaris-direct
    meta: dict[str, Any] = field(default_factory=dict)


def _truthy_mock(raw: str | None) -> bool:
    return (raw or "1").strip() not in {"0", "false", "False", "no", "NO"}


class ZetarisClient:
    def __init__(self) -> None:
        self.use_mock = _truthy_mock(os.getenv("USE_MOCK"))
        self.channel = (os.getenv("ZETARIS_CHANNEL") or "proxy").strip().lower()
        if self.channel not in {"proxy", "direct"}:
            self.channel = "proxy"
        self.base_url = (os.getenv("ZETARIS_BASE_URL") or "http://localhost:3000").rstrip("/")
        self.rest_url = (os.getenv("ZETARIS_REST_URL") or "http://localhost:8888/api/v1.0").rstrip(
            "/"
        )
        self.org_id = (os.getenv("ZETARIS_ORG_ID") or "").strip()
        self.api_key = (os.getenv("ZETARIS_API_KEY") or "").strip()
        self.username = (os.getenv("ZETARIS_USERNAME") or "").strip()
        self.password = (os.getenv("ZETARIS_PASSWORD") or "").strip()
        try:
            self.page_limit = max(1, int(os.getenv("ZETARIS_QUERY_LIMIT", "50")))
        except ValueError as exc:
            raise ZetarisError("ZETARIS_QUERY_LIMIT must be a positive integer.") from exc
        self.engine_id = (os.getenv("ZETARIS_ENGINE_ID") or "").strip() or None

    def status(self) -> dict[str, Any]:
        if self.use_mock:
            return {
                "mode": "mock",
                "tables": list(all_tables().keys()),
                "hint": "Set USE_MOCK=0 and fill Zetaris env to go live (see INTEGRATION_NOTES.md).",
            }
        auth_ok = bool(self.api_key) or bool(self.username and self.password)
        org_ok = bool(self.org_id and re.fullmatch(r"[0-9]+", self.org_id))
        return {
            "mode": "live" if (auth_ok and org_ok) else "live-unconfigured",
            "channel": self.channel,
            "base_url": self.base_url if self.channel == "proxy" else self.rest_url,
            "org_id_set": org_ok,
            "api_key_set": bool(self.api_key),
            "username_password_set": bool(self.username and self.password),
            "missing": self._missing_config(),
        }

    def _missing_config(self) -> list[str]:
        missing: list[str] = []
        if not (self.org_id and re.fullmatch(r"[0-9]+", self.org_id)):
            missing.append("ZETARIS_ORG_ID (numeric, Management → Organisation)")
        if not self.api_key and not (self.username and self.password):
            missing.append("ZETARIS_API_KEY (or ZETARIS_USERNAME + ZETARIS_PASSWORD)")
        if self.channel == "proxy" and not re.fullmatch(r"https?://[^/]+", self.base_url):
            missing.append("ZETARIS_BASE_URL must be an HTTP(S) origin with no path")
        return missing

    def _require_live_config(self) -> None:
        missing = self._missing_config()
        if missing:
            raise ZetarisError(
                "Zetaris live mode is not configured.\n"
                "Missing / invalid:\n  - "
                + "\n  - ".join(missing)
                + "\nFix: copy values into .env, or set USE_MOCK=1 for local demo.\n"
                "Guide: INTEGRATION_NOTES.md §30-minute live switch."
            )

    def _auth_headers(self, token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "X-Org-ID": self.org_id,
            "X-Request-ID": str(uuid.uuid4()),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _resolve_token(self, client: httpx.Client) -> str:
        if self.api_key:
            return self.api_key
        # UI login fallback (same as zetaris/getting-started scripts/zetaris_api.py)
        try:
            resp = client.post(
                f"{self.base_url}/api/auth/login",
                headers={"Content-Type": "application/json", "X-Request-ID": str(uuid.uuid4())},
                json={"username": self.username, "password": self.password},
                timeout=30.0,
            )
        except httpx.RequestError as exc:
            raise ZetarisError(
                f"Cannot reach Zetaris UI at {self.base_url}: {exc}\n"
                "Check ZETARIS_BASE_URL (origin only, e.g. https://your-instance)."
            ) from exc
        if resp.status_code >= 400:
            raise ZetarisError(
                f"Zetaris login failed: HTTP {resp.status_code}. "
                "Check ZETARIS_USERNAME / ZETARIS_PASSWORD, or create an API key instead."
            )
        login = resp.json()
        token = None
        if isinstance(login, dict):
            token = login.get("idToken") or login.get("token") or login.get("accessToken")
        if not token:
            raise ZetarisError("Zetaris login did not return an access token.")
        return str(token)

    def _raise_http(self, method: str, path: str, resp: httpx.Response) -> None:
        body_preview = (resp.text or "")[:400]
        hint = ""
        if resp.status_code in {401, 403}:
            hint = (
                " → Create a fresh API key: Management → API Tokens. "
                "Confirm X-Org-ID is the numeric organisation ID."
            )
        elif resp.status_code == 400:
            hint = (
                " → Often a bad Org ID or non-UUID X-Request-ID. "
                "Confirm ZETARIS_ORG_ID is digits only."
            )
        elif resp.status_code == 404:
            hint = (
                " → For proxy channel, ZETARIS_BASE_URL must be the web UI origin "
                "(not /api/v1.0). Path used: " + path
            )
        raise ZetarisError(
            f"{method} {path} failed: HTTP {resp.status_code}. {body_preview}{hint}"
        )

    def ping(self) -> dict[str, Any]:
        """Live connectivity check. Mock returns local table names."""
        if self.use_mock:
            return {"ok": True, "mode": "mock", "tables": list(all_tables().keys())}
        self._require_live_config()
        if self.channel == "proxy":
            return self._proxy_list_databases()
        # direct: try SELECT 1 via open-sql if configured
        result = self.execute_sql("SELECT 1")
        return {"ok": True, "mode": "direct", "rows": result.rows, "meta": result.meta}

    def execute_sql(self, sql: str) -> QueryResult:
        if self.use_mock:
            return self._mock_sql(sql)
        self._require_live_config()
        if self.channel == "proxy":
            return self._proxy_run_sql(sql)
        return self._direct_open_sql(sql)

    def crash_density_by_zone(self) -> QueryResult:
        sql = (
            "SELECT zone_id, COUNT(*) AS crashes, "
            "SUM(injured) AS injured, SUM(fatal) AS fatal "
            "FROM NY_VEHICLE_COLLISIONS.crash "
            "GROUP BY zone_id ORDER BY crashes DESC"
        )
        if self.use_mock:
            return QueryResult(sql=sql, rows=self._mock_crash_density(), source="mock")
        return self.execute_sql(sql)

    def companies_in_zones(self, zone_ids: list[str]) -> QueryResult:
        ids = ", ".join(f"'{z}'" for z in zone_ids) or "''"
        sql = (
            f"SELECT company_id, name, zone_id, industry "
            f"FROM COMPANY_DNS.companies WHERE zone_id IN ({ids})"
        )
        if self.use_mock:
            wanted = set(zone_ids)
            rows = [c for c in all_tables()["companies"] if c["zone_id"] in wanted]
            return QueryResult(sql=sql, rows=rows, source="mock")
        return self.execute_sql(sql)

    def zones_lookup(self, zone_ids: list[str]) -> QueryResult:
        ids = ", ".join(f"'{z}'" for z in zone_ids) or "''"
        sql = (
            "SELECT zone_id, name, borough, taxi_trips_k "
            f"FROM NY_TAXI.taxi_zones WHERE zone_id IN ({ids})"
        )
        if self.use_mock:
            wanted = set(zone_ids)
            rows = [z for z in all_tables()["zones"] if z["zone_id"] in wanted]
            return QueryResult(sql=sql, rows=rows, source="mock")
        return self.execute_sql(sql)

    def _proxy_list_databases(self) -> dict[str, Any]:
        path = "/api/proxy/lightning-database/databases"
        with httpx.Client(timeout=30.0) as client:
            token = self._resolve_token(client)
            try:
                resp = client.get(
                    f"{self.base_url}{path}",
                    headers=self._auth_headers(token),
                )
            except httpx.RequestError as exc:
                raise ZetarisError(
                    f"Cannot reach {self.base_url}: {exc}\n"
                    "Check VPN / URL. ZETARIS_BASE_URL is UI origin only."
                ) from exc
            if resp.status_code >= 400:
                self._raise_http("GET", path, resp)
            databases = resp.json()
        count = len(databases) if isinstance(databases, list) else "unknown"
        return {"ok": True, "mode": "proxy", "lightning_databases": count, "raw_type": type(databases).__name__}

    def _proxy_run_sql(self, sql: str) -> QueryResult:
        path = "/api/proxy/sql-editor/sqls/run-query"
        body: dict[str, Any] = {"sql": sql, "limit": self.page_limit}
        if self.engine_id:
            body["engineId"] = self.engine_id
        with httpx.Client(timeout=30.0) as client:
            token = self._resolve_token(client)
            try:
                resp = client.post(
                    f"{self.base_url}{path}",
                    headers=self._auth_headers(token),
                    json=body,
                )
            except httpx.RequestError as exc:
                raise ZetarisError(
                    f"Cannot reach {self.base_url}: {exc}\n"
                    "Check ZETARIS_BASE_URL and network."
                ) from exc
            if resp.status_code >= 400:
                self._raise_http("POST", path, resp)
            payload = resp.json()
        rows = _extract_rows(payload)
        return QueryResult(
            sql=sql,
            rows=rows,
            source="zetaris-proxy",
            meta={"path": path, "raw_keys": list(payload.keys()) if isinstance(payload, dict) else []},
        )

    def _direct_open_sql(self, sql: str) -> QueryResult:
        if not self.api_key:
            raise ZetarisError(
                "Direct REST channel requires ZETARIS_API_KEY "
                "(username/password login is UI-proxy only)."
            )
        # KB OpenSqlQuery style; path can differ — prefer proxy channel when unsure.
        path = "/dbquery/open"
        url = f"{self.rest_url}{path}"
        payload = {"select": sql, "pageLimit": min(self.page_limit, 100)}
        with httpx.Client(timeout=30.0) as client:
            try:
                resp = client.post(url, headers=self._auth_headers(self.api_key), json=payload)
            except httpx.RequestError as exc:
                raise ZetarisError(
                    f"Cannot reach {self.rest_url}: {exc}\n"
                    "Prefer ZETARIS_CHANNEL=proxy with ZETARIS_BASE_URL from the hackathon instance."
                ) from exc
            if resp.status_code >= 400:
                self._raise_http("POST", url, resp)
            body = resp.json()
        rows = _extract_rows(body)
        return QueryResult(
            sql=sql,
            rows=rows,
            source="zetaris-direct",
            meta={"queryToken": body.get("queryToken") if isinstance(body, dict) else None},
        )

    def _mock_crash_density(self) -> list[dict[str, Any]]:
        collisions = all_tables()["collisions"]
        agg: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"zone_id": "", "crashes": 0, "injured": 0, "fatal": 0}
        )
        for row in collisions:
            z = row["zone_id"]
            bucket = agg[z]
            bucket["zone_id"] = z
            bucket["crashes"] += 1
            bucket["injured"] += int(row.get("injured") or 0)
            bucket["fatal"] += int(row.get("fatal") or 0)
        return sorted(agg.values(), key=lambda r: r["crashes"], reverse=True)

    def _mock_sql(self, sql: str) -> QueryResult:
        upper = sql.upper()
        if "COLLISION" in upper or "CRASH" in upper:
            return QueryResult(sql=sql, rows=self._mock_crash_density(), source="mock")
        if "COMPANY" in upper:
            return QueryResult(sql=sql, rows=all_tables()["companies"], source="mock")
        if "ZONE" in upper or "TAXI" in upper:
            return QueryResult(sql=sql, rows=all_tables()["zones"], source="mock")
        if "SELECT 1" in upper.replace(" ", ""):
            return QueryResult(sql=sql, rows=[{"1": 1}], source="mock")
        return QueryResult(sql=sql, rows=[], source="mock", meta={"note": "no mock handler"})


def _extract_rows(payload: Any) -> list[dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("data", "rows", "result", "results", "records"):
        val = payload.get(key)
        if isinstance(val, list):
            return [r if isinstance(r, dict) else {"value": r} for r in val]
        if isinstance(val, dict):
            nested = val.get("rows") or val.get("data")
            if isinstance(nested, list):
                return [r if isinstance(r, dict) else {"value": r} for r in nested]
    # Some UI proxy responses wrap columns/values separately — leave empty with honesty.
    return []
