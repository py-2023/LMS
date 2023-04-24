from flask import Blueprint, app, render_template, session
from flask_login import login_required, current_user

home_bp = Blueprint("homepage", __name__)


# Flask views will only accept GET requests by default,
# unless the route decorator explicitly lists which HTTP methods the view should honor.
# multiple urls paths for same view
# @app.route('/', methods=['GET', 'POST'])

@home_bp.route("/")
@login_required
def index():  # put application's code here
    session['name'] =  current_user.username

    return render_template("homepage/index.html")
