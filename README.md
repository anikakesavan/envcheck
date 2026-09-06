# envcheck

**Try it in your browser, no install: https://anikakesavan.github.io/envcheck/**
(paste both files in, see the diff instantly — nothing is uploaded).

A tiny, dependency-free CLI that compares your `.env` against your
`.env.example` and tells you exactly what's missing, empty, or stale —
before your app crashes on a `KeyError` in production.

## Install

```bash
pip install .
```

Or run it straight from the repo:

```bash
python -m envcheck.cli
```

## Usage

```bash
envcheck                                    # checks .env against .env.example
envcheck --env .env.production --example .env.example
envcheck --init                             # fills in missing keys with example defaults
```

Example output:

```
Missing from .env (2):
  DATABASE_URL
  STRIPE_SECRET_KEY
Empty in .env (1):
  API_TIMEOUT
Extra in .env, not in .env.example (1):
  OLD_FEATURE_FLAG
```

Exits `0` when everything required is present and non-empty, `1` otherwise —
so it's a natural fit for a pre-commit hook, a `Makefile` target, or a CI
step that runs before your test suite.

`--init` never overwrites a value you've already set; it only appends keys
from `.env.example` that your `.env` doesn't have yet, copying over the
example's default.

## Development

Run the test suite (pure standard library, no dependencies needed):

```bash
python -m unittest discover -v
```

## License

MIT — see [LICENSE](LICENSE).
