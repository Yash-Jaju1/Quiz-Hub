from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from pathlib import Path
import os




db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app/data/quiz_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_object('config.Config')
    
    # Verify database path exists
    db_path = Path(__file__).parent.parent / "app" / "data" / "quiz_app.db"

    try:
        with open(db_path, 'a') as f:
            f.write('test')
        print("🎉 The notebook works!")
    except Exception as e:
        print(f"😢 Oh no! Error: {e}")

        
    if not db_path.parent.exists():
        os.makedirs(db_path.parent, exist_ok=True)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    with app.app_context():
        from . import routes
        routes.init_app(app, db)  # Pass db to routes
        db.create_all()

    return app
