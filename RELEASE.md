# Release checklist

## 0.1.0

1. Update `CHANGELOG.md` and confirm the version in `pyproject.toml` and `src/picshelf/__init__.py`.
2. Run local checks:

   ```bash
   PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests
   node --check src/picshelf/static/app.js
   docker compose config
   docker build -t picshelf:local .
   ```

3. Create a GitHub repository and push the project root as the repository root.
4. Confirm the GitHub Actions workflow passes.
5. Create tag `v0.1.0`.
6. Publish the first GitHub release using the `CHANGELOG.md` entry.

Optional image publishing target:

```text
ghcr.io/<github-user-or-org>/picshelf:0.1.0
ghcr.io/<github-user-or-org>/picshelf:latest
```
