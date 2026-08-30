import os
from flask import Flask, render_template, session, redirect, url_for
from config import Config
from models.database import get_db

# Import Blueprints
from routes.auth_routes import auth_bp, auth_views_bp
from routes.student_routes import student_bp, student_views_bp
from routes.company_routes import company_bp, company_views_bp
from routes.notification_routes import notification_bp, notification_views_bp
from routes.report_routes import report_bp, report_views_bp
from routes.resume_routes import resume_bp

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object(Config)
    
    # Initialize database & seed data if needed
    with app.app_context():
        db = get_db()
        print("Database initialized successfully.")
        
    # Register API Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(student_bp, url_prefix="/api/students")
    app.register_blueprint(company_bp, url_prefix="/api/companies")
    app.register_blueprint(notification_bp, url_prefix="/api/notifications")
    app.register_blueprint(report_bp, url_prefix="/api/reports")
    app.register_blueprint(resume_bp, url_prefix="/api/resume")
    
    # Register View Blueprints
    app.register_blueprint(auth_views_bp)
    app.register_blueprint(student_views_bp)
    app.register_blueprint(company_views_bp)
    app.register_blueprint(notification_views_bp)
    app.register_blueprint(report_views_bp)
    
    # Global error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        from flask import request, jsonify
        if request.path.startswith("/api/"):
            return jsonify({"error": "Endpoint not found", "code": 404}), 404
        return render_template("login.html"), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        from flask import request, jsonify
        import traceback
        original = getattr(e, "original_exception", None)
        err_msg = str(original) if original else str(e)
        tb = traceback.format_exc()
        if request.path.startswith("/api/"):
            return jsonify({
                "error": "Internal server error occurred",
                "details": err_msg,
                "traceback": tb,
                "code": 500
            }), 500
        return render_template("login.html"), 500
        
    return app

app = create_app()

if __name__ == "__main__":
    # Host on all interfaces for network testing
    app.run(host="0.0.0.0", port=5000, debug=True)
