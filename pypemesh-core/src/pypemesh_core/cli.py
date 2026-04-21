"""pypemesh command-line interface.

Usage:
    pypemesh solve <project.json>          — run solver + B31.3, print summary
    pypemesh validate <project.json>       — parse-and-validate without solving
    pypemesh report <project.json> [-o out.pdf]  — generate PDF report
    pypemesh bench [<benchmarks_dir>]      — run benchmark suite
    pypemesh version                       — print version

For machine-readable output, use --json with `solve`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pypemesh_core import __version__
from pypemesh_core.codes.b31_1 import B31_1
from pypemesh_core.codes.b31_3 import B31_3
from pypemesh_core.codes.b31_4 import B31_4
from pypemesh_core.codes.b31_5 import B31_5
from pypemesh_core.codes.b31_8 import B31_8
from pypemesh_core.codes.b31_9 import B31_9
from pypemesh_core.codes.b31_12 import B31_12
from pypemesh_core.codes.csa_z662 import CSA_Z662
from pypemesh_core.codes.en_13480 import EN_13480
from pypemesh_core.io.pcf import load_pcf
from pypemesh_core.io.project import load_project, save_project
from pypemesh_core.io.report_pdf import generate_pdf_report
from pypemesh_core.solver.combinations import evaluate_combinations
from pypemesh_core.validation.harness import run_all_benchmarks


CODE_REGISTRY = {
    "B31.3": B31_3, "B31.1": B31_1, "B31.4": B31_4, "B31.5": B31_5,
    "B31.8": B31_8, "B31.9": B31_9, "B31.12": B31_12,
    "CSA-Z662": CSA_Z662, "EN-13480": EN_13480,
}


def _cmd_solve(args: argparse.Namespace) -> int:
    project = load_project(args.project)
    combos = evaluate_combinations(project, T_eval=args.temperature)
    code = args.code if args.code in CODE_REGISTRY else "B31.3"
    code_results = CODE_REGISTRY[code](T_evaluation=args.temperature).evaluate(
        project, combinations=combos,
    )

    if args.json:
        out = {
            "project_name": project.name,
            "results": [
                {
                    "element_id": r.element_id,
                    "combination_id": r.combination_id,
                    "stress_pa": r.stress,
                    "allowable_pa": r.allowable,
                    "ratio": r.ratio,
                    "status": r.status,
                    "equation": r.equation_used,
                }
                for r in code_results
            ],
        }
        print(json.dumps(out, indent=2))
        return 0

    failed = sum(1 for r in code_results if r.status == "fail")
    max_ratio = max((r.ratio for r in code_results), default=0.0)
    overall = "FAIL" if failed else "PASS"

    print(f"\n  pypemesh — ASME B31.3 Stress Analysis")
    print(f"  ─────────────────────────────────────")
    print(f"  Project   : {project.name}")
    print(f"  Code      : {project.code} {project.code_version}")
    print(f"  Nodes     : {len(project.nodes)}   Elements : {len(project.elements)}")
    print(f"  Combos    : {len(project.load_combinations)}   Checks   : {len(code_results)}")
    print(f"  Max ratio : {max_ratio:.3f}")
    print(f"  Status    : {overall}\n")

    if code_results:
        print(f"  {'Element':<8} {'Combo':<10} {'Eq':<5} {'Stress (MPa)':>14} "
              f"{'Allow (MPa)':>14} {'Ratio':>8} {'Status':>7}")
        print(f"  {'-'*8} {'-'*10} {'-'*5} {'-'*14} {'-'*14} {'-'*8} {'-'*7}")
        for r in code_results:
            print(f"  {r.element_id:<8} {r.combination_id:<10} {r.equation_used:<5} "
                  f"{r.stress/1e6:>14.2f} {r.allowable/1e6:>14.2f} "
                  f"{r.ratio:>8.3f} {r.status.upper():>7}")
        print()

    return 1 if failed else 0


def _cmd_validate(args: argparse.Namespace) -> int:
    project = load_project(args.project)
    print(f"OK: {project.name} ({len(project.nodes)} nodes, "
          f"{len(project.elements)} elements, "
          f"{len(project.load_combinations)} combinations)")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    project = load_project(args.project)
    combos = evaluate_combinations(project, T_eval=args.temperature)
    code_results = B31_3(T_evaluation=args.temperature).evaluate(project, combinations=combos)
    out_path = args.output or f"{project.name.replace(' ', '_')}_b31_3_report.pdf"
    generate_pdf_report(
        project, code_results, combinations=combos,
        output_path=out_path, company=args.company, engineer=args.engineer,
    )
    print(f"Wrote: {out_path}")
    return 0


def _cmd_bench(args: argparse.Namespace) -> int:
    bench_dir = args.benchmarks_dir or Path(__file__).resolve().parents[3] / "benchmarks"
    bench_dir = Path(bench_dir)
    if not bench_dir.exists():
        print(f"No benchmarks dir at {bench_dir}", file=sys.stderr)
        return 1
    results = run_all_benchmarks(bench_dir)
    failed = 0
    print(f"\n  pypemesh benchmark suite ({len(results)} cases)")
    print(f"  ─────────────────────────────────────")
    for r in results:
        marker = "✓" if r.passed else "✗"
        print(f"  {marker} {r.name:<40} ({r.summary['n_failures']} failures)")
        if not r.passed:
            failed += 1
            for f in r.failures:
                print(f"      {f}")
    print(f"\n  Result: {len(results) - failed}/{len(results)} passed\n")
    return 0 if failed == 0 else 1


def _cmd_version(_args: argparse.Namespace) -> int:
    print(f"pypemesh-core {__version__}")
    return 0


def _cmd_import_pcf(args: argparse.Namespace) -> int:
    project = load_pcf(args.pcf_file)
    output = args.output or f"{Path(args.pcf_file).stem}.json"
    save_project(project, output)
    print(f"Imported {args.pcf_file} → {output}")
    print(f"  {len(project.nodes)} nodes, {len(project.elements)} elements")
    return 0


def _cmd_materials(_args: argparse.Namespace) -> int:
    from pypemesh_core.materials.library import list_materials
    items = list_materials()
    print(f"\n  pypemesh — curated material library ({len(items)} materials)")
    print(f"  {'ID':<20} Name")
    print(f"  {'-' * 20} {'-' * 60}")
    for mid, name in items:
        print(f"  {mid:<20} {name}")
    print()
    return 0


def _cmd_codes(_args: argparse.Namespace) -> int:
    print(f"\n  pypemesh — supported codes ({len(CODE_REGISTRY)} codes)")
    for code_id, cls in CODE_REGISTRY.items():
        ver = getattr(cls, "version", "?")
        print(f"  {code_id:<15} ({ver})")
    print()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pypemesh",
        description="Open-source pipe stress analysis (ASME B31.3 today; more codes on the roadmap).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_solve = sub.add_parser("solve", help="Solve a project and print stress results")
    p_solve.add_argument("project", help="Path to project JSON file")
    p_solve.add_argument("--code", default="B31.3",
                         choices=list(CODE_REGISTRY.keys()),
                         help="Code to check against")
    p_solve.add_argument("--temperature", type=float, default=293.15, help="Evaluation temperature [K]")
    p_solve.add_argument("--json", action="store_true", help="Output as JSON")
    p_solve.set_defaults(func=_cmd_solve)

    p_val = sub.add_parser("validate", help="Validate a project JSON without solving")
    p_val.add_argument("project")
    p_val.set_defaults(func=_cmd_validate)

    p_rep = sub.add_parser("report", help="Generate a PDF stress report")
    p_rep.add_argument("project")
    p_rep.add_argument("-o", "--output", help="Output PDF path")
    p_rep.add_argument("--company", default="")
    p_rep.add_argument("--engineer", default="")
    p_rep.add_argument("--temperature", type=float, default=293.15)
    p_rep.set_defaults(func=_cmd_report)

    p_bench = sub.add_parser("bench", help="Run benchmark suite")
    p_bench.add_argument("benchmarks_dir", nargs="?", help="Path to benchmarks dir")
    p_bench.set_defaults(func=_cmd_bench)

    p_ver = sub.add_parser("version", help="Print version")
    p_ver.set_defaults(func=_cmd_version)

    p_pcf = sub.add_parser("import-pcf",
                           help="Import a PCF (Piping Component File) and write project JSON")
    p_pcf.add_argument("pcf_file", help="Path to .pcf file")
    p_pcf.add_argument("-o", "--output", help="Output project JSON path (default: <pcf_stem>.json)")
    p_pcf.set_defaults(func=_cmd_import_pcf)

    p_mat = sub.add_parser("materials", help="List curated materials in the library")
    p_mat.set_defaults(func=_cmd_materials)

    p_cod = sub.add_parser("codes", help="List supported compliance codes")
    p_cod.set_defaults(func=_cmd_codes)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
