# Contributing to pypemesh

Thanks for your interest. pypemesh is pre-alpha and moves fast; please
read this before opening a PR.

## Ground rules

- **Read `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, `docs/UX_PRINCIPLES.md` first.** Changes that conflict with these docs need the doc updated first.
- **Every solver change needs a test.** No exceptions. If you change an equation, add a unit test against a textbook value.
- **Every UI change is measured against `UX_PRINCIPLES.md`.** PRs that violate the 12 laws get revised, not merged.
- **CLA required.** First PR triggers a Contributor License Agreement bot. You retain copyright; we retain the right to relicense.

## Development setup

```bash
# Python core
cd pypemesh-core
pip install -e ".[dev]"
pytest

# Frontend
cd ../pypemesh-web/frontend
npm install
npm run dev

# Backend
cd ../backend
pip install -e ".[dev]"
uvicorn app.main:app --reload

# Full stack with Postgres + Redis
docker-compose up
```

## Commit style

[Conventional Commits](https://www.conventionalcommits.org/). Examples:
- `feat(solver): add elbow Karman flexibility factor`
- `fix(b31_3): correct SIF for reducing tee`
- `docs(architecture): clarify plugin registration`
- `test(validation): add Peng Ch 5 ex 5.3 benchmark`
- `perf(assembly): use CSR directly, skip COO intermediate`

## PR checklist

- [ ] Linked to an issue (or created one if substantial)
- [ ] Tests added or updated
- [ ] `ruff`, `mypy`, `prettier`, `eslint` all pass locally
- [ ] Benchmark suite hasn't regressed (CI will check)
- [ ] Docs updated if behavior changed
- [ ] Entry added to `CHANGELOG.md`

## What gets accepted

- Bug fixes with a failing test
- Validation cases (more benchmarks = better)
- UX improvements that align with `UX_PRINCIPLES.md`
- Documentation improvements
- New codes — coordinate first via issue; these are large changes

## What gets rejected

- PRs that drop solver accuracy
- PRs that add modal dialogs for routine workflow (see UX law #3)
- PRs without tests
- PRs that introduce copyrighted data (ASME Section II Part D, etc.)
- "Clean up this file" PRs that mix refactor + behavior change
