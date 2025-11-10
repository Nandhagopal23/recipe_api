import json
import math

def parse_json_file(file_path):
    """Parse the JSON file and handle NaN values"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # If it's a single recipe, wrap it in a list
        if isinstance(data, dict):
            data = [data]
        
        parsed_recipes = []
        
        for recipe_data in data:
            # Handle NaN values for numeric fields
            numeric_fields = ['rating', 'prep_time', 'cook_time', 'total_time']
            
            for field in numeric_fields:
                value = recipe_data.get(field)
                if value is None or (isinstance(value, str) and value.lower() == 'nan'):
                    recipe_data[field] = None
                elif isinstance(value, (int, float)) and math.isnan(value):
                    recipe_data[field] = None
            
            # Ensure nutrients is a proper dictionary
            nutrients = recipe_data.get('nutrients', {})
            if nutrients is None:
                nutrients = {}
            
            parsed_recipe = {
                'cuisine': recipe_data.get('cuisine'),
                'title': recipe_data.get('title'),
                'rating': recipe_data.get('rating'),
                'prep_time': recipe_data.get('prep_time'),
                'cook_time': recipe_data.get('cook_time'),
                'total_time': recipe_data.get('total_time'),
                'description': recipe_data.get('description'),
                'nutrients': nutrients,
                'serves': recipe_data.get('serves'),
                'url': recipe_data.get('URL')  # Note: URL in JSON maps to url in DB
            }
            
            parsed_recipes.append(parsed_recipe)
        
        return parsed_recipes
    
    except Exception as e:
        print(f"Error parsing JSON file: {e}")
        return []

def load_recipes_to_db(file_path, db, Recipe):
    """Load parsed recipes into database"""
    recipes_data = parse_json_file(file_path)
    
    for recipe_data in recipes_data:
        recipe = Recipe(**recipe_data)
        db.session.add(recipe)
    
    try:
        db.session.commit()
        print(f"Successfully loaded {len(recipes_data)} recipes into database")
    except Exception as e:
        db.session.rollback()
        print(f"Error loading recipes to database: {e}")