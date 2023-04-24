from flask import render_template, make_response, redirect, request
from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager

# With the above, our app knows that calling render_template()
# in a Flask route will look in our app's /templates folder for the template we pass in


app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
FLASK_DEBUG=1

# Registering blueprints
from app.auth.views import auth_bp
from app.home.views import home_bp
from app.lms.views import lms_bp

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(lms_bp)

# for redirecting to login
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)


@app.errorhandler(404)
def not_found():
    """Page not found."""
    return make_response(
        render_template("custom-http-responses/404.html"),
        404
    )


@app.errorhandler(400)
def bad_request():
    """Bad request."""
    return make_response(
        render_template("custom-http-responses/400.html"),
        400
    )


@app.errorhandler(500)
def server_error():
    """Internal server error."""
    return make_response(
        render_template("custom-http-responses/500.html"),
        500
    )


# not required
if __name__ == '__main__':
    app.run(debug=True)
