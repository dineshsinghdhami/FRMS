from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return "Family Record Management System is running successfully!"

    return app