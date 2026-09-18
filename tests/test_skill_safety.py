import ast
import json
import os
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


class SkillSafetyTests(unittest.TestCase):
    def run_script(self, skill, script, *args):
        return subprocess.run(
            [sys.executable, "-B", str(SKILLS / skill / "scripts" / script), *args],
            cwd=ROOT,
            env={**os.environ, "NO_PROXY": "127.0.0.1", "no_proxy": "127.0.0.1"},
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_personal_skills_require_explicit_invocation(self):
        entries = list(SKILLS.glob("*/SKILL.md"))
        self.assertTrue(entries)
        for entry in entries:
            with self.subTest(skill=entry.parent.name):
                metadata = yaml.safe_load(
                    (entry.parent / "agents" / "openai.yaml").read_text()
                )
                self.assertIs(metadata["policy"]["allow_implicit_invocation"], False)

    def test_python_sources_parse(self):
        for path in SKILLS.rglob("*.py"):
            with self.subTest(path=path.relative_to(ROOT)):
                ast.parse(path.read_text(), filename=str(path))

    def test_shell_sources_parse(self):
        for path in SKILLS.rglob("*.sh"):
            with self.subTest(path=path.relative_to(ROOT)):
                result = subprocess.run(
                    ["bash", "-n", str(path)], capture_output=True, text=True, timeout=10
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_pool_services_select_real_deployments(self):
        manifests = SKILLS / "pp-separation-benchmark" / "manifests"
        for directory in (manifests, manifests / "examples-verified"):
            with self.subTest(directory=directory.relative_to(ROOT)):
                services = list(yaml.safe_load_all((directory / "services.yaml").read_text()))
                deployments = [
                    document
                    for document in yaml.safe_load_all((directory / "vllm-pools.yaml").read_text())
                    if document and document["kind"] == "Deployment"
                ]
                self.assertEqual({item["metadata"]["name"] for item in services}, {"hot-svc", "cold-svc"})
                for service in services:
                    self.assertEqual(service["kind"], "Service")
                    selector = service["spec"]["selector"]
                    matching = [
                        deployment for deployment in deployments
                        if all(
                            deployment["spec"]["template"]["metadata"]["labels"].get(key) == value
                            for key, value in selector.items()
                        )
                    ]
                    self.assertEqual(len(matching), 1)
                    ports = {
                        port["containerPort"]
                        for container in matching[0]["spec"]["template"]["spec"]["containers"]
                        for port in container.get("ports", [])
                    }
                    self.assertIn(service["spec"]["ports"][0]["targetPort"], ports)

    def test_round_analysis_rejects_non_json_input(self):
        result = self.run_script(
            "model-perf-binary-search", "analyze_rounds.py",
            "--json", str(ROOT / "README.md"), "--total-rounds", "1", "--tail-window", "1",
        )
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "ERROR")

    def test_probe_rejects_zero_requests(self):
        result = self.run_script(
            "llm-torch-profiler-analysis", "probe_llm_server.py",
            "--framework", "sglang", "--url", "http://127.0.0.1:1", "--requests", "0",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--requests must be positive", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_probe_connection_failure_is_not_success(self):
        # Binding without listening produces a real connection-refused failure.
        with socket.socket() as endpoint:
            endpoint.bind(("127.0.0.1", 0))
            port = endpoint.getsockname()[1]
            result = self.run_script(
                "llm-torch-profiler-analysis", "probe_llm_server.py",
                "--framework", "sglang", "--url", f"http://127.0.0.1:{port}",
                "--requests", "1", "--timeout", "1",
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("URLError", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_host_analysis_requires_real_input(self):
        result = self.run_script("perf-host-analysis", "analyze_host_overhead.py", "--mock")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_latency_labels_identify_the_statistic(self):
        namespace = runpy.run_path(str(SKILLS / "llm-serving-auto-benchmark" / "scripts" / "compare_benchmark_results.py"))
        format_metric = namespace["_p50_or_mean_value"]
        self.assertEqual(format_metric({"metrics": {"p50_ttft_ms": 1.5}}, "ttft"), "1.50 (P50)")
        self.assertEqual(format_metric({"metrics": {"mean_ttft_ms": 1.5}}, "ttft"), "1.50 (mean)")
        self.assertIsNone(format_metric({"metrics": {}}, "ttft"))
        with self.assertRaises(ValueError):
            namespace["_float"]({"metrics": {"request_throughput": "invalid"}}, "metrics.request_throughput")


if __name__ == "__main__":
    unittest.main()
