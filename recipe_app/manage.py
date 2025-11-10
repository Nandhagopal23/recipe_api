"""Manage script to expose the Flask app for the Flask CLI (migrations etc.).

Usage (from the project root):
  set FLASK_APP=recipe_app.manage   # Windows (PowerShell: $Env:FLASK_APP = 'recipe_app.manage')
  flask db init
  flask db migrate -m "Initial"
  flask db upgrade

This file simply exposes the `app` object at import-time so `flask` can find
it when FLASK_APP points to `recipe_app.manage`.
"""

from recipe_app.app import app

if __name__ == '__main__':
    app.run(debug=True)
