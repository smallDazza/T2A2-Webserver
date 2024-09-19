from flask import Blueprint, request
from models.group import Group, GroupSchema, group_schema
from models.member import Member, MemberSchema
from init import bcrypt, db

from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import get_jwt_identity, jwt_required

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
            return {"Error": "This Family group name already exists. Please add a new Family group name"}, 400

@group_bp.route("/delete/<int:id>", methods= ["DELETE"])
@jwt_required()
def delete_group(id):
    stmt = db.select(Group).filter_by(group_id = id)
    group = db.session.scalar(stmt)
    stmt2 = db.select(Member).filter_by(member_id = get_jwt_identity())
    auth_member = db.session.scalar(stmt2)
    if not group:
        return {"Error": f"Group with id: {id}, does not exist"}, 404
    if auth_member.is_admin and auth_member:
        db.session.delete(group)
        db.session.commit()
        return {"messsage": f"Group with id: {id}, has been deleted."}, 200
    else:
        return {"Error": "You are not a admin member and cannot delete family groups."}, 404