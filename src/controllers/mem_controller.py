from flask import Blueprint, request
from models.member import Member, MemberSchema, member_schema
from models.group import Group, GroupSchema, group_schema
from init import bcrypt, db


from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta


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
        return {"Error": f"That group name: {user_group}, does not exist. You must create a family group before creating a family member."}, 404

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

@member_bp.route("/login", methods= ["POST"])
def member_login():
    body_data = request.get_json()
# find the member from the db with the correct username entered.
    stmt = db.select(Member).filter_by(username= body_data.get("username"))
    member = db.session.scalar(stmt)
# if user exists, check password is correct
    if member and bcrypt.check_password_hash(member.password, body_data.get("password")):
        token = create_access_token(identity=str(member.member_id), expires_delta=timedelta(days=1))

        return {"username": member.username, "is_admin": member.is_admin, "token": token}, 201
    else:
        return {"Error": "The username or password is incorrect"}
    
@member_bp.route("/update", methods= ["PUT", "PATCH"])
@jwt_required()
def update_member():
    try:
        body_data = MemberSchema().load(request.get_json(), partial=True)
        password = body_data.get("password")
        stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
        member = db.session.scalar(stmt)
        if member:
            member.username = body_data.get("username") or member.username
            member.name = body_data.get("name") or member.name
            member.phone_number = body_data.get("phone_number") or member.phone_number
            member.email = body_data.get("email") or member.email
            if password:
                member.password = bcrypt.generate_password_hash(password).decode("utf-8")
            db.session.commit()
            return member_schema.dump(member), 200
        else:
            return {"Error": "This member does not exist"}
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"Error": "An invalid token or same username has been used."}, 400
        
@member_bp.route("/delete/<int:id>", methods= ["DELETE"])
@jwt_required()
def delete_member(id):
    stmt = db.select(Member).filter_by(member_id = id)
    member = db.session.scalar(stmt)
    stmt2 = db.select(Member).filter_by(member_id = get_jwt_identity())
    member2 = db.session.scalar(stmt2)
    if not member:
        return {"Error": f"Member with id: {id}, does not exist."}, 404
    if member2.is_admin and member2:
        db.session.delete(member)
        db.session.commit()
        return {"message": f"Member with id: {id} is deleted."}, 200
    else:
        return {"Error": "You are not a admin member and cannot delete other members."}, 404






