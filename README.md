# Recipe API

This repository contains the Recipe API: a small Flask application that
parses recipe data from a JSON file, stores it in a SQL database, and
exposes REST endpoints for listing and searching recipes.

Quick links

- Code: root of repo
- App module: `recipe_app/` (contains app, models, data parser, and templates)
- Tests: `recipe_app/tests/`
- Migrations: `migrations/`

Quickstart (SQLite local)

1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate    # Bash on Windows or macOS/Linux
# On Windows CMD: .venv\Scripts\activate
```

2. Install dependencies

```bash
pip install -r recipe_app/requirements.txt
```

3. Run the app (this will create and seed `recipes.db` if empty):

```bash
python -m recipe_app.app
```

4. Open the UI or call the API

```bash
http://127.0.0.1:5000/
curl "http://127.0.0.1:5000/api/recipes?page=1&limit=10"
```

Postgres (optional, local via Docker Compose)

1. Start Postgres with Docker Compose

```bash
docker compose up -d
```

2. Set `DATABASE_URL` in `.env` to something like:

```
DATABASE_URL=postgresql://recipes_user:secret@localhost:5432/recipes_db
```

3. Apply migrations and run the app

```bash
pip install -r recipe_app/requirements.txt
flask --app recipe_app.manage db upgrade
python -m recipe_app.app
```

Testing

```bash
python -m pytest
```

CI

This repo includes a GitHub Actions workflow that runs tests and builds a
Docker image to run tests inside the container. See `.github/workflows/python-tests.yml`.

Notes

- Keep secrets out of the repository. Use `.env.example` as a template and add `.env` to `.gitignore`.
- If you plan to deploy, consider using PostgreSQL (set `DATABASE_URL`) and adding JSONB indexes for nutrient queries.

Contributions

See `CONTRIBUTING.md` for guidelines.
