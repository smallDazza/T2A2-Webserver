from flask import Blueprint, request
from models.group import Group, GroupSchema, group_schema
from models.member import Member, MemberSchema
from init import bcrypt, db

from flask_jwt_extended import get_jwt_identity, jwt_required


group_bp = Blueprint("group", __name__, url_prefix="/group")
# this function will is called from the mem_controller:
def create_group(family_name):
# because the family_group table has a mandatory relationship with the family_member table,
# = the group must be commited first.
# So checking to see if the group name already exists: 
        stmt = db.select(Group).where(Group.group_name == family_name)
        name = db.session.scalar(stmt)
        
        group = Group(
            group_name = family_name
        ) 
# if group name does not exist = adds & create this new group to the family_group table in database,
# and returns the new family group id.
# if name does exist, returns the current family group id.
        if not name:
            db.session.add(group)
            db.session.commit()
            return group.group_id
        else:
             return name.group_id
                
# this is the route location and method to be used to delete a family group (token required):
@group_bp.route("/delete/<int:id>", methods= ["DELETE"])
@jwt_required()
def delete_group(id):
# check the id entered is a group id in family_group table:
    stmt = db.select(Group).filter_by(group_id = id)
    group = db.session.scalar(stmt)
# check the member token is valid:
    stmt2 = db.select(Member).filter_by(member_id = get_jwt_identity())
    auth_member = db.session.scalar(stmt2)
# if not group id exists, display error:
    if not group:
        return {"Error": f"Group with id: {id}, does not exist"}, 404
# check if the member with the token is a administrator and valid member:
    if auth_member.is_admin and auth_member:
# also if the member with the token belongs to same family group as group id entered:
        if auth_member.fam_group_id == group.group_id:
            db.session.delete(group)
            db.session.commit()
            return {"messsage": f"Group with id: {id}, and all this group members have been deleted."}, 200
        else:
             return {"Error": "Cannot delete family groups you are not assigned to. Admin user can only delete the group they belong to."}, 404
    else:
        return {"Error": "You are not a admin member and cannot delete family groups."}, 404