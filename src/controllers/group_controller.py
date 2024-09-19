from flask import Blueprint, request
from models.group import Group, GroupSchema, group_schema
from init import bcrypt, db

from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

group_bp = Blueprint("group", __name__, url_prefix="/group")

@group_bp.route("/create", methods=["POST"])
def create_group():
    try:
# because the family_group table has a mandatory relationship with the family_member table = the group must be commited first. 
        body_data = GroupSchema().load(request.get_json())
        check_blank = body_data.get("group_name")
        if check_blank == "":
            return {"Error": "The group name cannot be blank"}, 400
        group = Group(
            group_name = body_data.get("group_name")
        ) 

        db.session.add(group)
        db.session.commit()

        return {
            "Created Group": group_schema.dump(group)
            }, 201
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"Error": f"This Family group name already exists. Please add a new Family group name"}, 400