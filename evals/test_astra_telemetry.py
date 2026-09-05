import json
import tempfile
import unittest
from pathlib import Path

from astra_telemetry import aggregate_final_usage, read_usage


class TelemetryTests(unittest.TestCase):
    def test_cached_and_reasoning_are_subsets_not_extra_tokens(self):
        actor = {"id": "root", "total_token_usage": {"input_tokens": 100, "cached_input_tokens": 80, "output_tokens": 20, "reasoning_output_tokens": 15}}
        self.assertEqual(aggregate_final_usage([actor], {"root"})["total"], 120)
        self.assertIsNone(aggregate_final_usage([actor, actor], {"root"})["total"])
        self.assertIsNone(aggregate_final_usage([actor], {"root", "missing"})["total"])

    def test_recursive_identity_and_final_cumulative_usage(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for actor_id, parent, spawn in (("root", None, True), ("child", "root", True), ("grandchild", "child", False), ("unrelated", None, False)):
                source = {"subagent": {"thread_spawn": {"parent_thread_id": parent}}} if parent else "exec"
                rows = [
                    {"type": "session_meta", "payload": {"id": actor_id, "source": source, "other": "root"}},
                    {"type": "turn_context", "payload": {"model": "gpt-6-astra", "effort": "medium"}},
                    {"type": "event_msg", "payload": {"type": "task_started", "turn_id": "t"}},
                ]
                if spawn:
                    rows += [
                        {"type": "response_item", "payload": {"type": "function_call", "name": "spawn_agent", "call_id": "c"}},
                        {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "c", "output": '{"task_name":"/root/child"}'}},
                    ]
                for count in (5, 10):
                    rows.append({"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": count, "output_tokens": 2, "cached_input_tokens": 3}}}})
                rows.append({"type": "event_msg", "payload": {"type": "task_complete", "turn_id": "t"}})
                (root / (actor_id + ".jsonl")).write_text("\n".join(json.dumps(row) for row in rows))
            result = read_usage("root", root)
            self.assertEqual(result["coverage"], "complete")
            self.assertEqual(result["total"], 36)
            self.assertEqual(result["cached_input_tokens"], 9)
            self.assertEqual({actor["id"] for actor in result["actors"]}, {"root", "child", "grandchild"})
            (root / "grandchild.jsonl").unlink()
            self.assertIsNone(read_usage("root", root)["total"])


if __name__ == "__main__":
    unittest.main()
