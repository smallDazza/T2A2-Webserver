from flask import Blueprint, request
from models.member import Member, MemberSchema, member_schema, members_schema
from models.group import Group, GroupSchema, group_schema
from controllers.group_controller import create_group
from init import bcrypt, db

from sqlalchemy.exc import IntegrityError, ProgrammingError, StatementError
from marshmallow import ValidationError
from psycopg2 import errorcodes
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta


member_bp = Blueprint("member", __name__, url_prefix="/member")
# this is the route location and method to be used to create a new member:
@member_bp.route("/create", methods= ["POST"])
def create_member():
    try:
# get the member & group data from the json request, then adding the password & group into variables:
        body_data = request.get_json()
        password = body_data.get("password")
        group = body_data.get("family_group_name")
        if all(body_data.get(field) for field in ["name","username", "password", "family_group_name"]):
# Proceed if these 4 fields are present.
            pass
        else:
            return {"Error": "Some fields are missing or empty = name, username, password & family group name must have data entered."}, 404
        
# check if the password length is between 8 and 12 characters
        if not (8 <= len(password) <= 12):
            return {"Error": "The password must be between 8 and 12 characters long. Please re-enter a new password."}, 400
# checking if the member is going to be a administrator. If = true, then calls the create group function to create the group name entered.
        admin = body_data.get("is_admin")
        if admin:
            family_group_id = create_group(group)
        else:
# if not a admin member = the member will join the group name they entered in.
            stmt = db.select(Group).where(Group.group_name == group)
            grp_name = db.session.scalar(stmt)
            family_group_id = grp_name.group_id 
# the variable member will have all the member inputs:
        member = Member(
            name = body_data.get("name"),
            phone_number = body_data.get("phone_number"),
            email = body_data.get("email"),
            is_admin = body_data.get("is_admin"),
            username = body_data.get("username"),
            fam_group_id = family_group_id  
        )
    # hash the password into the database table.
        if password:
            member.password = bcrypt.generate_password_hash(password).decode("utf-8")    
  # add the member variable details and then commit to the family_member table in the database:          
        db.session.add(member)
        db.session.commit()
# return the member_schema details as a json format:
        return {
            "Created Member": member_schema.dump(member)
        }, 201
    except AttributeError:
        return {"Error": "No Family group by that name exists."}, 400 
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION: 
            return {"Error": "That Username already exists. Please re-enter a new username."}, 400
    except (ProgrammingError, StatementError, TypeError):
            return {"Error": "Incorrect format for the fields entered."}, 400
# this is the route location and method to be used for a member to login and generate a jwt_token:
@member_bp.route("/login", methods= ["POST"])
def member_login():
    try:
        body_data = request.get_json()
    # find the member from the db with the correct username entered.
        stmt = db.select(Member).filter_by(username= body_data.get("username"))
        member = db.session.scalar(stmt)
    # if user exists, check password is correct = then create a token:
        if member and bcrypt.check_password_hash(member.password, body_data.get("password")):
            token = create_access_token(identity=str(member.member_id), expires_delta=timedelta(days=1))
# this returns the username, their admin status and the token to use:
            return {"username": member.username, "is_admin": member.is_admin, "token": token}, 201
        else:
            return {"Error": "The username or password is incorrect"}, 400
    except (ProgrammingError,TypeError):
        return {"Error": "Invalid field format. Please re-enter in correct format"}, 400
# this is the route location and method to be used to view all members in the same family group:
@member_bp.route("/view", methods= ["GET"])
# members must use a token to view:
@jwt_required()
def view_members():
# checking the member id has a token:
    stmt = db.select(Member).filter_by(member_id = get_jwt_identity())
    member = db.session.scalar(stmt)
    if not member:
        return {"Error": "Invalid member token."},400
#  getting all the members that have the same family group id as the member with the token:   
    stmt2 = db.select(Member).where(Member.fam_group_id == member.fam_group_id)
    members = db.session.scalars(stmt2).all()

    if members:
        return {
            "The family members in your family group are": members_schema.dump(members)
        }, 200
    else:
        return {"Error": "There are no members in your family group."}, 404
# this is the route location and method to be used to update a member detils (must have a token):
@member_bp.route("/update/<int:id>", methods= ["PUT", "PATCH"])
@jwt_required()
def update_member(id):
    try:
# requesting the data from json and loading it with partial values in the MemberSchema:
        body_data = MemberSchema().load(request.get_json(), partial=True)
        password = body_data.get("password")
# checking the id entered matches a member id in database:
        stmt = db.select(Member).filter_by(member_id = id)
        member = db.session.scalar(stmt)
# checking the member id has a token:
        stmt2 = db.select(Member).filter_by(member_id = get_jwt_identity())
        member2 = db.session.scalar(stmt2)
# if the user with the token does not belong to the same family group = displays error         
        if member2.fam_group_id != member.fam_group_id:
            return {
            "Error": f"Member with id: {id} does not exist in your family group. Update not permitted."
        }, 404
# check if the password length is between 8 and 12 characters
        if not (8 <= len(password) <= 12):
            return {"Error": "The password must be between 8 and 12 characters long. Please re-enter a new password."}, 400
# if the member is a administrator then,
# update the fields present in the json request or leave as current:
        if member2.is_admin:
            member.username = body_data.get("username") or member.username
            member.name = body_data.get("name") or member.name
            member.phone_number = body_data.get("phone_number") or member.phone_number
            member.email = body_data.get("email") or member.email
            if "is_admin" in body_data:
                member.is_admin = body_data.get("is_admin")
            if password:
                member.password = bcrypt.generate_password_hash(password).decode("utf-8")
# commit to the family_member table in the database and return the member schema details:
            db.session.commit()
            return member_schema.dump(member), 200
# if not a admin user = cannot do updates and advise them:      
        else:
            return {"Error": "You are not an admin user.Only admin users can update"}, 400
    
    except (ProgrammingError,TypeError, StatementError):
        return {"Error": "Invalid field format. Please re-enter in correct format"}, 400
    except ValidationError as err:
        return {"Error": f"These fields do not exist: {err}, please remove."}, 400
    except AttributeError:
        return {"Error": "Invalid member token or id entered."},404
# this is the route location and method to be used to delete a member (must have a token):   
@member_bp.route("/delete/<int:id>", methods= ["DELETE"])
@jwt_required()
def delete_member(id):
# checking the id entered matches a member in database:
    stmt = db.select(Member).filter_by(member_id = id)
    member = db.session.scalar(stmt)
# checking the member id has a token:
    stmt2 = db.select(Member).filter_by(member_id = get_jwt_identity())
    member2 = db.session.scalar(stmt2)
# if the member to be deleted does not exist:
    if not member:
        return {"Error": f"Member with id: {id} does not exist."}, 404

# if the user with the token does not belong to the same family group
    if member2.fam_group_id != member.fam_group_id:
        return {
            "Error": f"Member with id: {id} does not exist in your family group. Delete not permitted."
        }, 404

# if the current member with the token is not an admin
    if not member2.is_admin:
        return {"Error": "You are not an admin member and cannot delete other members."}, 403
# delete the member from the family_member table in database and display the message:
    db.session.delete(member)
    db.session.commit()
    return {"message": f"Member with id: {id} is deleted."}, 200
   






