from flask import Blueprint, request
from models.outing import Outing, OutingSchema, outing_schema, outings_schema
from models.member import Member, MemberSchema
from controllers.invite_controller import private_invite
from init import db
from datetime import datetime

from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import extract, or_


outing_bp = Blueprint("outing", __name__, url_prefix= "/outing")

@outing_bp.route("/create", methods= ["POST"])
@jwt_required()
def create_outing():
    body_data = OutingSchema().load(request.get_json())
    if all(body_data.get(field) for field in ["start_date", "end_date", "title"]):
# Proceed if these 3 fields are present.
        pass
    else:
        return {"Error": "Some fields are missing or empty = start_date, end_date & title must have data entered."}, 404
         
    outing = Outing(
        start_date = body_data.get("start_date"),
        end_date = body_data.get("end_date"),
        title = body_data.get("title"),
        description = body_data.get("description"),
        public = body_data.get("public") 
    )
    stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
    member = db.session.scalar(stmt)
    
    if member:
        outing.member_id = member.member_id
        db.session.add(outing)
        db.session.commit()

        if not outing.public:
            response = private_invite(outing.out_id, member.fam_group_id)
        else:
            response = None

        display_response = {
            "Created Outing": outing_schema.dump(outing)
        }
        if response:
            display_response["If public is false"] = f"{response}"

        return display_response, 201
    else:
        {"Error": "You do not have the authority to create Outings"}, 401

@outing_bp.route("/", methods= ["GET"])
def display_outings():
    try:
        body_data = request.get_json()
        user_date_ent = body_data.get("outings_during_year_month")
        if not user_date_ent:
            return {"Error": "Must enter a date of YYYY-MM , cannot be blank."}, 400
        user_date = datetime.strptime(user_date_ent, "%Y-%m")
    except (ValueError, TypeError):
        return {"Error": f"Invalid date format entered. Please enter YYYY-MM."}, 400

    stmt = db.select(Outing).where(
        or_(
            (extract("year", Outing.start_date) == user_date.year) & (extract("month", Outing.start_date) == user_date.month),
            (extract("year", Outing.end_date) == user_date.year) & (extract("month", Outing.end_date) == user_date.month)
        )
    )
    
    outings = db.session.scalars(stmt).all()

    if not outings:
        return {"message": f"There are no outings during the: {user_date_ent}."}, 200
    
    return {
        f"Outings for {user_date_ent}": outings_schema.dump(outings)
    }, 200

@outing_bp.route("/outing/<int:id>", methods= ["PUT", "PATCH"])
@jwt_required()
def update_outing(id):
    body_data = OutingSchema().load(request.get_json(), partial=True)
    
    stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
    member = db.session.scalar(stmt)
    stmt2 = db.select(Outing).filter_by(out_id = id)
    outing = db.session.scalar(stmt2)

    if outing and member:
# Update the fields if they exist in the request data, or keep the current values
        outing.start_date = body_data.get("start_date") or outing.start_date  
        outing.end_date = body_data.get("end_date") or outing.end_date        
        outing.title = body_data.get("title") or outing.title
        outing.description = body_data.get("description") or outing.description
        outing.public = body_data.get("public") or outing.public
        outing.member_id = member.member_id
        
        db.session.commit()
        return {
            "Outing updated": "The outing fields have been updated."
        }, 201
    else:
        return {"Error": "This outing does not exist or you dont have authority."}


@outing_bp.route("/delete/<int:id>", methods= ["DELETE"])
@jwt_required()
def delete_bill(id):
    stmt = db.select(Outing).filter_by(out_id = id)
    outing = db.session.scalar(stmt)
    stmt2 = db.select(Member).filter_by(member_id = get_jwt_identity())
    member = db.session.scalar(stmt2)
    if not outing:
        return {"Error": f"Outing with id: {id}, does not exist."}, 404
    if member.is_admin and member:
        db.session.delete(outing)
        db.session.commit()
        return {"message": f"Outing with id: {id} is deleted."}, 200
    else:
        return {"Error": "You are not a admin member and cannot delete Outings."}, 404

    