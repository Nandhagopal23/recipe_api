from flask import Flask, request, jsonify, render_template
from recipe_app.models import db, Recipe
from recipe_app.data_parser import load_recipes_to_db
from recipe_app.config import Config
import os
import re

# Initialize DB migrations if Flask-Migrate is installed. We import inside a
# try/except so that the app can still run without Flask-Migrate present; the
# developer will be prompted to install it when they want to run migrations.
try:
    from flask_migrate import Migrate
except Exception:
    Migrate = None

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
if Migrate is not None:
    try:
        migrate = Migrate(app, db)
    except Exception as e:
        # If migrations fail to initialize for any reason, continue running the
        # app but log the issue so developer can fix their environment.
        print(f"Warning: Flask-Migrate failed to initialize: {e}")
else:
    print("Flask-Migrate not installed. Install with 'pip install Flask-Migrate' to enable DB migrations.")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    # Simple health check for containers and CI smoke-tests
    return jsonify({'status': 'ok'}), 200

# API Endpoint 1: Get all recipes (paginated and sorted by rating)
@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    try:
        # Get query parameters with defaults
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Query recipes with pagination and sorting
        recipes_query = Recipe.query.order_by(Recipe.rating.desc().nulls_last())
        total_recipes = recipes_query.count()
        recipes = recipes_query.offset(offset).limit(limit).all()
        
        response = {
            'page': page,
            'limit': limit,
            'total': total_recipes,
            'data': [recipe.to_dict() for recipe in recipes]
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Endpoint 2: Search recipes
@app.route('/api/recipes/search', methods=['GET'])
def search_recipes():
    try:
        query = Recipe.query
        
        # Apply filters
        calories_filter = request.args.get('calories')
        title_filter = request.args.get('title')
        cuisine_filter = request.args.get('cuisine')
        total_time_filter = request.args.get('total_time')
        rating_filter = request.args.get('rating')
        
        # Title filter (partial match)
        if title_filter:
            query = query.filter(Recipe.title.ilike(f'%{title_filter}%'))
        
        # Cuisine filter
        if cuisine_filter:
            query = query.filter(Recipe.cuisine.ilike(f'%{cuisine_filter}%'))
        
        # Rating filter
        if rating_filter:
            if rating_filter.startswith('>='):
                rating_value = float(rating_filter[2:])
                query = query.filter(Recipe.rating >= rating_value)
            elif rating_filter.startswith('<='):
                rating_value = float(rating_filter[2:])
                query = query.filter(Recipe.rating <= rating_value)
            elif rating_filter.startswith('>'):
                rating_value = float(rating_filter[1:])
                query = query.filter(Recipe.rating > rating_value)
            elif rating_filter.startswith('<'):
                rating_value = float(rating_filter[1:])
                query = query.filter(Recipe.rating < rating_value)
            else:
                rating_value = float(rating_filter)
                query = query.filter(Recipe.rating == rating_value)
        
        # Total time filter
        if total_time_filter:
            if total_time_filter.startswith('>='):
                time_value = int(total_time_filter[2:])
                query = query.filter(Recipe.total_time >= time_value)
            elif total_time_filter.startswith('<='):
                time_value = int(total_time_filter[2:])
                query = query.filter(Recipe.total_time <= time_value)
            elif total_time_filter.startswith('>'):
                time_value = int(total_time_filter[1:])
                query = query.filter(Recipe.total_time > time_value)
            elif total_time_filter.startswith('<'):
                time_value = int(total_time_filter[1:])
                query = query.filter(Recipe.total_time < time_value)
            else:
                time_value = int(total_time_filter)
                query = query.filter(Recipe.total_time == time_value)
        
        # Calories filter (from nutrients JSON)
        def parse_calories_value(val):
            """Parse a calories string like '389 kcal' and return integer or None."""
            if not val:
                return None
            # Try to extract first integer in the string
            if isinstance(val, (int, float)):
                try:
                    return int(val)
                except Exception:
                    return None
            m = re.search(r"(\d+)", str(val))
            if m:
                try:
                    return int(m.group(1))
                except Exception:
                    return None
            return None

        def cal_matches(cal_val, filter_str):
            if cal_val is None:
                return False
            try:
                if filter_str.startswith('>='):
                    v = int(filter_str[2:])
                    return cal_val >= v
                if filter_str.startswith('<='):
                    v = int(filter_str[2:])
                    return cal_val <= v
                if filter_str.startswith('>'):
                    v = int(filter_str[1:])
                    return cal_val > v
                if filter_str.startswith('<'):
                    v = int(filter_str[1:])
                    return cal_val < v
                # exact
                v = int(filter_str)
                return cal_val == v
            except Exception:
                return False

        recipes = None
        if calories_filter:
            # Detect DB dialect; prefer SQL-level JSON filtering for Postgres
            dialect = None
            try:
                dialect = db.session.bind.dialect.name
            except Exception:
                dialect = None

            if dialect and 'postgres' in dialect:
                # Use SQL JSON access + cast for Postgres
                if calories_filter.startswith('>='):
                    cal_value = int(calories_filter[2:])
                    query = query.filter(Recipe.nutrients['calories'].astext.cast(db.Integer) >= cal_value)
                elif calories_filter.startswith('<='):
                    cal_value = int(calories_filter[2:])
                    query = query.filter(Recipe.nutrients['calories'].astext.cast(db.Integer) <= cal_value)
                elif calories_filter.startswith('>'):
                    cal_value = int(calories_filter[1:])
                    query = query.filter(Recipe.nutrients['calories'].astext.cast(db.Integer) > cal_value)
                elif calories_filter.startswith('<'):
                    cal_value = int(calories_filter[1:])
                    query = query.filter(Recipe.nutrients['calories'].astext.cast(db.Integer) < cal_value)
                else:
                    cal_value = int(calories_filter)
                    query = query.filter(Recipe.nutrients['calories'].astext.cast(db.Integer) == cal_value)

                recipes = query.all()
            else:
                # Fallback: fetch candidates and apply calories filter in Python
                candidates = query.all()
                filtered = []
                for r in candidates:
                    cal_raw = None
                    try:
                        cal_raw = r.nutrients.get('calories') if r.nutrients else None
                    except Exception:
                        cal_raw = None
                    cal_val = parse_calories_value(cal_raw)
                    if cal_matches(cal_val, calories_filter):
                        filtered.append(r)
                recipes = filtered
        else:
            recipes = query.all()
        
        response = {
            'data': [recipe.to_dict() for recipe in recipes]
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def init_db():
    """Initialize database and load data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if we need to load data
        if Recipe.query.count() == 0:
            # Use a package-relative path so the JSON file is found whether
            # the app is started with `python app.py` or `python -m recipe_app.app`.
            base_dir = os.path.dirname(__file__)
            json_file_path = os.path.join(base_dir, 'recipes.json')
            if os.path.exists(json_file_path):
                load_recipes_to_db(json_file_path, db, Recipe)
            else:
                print(f"JSON file not found at {json_file_path}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)