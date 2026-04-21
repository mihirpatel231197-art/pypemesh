"""Vercel Python serverless function: POST /api/solve

Accepts the same payload as the full FastAPI /solve endpoint and returns
the same response shape. Lightweight — no modal / report endpoints (those
are too heavy for serverless). For full capability, run the FastAPI
backend locally (see USAGE.md).
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Bundled pypemesh_core sits next to this file
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pypemesh_core.codes.b31_1 import B31_1
from pypemesh_core.codes.b31_3 import B31_3
from pypemesh_core.codes.b31_4 import B31_4
from pypemesh_core.codes.b31_5 import B31_5
from pypemesh_core.codes.b31_8 import B31_8
from pypemesh_core.codes.b31_9 import B31_9
from pypemesh_core.codes.b31_12 import B31_12
from pypemesh_core.codes.csa_z662 import CSA_Z662
from pypemesh_core.codes.en_13480 import EN_13480
from pypemesh_core.io.project import project_from_dict
from pypemesh_core.solver.combinations import evaluate_combinations


CODE_REGISTRY = {
    "B31.3": B31_3, "B31.1": B31_1, "B31.4": B31_4, "B31.5": B31_5,
    "B31.8": B31_8, "B31.9": B31_9, "B31.12": B31_12,
    "CSA-Z662": CSA_Z662, "EN-13480": EN_13480,
}


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"

        try:
            req = json.loads(body)
        except Exception as e:
            return self._error(400, f"Invalid JSON: {e}")

        try:
            project = project_from_dict(req["project"])
        except Exception as e:
            return self._error(400, f"Invalid project: {e}")

        code = req.get("code", "B31.3")
        if code not in CODE_REGISTRY:
            return self._error(400, f"Unsupported code: {code}")

        T_eval = req.get("T_evaluation", 293.15)

        try:
            combos = evaluate_combinations(project, T_eval=T_eval)
            checker = CODE_REGISTRY[code](T_evaluation=T_eval)
            results = checker.evaluate(project, combinations=combos)
        except Exception as e:
            return self._error(500, f"Solver error: {e}")

        serialized = [
            {
                "element_id": r.element_id,
                "combination_id": r.combination_id,
                "stress_pa": r.stress,
                "allowable_pa": r.allowable,
                "ratio": r.ratio,
                "status": r.status,
                "equation": r.equation_used,
            }
            for r in results
        ]

        failed = [r for r in results if r.status == "fail"]
        max_ratio = max((r.ratio for r in results), default=0.0)

        response = {
            "status": "ok",
            "project_name": project.name,
            "n_nodes": len(project.nodes),
            "n_elements": len(project.elements),
            "n_load_cases": len(project.load_cases),
            "n_combinations": len(project.load_combinations),
            "code": code,
            "results": serialized,
            "summary": {
                "total_checks": len(results),
                "failed": len(failed),
                "max_ratio": max_ratio,
                "overall_status": "fail" if failed else "pass",
            },
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _error(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode("utf-8"))
