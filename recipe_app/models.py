from flask_sqlalchemy import SQLAlchemy
import os
import json

# Choose the JSON column type based on the DATABASE_URL. If the app is
# configured to use PostgreSQL, prefer the PostgreSQL JSONB type for better
# querying performance and features; otherwise fall back to the generic
# SQLAlchemy JSON type which works with SQLite.
db = SQLAlchemy()
USE_POSTGRES_JSONB = False
database_url = os.environ.get('DATABASE_URL', '')
if 'postgres' in database_url or 'postgresql' in database_url:
    try:
        from sqlalchemy.dialects.postgresql import JSONB
        USE_POSTGRES_JSONB = True
    except Exception:
        # If the dialect isn't available, fall back to generic JSON.  The
        # developer should ensure psycopg2 and appropriate SQLAlchemy
        # dialects are installed when using Postgres.
        USE_POSTGRES_JSONB = False

class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    cuisine = db.Column(db.String(100))
    title = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float)
    prep_time = db.Column(db.Integer)
    cook_time = db.Column(db.Integer)
    total_time = db.Column(db.Integer)
    description = db.Column(db.Text)
    # Use JSONB for Postgres when available, otherwise use generic JSON.
    if USE_POSTGRES_JSONB:
        nutrients = db.Column(JSONB)
    else:
        nutrients = db.Column(db.JSON)
    serves = db.Column(db.String(50))
    url = db.Column(db.String(500))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'cuisine': self.cuisine,
            'rating': self.rating,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'total_time': self.total_time,
            'description': self.description,
            'nutrients': self.nutrients if self.nutrients else {},
            'serves': self.serves,
            'url': self.url
        }