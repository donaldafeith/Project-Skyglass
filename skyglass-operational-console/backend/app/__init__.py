import os
import importlib
from flask import Flask
from flask_cors import CORS
from config import Config
from .extensions import db, migrate
from .services.scheduler import start_scheduler


def load_plugins(app):
    plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    if not os.path.exists(plugins_dir):
        return
    for filename in os.listdir(plugins_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = f"app.plugins.{filename[:-3]}"
            try:
                plugin = importlib.import_module(module_name)
                if hasattr(plugin, 'init_app'):
                    plugin.init_app(app)
                print(f"Loaded plugin: {module_name}")
            except Exception as e:
                print(f"Failed to load plugin {module_name}: {e}")


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    from .api.data_routes import data_bp
    app.register_blueprint(data_bp, url_prefix='/api')

    load_plugins(app)

    if app.config.get('SCHEDULER_API_ENABLED'):
        start_scheduler(app)

    return app
