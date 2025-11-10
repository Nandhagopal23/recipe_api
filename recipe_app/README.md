# Recipe API

This project parses a recipes JSON file, stores recipes in a database, and exposes a REST API to list and search recipes.

Features

- Parse provided `recipes.json` and normalize numeric fields (NaN -> NULL)
- Store recipes in a SQL database (SQLite by default; Postgres supported)
- REST APIs:
  - `GET /api/recipes` — paginated, sorted by rating (query: `page`, `limit`)
  - `GET /api/recipes/search` — search by `title`, `cuisine`, `rating`, `total_time`, and `calories`
- Basic frontend under `templates/` and `static/` that lists recipes and shows details
- Migrations with Flask-Migrate (migrations/ folder)

Quickstart (SQLite, local)

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/Scripts/activate    # or .venv\Scripts\activate on Windows cmd
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app (this will create `recipes.db` and seed recipes if the table is empty):

```bash
# from project root
python -m recipe_app.app
```

4. Open http://127.0.0.1:5000/ or call the API:

```bash
curl "http://127.0.0.1:5000/api/recipes?page=1&limit=10"
```

Postgres (optional)

- Use `docker compose up -d` to start Postgres defined in `docker-compose.yml`.
- Set `DATABASE_URL` in `.env` (or environment) to `postgresql://recipes_user:secret@localhost:5432/recipes_db`.
- Install requirements, run migrations, and run the app:

```bash
pip install -r requirements.txt
flask --app recipe_app.manage db upgrade
python -m recipe_app.app
```

Running tests

```bash
#.venv active
python -m pytest
```

Notes

- Keep secrets out of the repo — do not commit `.env`. Use `.env.example` as a template.
- Tests set `DATABASE_URL` empty to ensure they run against a temporary SQLite database.

License: MIT (choose your preferred license)
