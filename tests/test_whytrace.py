"""Minimal tests — mock only; never call live APIs."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

os.environ["USE_MOCK"] = "1"
os.environ["SYNTHESIS_PROVIDER"] = "mock"


class WhyTraceMockTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        os.environ["METERLESS_STORE_DIR"] = self._tmpdir.name
        os.environ["USE_MOCK"] = "1"
        from whytrace.agent import WhyTraceAgent
        from whytrace.demo_questions import DEMO_QUESTIONS, get_demo
        from whytrace.zetaris_client import ZetarisClient

        self.WhyTraceAgent = WhyTraceAgent
        self.DEMO_QUESTIONS = DEMO_QUESTIONS
        self.get_demo = get_demo
        self.ZetarisClient = ZetarisClient

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_status_mock(self) -> None:
        agent = self.WhyTraceAgent()
        st = agent.status()
        self.assertEqual(st["zetaris"]["mode"], "mock")
        self.assertIn("python-hmem", st["meterless"]["mode"])

    def test_ping_mock(self) -> None:
        agent = self.WhyTraceAgent()
        p = agent.ping()
        self.assertTrue(p["zetaris"]["ok"])

    def test_ask_demo_1_has_citations(self) -> None:
        agent = self.WhyTraceAgent()
        q = self.get_demo("1")["question"]
        result = agent.ask(q)
        self.assertGreaterEqual(len(result["findings"]), 3)
        self.assertTrue(result["citation_ids"])
        self.assertIn("ev-", result["answer"])
        self.assertNotEqual(result.get("warning"), "zetaris_error")

    def test_audit_after_ask(self) -> None:
        agent = self.WhyTraceAgent()
        agent.ask(self.get_demo("1")["question"])
        events = agent.audit(limit=50)
        self.assertTrue(any(e["action"] == "write" for e in events))

    def test_live_unconfigured_errors_clearly(self) -> None:
        os.environ["USE_MOCK"] = "0"
        os.environ.pop("ZETARIS_API_KEY", None)
        os.environ.pop("ZETARIS_ORG_ID", None)
        os.environ.pop("ZETARIS_USERNAME", None)
        os.environ.pop("ZETARIS_PASSWORD", None)
        client = self.ZetarisClient()
        from whytrace.zetaris_client import ZetarisError

        with self.assertRaises(ZetarisError) as ctx:
            client.execute_sql("SELECT 1")
        msg = str(ctx.exception)
        self.assertIn("ZETARIS_ORG_ID", msg)
        self.assertIn("USE_MOCK=1", msg)
        os.environ["USE_MOCK"] = "1"

    def test_demo_catalog_ids(self) -> None:
        ids = {d["id"] for d in self.DEMO_QUESTIONS}
        self.assertEqual(ids, {"1", "2", "3", "4"})


if __name__ == "__main__":
    unittest.main()
