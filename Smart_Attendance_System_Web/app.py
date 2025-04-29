from flask import Flask, render_template
from app.controllers.auth_controller import auth_bp
from app.controllers.analytics_controller import analytics_bp
from app.config import SECRET_KEY
import os

def create_app():
    """
    Create and configure the Flask application
    """
    app = Flask(__name__, 
                template_folder=os.path.join('app', 'templates'),
                static_folder=os.path.join('app', 'static'))
    
    # Configure the app
    app.secret_key = SECRET_KEY
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(analytics_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
