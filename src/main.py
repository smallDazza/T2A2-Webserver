import os
from flask import Flask

from init import db, ma, bcrypt, jwt
from controllers.cli_controller import db_commands
from controllers.mem_controller import member_bp
from controllers.group_controller import group_bp
from controllers.bill_controller import bill_bp
from controllers.out_controller import outing_bp
from controllers.invite_controller import invite_bp


def create_app():
    app = Flask(__name__)
    app.json.sort_keys = False
# this is pointing to the .env file for the database connection details.
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
# initiate the app
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
# register the Blueprint variables from each controller:
    app.register_blueprint(db_commands)
    app.register_blueprint(member_bp)
    app.register_blueprint(group_bp)
    app.register_blueprint(bill_bp)
    app.register_blueprint(outing_bp)
    app.register_blueprint(invite_bp)

    return app


    