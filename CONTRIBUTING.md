# Contributing to BEKAL

Thanks for taking an interest in BEKAL.

BEKAL is a local-first receipt-intelligence project with a deliberately narrow privacy boundary. Contributions are welcome when they strengthen the accepted product path without weakening data safety or silently expanding scope.

## Before contributing

Read:

1. [README](README.md)
2. [Documentation index](docs/README.md)
3. [Architecture](docs/architecture.md)
4. [Development guide](docs/development.md)
5. [Privacy & Security](docs/privacy-security.md)
6. [Roadmap](docs/roadmap.md)

Coding agents should also read [`AGENTS.md`](AGENTS.md).

## Contribution principles

- Keep changes scoped and reviewable.
- Prefer straightforward, maintainable solutions over unnecessary architecture.
- Preserve the local-first privacy model.
- Use synthetic data in tests/examples.
- Do not fabricate receipt data when extraction is uncertain.
- Keep the original receipt PDF as the source of truth.
- Do not expose the current unauthenticated backend beyond its supported local boundary.
- Treat persistent-data and migration changes as architecture-sensitive work.

## Privacy rules

Never include in a commit, issue, PR, screenshot, log, or test fixture:

- real receipt PDFs/images;
- private CSV exports;
- database files/dumps containing user data;
- generated local `.env` files;
- passwords, access tokens, API keys, or credentials;
- private logs containing receipt content.

Only synthetic/public-safe data belongs in the repository.

Before submitting a change, run:

```powershell
python scripts/check_repository_safety.py --history
```

`.env.example` is an intentionally public template and is allowed.

## Development setup

See [Development](docs/development.md).

The normal browser/Docker flow starts with:

```powershell
Copy-Item .env.example .env
# Set a local PostgreSQL password in .env
docker compose up --build -d
docker compose exec backend alembic upgrade head
```

Frontend work uses `npm ci` / `npm run build` in `frontend/`.

Desktop work additionally requires the Rust/Tauri Windows toolchain.

## Tests and checks

Run the checks appropriate to your change.

Typical gates include:

- backend pytest suite;
- frontend production build;
- npm audit;
- repository safety/history scan;
- Rust format/check/audit for desktop changes;
- Windows installer build/verification for packaging changes.

Do not weaken or bypass a test/privacy gate simply to make CI green.

## Pull requests

A good PR should explain:

- the problem being solved;
- the exact scope of the change;
- explicit non-goals if scope could be misunderstood;
- user-visible behavior changes;
- data/privacy impact;
- tests/checks performed;
- migration or upgrade impact, if any.

Keep unrelated refactors out of a focused bug/feature PR unless they are required for the change.

## Product scope

The current released milestone is V0.2. New areas such as mobile clients, cloud sync, authentication, multi-user accounts, pantry/recipe features, or replacing Docker/PostgreSQL are not routine maintenance tasks.

If a contribution would introduce one of those boundaries, start with an architecture/scope discussion rather than presenting it as a small implementation detail.

See [Roadmap](docs/roadmap.md).

## Documentation

Update current documentation when behavior changes.

Use `docs/archive/` only for historical milestone records. Do not create a new root-level draft document when an existing current document can be updated.

## Commit style

Use clear, scoped commit messages, for example:

```text
fix: preserve candidate after database failure
test: cover duplicate receipt override
docs: clarify Windows installation flow
chore: update audited dependency
```

## License

By contributing to this repository, you agree that your contribution is provided under the repository's [MIT License](LICENSE).
