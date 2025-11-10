import os
import pytest

# Ensure tests don't accidentally connect to an external Postgres instance
# If a .env file exists it may set DATABASE_URL via load_dotenv() when
# importing app/config. To prevent that, set DATABASE_URL to an empty
# string here so load_dotenv() will not override it (load_dotenv does not
# overwrite existing env vars by default).
os.environ['DATABASE_URL'] = ''

from recipe_app.app import app
from recipe_app.models import db, Recipe


@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Use the existing app context and a temporary SQLite DB file
    app.config['TESTING'] = True
    # Use a temporary sqlite file to avoid interfering with real DB
    test_db = 'sqlite:///test_recipes.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = test_db

    with app.app_context():
        db.drop_all()
        db.create_all()
        # seed two recipes
        r1 = Recipe(title='Sweet Potato Pie', cuisine='Southern Recipes', rating=4.8,
                    prep_time=15, cook_time=100, total_time=115,
                    description='A pie', nutrients={'calories': '389 kcal'}, serves='8')
        r2 = Recipe(title='Apple Pie', cuisine='American', rating=4.2,
                    prep_time=10, cook_time=50, total_time=60,
                    description='Apple pie', nutrients={'calories': '450 kcal'}, serves='6')
        db.session.add_all([r1, r2])
        db.session.commit()

    yield

    # teardown
    import os
    import pytest

    # Ensure tests don't accidentally connect to an external Postgres instance
    # if DATABASE_URL is set in the environment. Clear it before importing app.
    os.environ.pop('DATABASE_URL', None)

    from recipe_app.app import app
    from recipe_app.models import db, Recipe


    @pytest.fixture(autouse=True)
    def setup_and_teardown():
        # Use the existing app context and a temporary SQLite DB file
        app.config['TESTING'] = True
        # Use a temporary sqlite file to avoid interfering with real DB
        test_db = 'sqlite:///test_recipes.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = test_db

        with app.app_context():
            db.drop_all()
            db.create_all()
            # seed two recipes
            r1 = Recipe(title='Sweet Potato Pie', cuisine='Southern Recipes', rating=4.8,
                        prep_time=15, cook_time=100, total_time=115,
                        description='A pie', nutrients={'calories': '389 kcal'}, serves='8')
            r2 = Recipe(title='Apple Pie', cuisine='American', rating=4.2,
                        prep_time=10, cook_time=50, total_time=60,
                        description='Apple pie', nutrients={'calories': '450 kcal'}, serves='6')
            db.session.add_all([r1, r2])
            db.session.commit()

        yield
import os
import pytest

# Ensure tests don't accidentally connect to an external Postgres instance
# if DATABASE_URL is set in the environment. Clear it before importing app.
os.environ.pop('DATABASE_URL', None)

from recipe_app.app import app
from recipe_app.models import db, Recipe


@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Use the existing app context and a temporary SQLite DB file
    app.config['TESTING'] = True
    # Use a temporary sqlite file to avoid interfering with real DB
    test_db = 'sqlite:///test_recipes.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = test_db

    with app.app_context():
        db.drop_all()
        db.create_all()
        # seed two recipes
        r1 = Recipe(title='Sweet Potato Pie', cuisine='Southern Recipes', rating=4.8,
                    prep_time=15, cook_time=100, total_time=115,
                    description='A pie', nutrients={'calories': '389 kcal'}, serves='8')
        r2 = Recipe(title='Apple Pie', cuisine='American', rating=4.2,
                    prep_time=10, cook_time=50, total_time=60,
                    description='Apple pie', nutrients={'calories': '450 kcal'}, serves='6')
        db.session.add_all([r1, r2])
        db.session.commit()

    yield

    # teardown
    with app.app_context():
        db.session.remove()
        db.drop_all()
        # remove sqlite file
        try:
            os.remove('test_recipes.db')
        except Exception:
            pass


def test_get_recipes_pagination():
    client = app.test_client()
    resp = client.get('/api/recipes?page=1&limit=1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['page'] == 1
    assert data['limit'] == 1
    assert data['total'] == 2
    assert len(data['data']) == 1
    # first result should be the highest rated (4.8)
    assert data['data'][0]['title'] == 'Sweet Potato Pie'


def test_search_calories_filter():
    client = app.test_client()
    # search for calories <= 400 should return only Sweet Potato Pie (389)
    resp = client.get('/api/recipes/search?calories=<=400')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'data' in data
    titles = [r['title'] for r in data['data']]
    assert 'Sweet Potato Pie' in titles
    assert 'Apple Pie' not in titles