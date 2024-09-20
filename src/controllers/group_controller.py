from flask import Blueprint, request
from models.group import Group, GroupSchema, group_schema
from models.member import Member, MemberSchema
from init import bcrypt, db

from flask_jwt_extended import get_jwt_identity, jwt_required


group_bp = Blueprint("group", __name__, url_prefix="/group")

def create_group(family_name):
# because the family_group table has a mandatory relationship with the family_member table = the group must be commited first. 
        stmt = db.select(Group).where(Group.group_name == family_name)
        name = db.session.scalar(stmt)
        
        group = Group(
            group_name = family_name
        ) 
        if not name:
            db.session.add(group)
            db.session.commit()
            return group.group_id
        else:
             return name.group_id
                

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