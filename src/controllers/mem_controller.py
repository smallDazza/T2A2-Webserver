from flask import Blueprint, request
from models.member import Member, MemberSchema, member_schema
from models.group import Group, GroupSchema, group_schema
from init import bcrypt, db

from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity


member_bp = Blueprint("member", __name__, url_prefix="/member")

@member_bp.route("/create", methods= ["POST"])
def create_member():
# get the member & group data from the json request
    body_data = request.get_json()
    member_data = body_data.get("member")
    group_data = body_data.get("family_group")
    user_group = group_data.get("group_name")

    group = Group.query.filter_by(group_name = user_group).first()
    if group:
        family_assigned = group.group_id
    else:
        return {"Error": f"That group name: {user_group}, does not exist"}, 404

    member = Member(
        name = member_data.get("name"),
        phone_number = member_data.get("phone_number"),
        email = member_data.get("email"),
        is_admin = member_data.get("is_admin"),
        username = member_data.get("username"),
        fam_group_id = family_assigned  
    )
# hash the password into the table.
    password = member_data.get("password")
    if password:
        member.password = bcrypt.generate_password_hash(password).decode("utf-8")    
        
    db.session.add(member)
    db.session.commit()

    return {
        "Created Member": member_schema.dump(member)
    }, 201
