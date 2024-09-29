from flask import Blueprint, request
from models.outing import Outing, OutingSchema, outing_schema, outings_schema
from models.member import Member, MemberSchema
from models.invite import Invite, InviteSchema
from controllers.invite_controller import private_invite
from init import db
from datetime import datetime

from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import extract, or_
from sqlalchemy.exc import ProgrammingError, DataError, StatementError
from marshmallow import ValidationError


outing_bp = Blueprint("outing", __name__, url_prefix= "/outing")
# this is the route location and method to be used to create a new outing (token required):
@outing_bp.route("/create", methods= ["POST"])
@jwt_required()
def create_outing():
    try:
        body_data = OutingSchema().load(request.get_json())
        if all(body_data.get(field) for field in ["start_date", "end_date", "title"]):
    # Proceed if these 3 fields are present.
            pass
        else:
            return {"Error": "Some fields are missing or empty = start_date, end_date & title must have data entered."}, 404
# assign the json request data to the outing variable:          
        outing = Outing(
            start_date = body_data.get("start_date"),
            end_date = body_data.get("end_date"),
            title = body_data.get("title"),
            description = body_data.get("description"),
            public = body_data.get("public") 
        )
# check the member id has a valid token, if not display a error:
        stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
        member = db.session.scalar(stmt)
        
        if not member:
            return {"Error": "Your token is invalid and not a member of this application."}, 401
# the FK member_id in the Outing function (outing table), will be assigned the member id of the member using the token.
# Then add the outing variable details and commit to the Outing table in database:      
        outing.member_id = member.member_id
        db.session.add(outing)
        db.session.commit()
# if the outing is private (public = false), then call the private invite function to create a private family invite:
        if not outing.public:
            response = private_invite(outing.out_id, member.fam_group_id)
        else:
            response = None
# assign the outing schema response to a variable:
        display_response = {
                "Created Outing": outing_schema.dump(outing)
            }
# if the private invite was created, add this extra text and the response text from the private invite function:
        if response:
            display_response["If public is false"] = f"{response}"
# then display the display response variable:
        return display_response, 201
            
    except (ProgrammingError, DataError, StatementError, ValidationError):
        return {"Error": "Incorrect field format. Please enter correct format."}, 400

# this is the route location and method to be used to view all outings (token required):
@outing_bp.route("/", methods= ["GET"])
@jwt_required()
def display_outings():
    try:
        body_data = request.get_json()
    # get the date entered by the member:
        user_date_ent = body_data.get("outings_during_year_month")
    # if no date , then display error message:
        if not user_date_ent:
            return {"Error": "Must enter a date of YYYY-MM , cannot be blank."}, 400
# using the datetime module, format the date entered by member. If not correct format entered display a warning:
        user_date = datetime.strptime(user_date_ent, "%Y-%m")
    except (ValueError, TypeError):
        return {"Error": f"Invalid date format entered. Please enter YYYY-MM."}, 400
# check the member id token is valid:   
    stmt = db.select(Member).filter_by(member_id = get_jwt_identity())
    member = db.session.scalar(stmt)
    if not member:
        return {"Error": "Invalid token or member not found."}, 404
# the member with the token will have their family group id assigned to this variable:       
    group_id = member.fam_group_id
# getting the members are that are linked to the same family group as the above variable,
# then joining them to the outings that belong to a member in the same family group.
# then getting these outings where the start date or end date match the member date entered:
    stmt2 = db.select(Outing).join(Member).where(Member.fam_group_id == group_id, Outing.member_id == Member.member_id).where(
        or_(
            (extract("year", Outing.start_date) == user_date.year) & (extract("month", Outing.start_date) == user_date.month),
            (extract("year", Outing.end_date) == user_date.year) & (extract("month", Outing.end_date) == user_date.month)
        )
    )
    outings = db.session.scalars(stmt2).all()
# if no matches from above query, display a message:
    if not outings:
        return {"message": f"There are no family outings during the: {user_date_ent}."}, 200
# display the results of above query:   
    return {
        f"Outings for {user_date_ent}": outings_schema.dump(outings)
    }, 200
# this is the route location and method to be used to update a outing details (token required):
@outing_bp.route("/update/<int:id>", methods= ["PUT", "PATCH"])
@jwt_required()
def update_outing(id):
    try:
        body_data = OutingSchema().load(request.get_json(), partial=True)
   # check the member id token is valid:     
        stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
        member = db.session.scalar(stmt)
# checking the id entered matches a outing id in outing table in database:
        stmt2 = db.select(Outing).filter_by(out_id = id)
        outing = db.session.scalar(stmt2)
# if member token is invalid or id entered does not exist, display errors:
        if not outing:
            return {"Error": f"Outing with id: {id}, does not exist."}, 404
        if not member:
            return {"Error": "Invalid token used. Update not allowed."}, 401 
# if the member using token belongs to a different family group than the member that entered the original outing,
# display error:
        if outing.member.fam_group_id != member.fam_group_id:
            return {"Error": "Update of Outings not in your same family group is not allowed. "}, 401

        
# Update the fields if they exist in the json request data, or keep the current values:
        outing.start_date = body_data.get("start_date") or outing.start_date  
        outing.end_date = body_data.get("end_date") or outing.end_date        
        outing.title = body_data.get("title") or outing.title
        outing.description = body_data.get("description") or outing.description
        outing.public = body_data.get("public") or outing.public
        outing.member_id = member.member_id
# commit changes to the outing table in database:          
        db.session.commit()
        return {
                "Outing updated": "The outing fields have been updated."
            }, 200
            
    except (ProgrammingError, DataError, StatementError, ValidationError):
        return {"Error": "Incorrect field format. Please enter correct format."}, 400

# this is the route location and method to be used to delete a outing (token required):
@outing_bp.route("/delete/<int:id>", methods= ["DELETE"])
@jwt_required()
def delete_bill(id):
    try:
# checking the id entered matches a outing id in outing table in database:
        stmt = db.select(Outing).filter_by(out_id = id)
        outing = db.session.scalar(stmt)
# check the member id token is valid: 
        stmt2 = db.select(Member).filter_by(member_id = get_jwt_identity())
        member = db.session.scalar(stmt2)
# if outing id does not exist,
# if the member using token belongs to a different family group than the member that entered the original outing,
# display error:
        if not outing:
            return {"Error": f"Outing with id: {id}, does not exist."}, 404
        if outing.member.fam_group_id != member.fam_group_id:
                return {"Error": "Deleting of Outings not in your same family group is not allowed. "}, 401
# if member with token is a admin then delete the outing from the outing table in database:      
        if member.is_admin and member:
            db.session.delete(outing)
            db.session.commit()
            return {"message": f"Outing with id: {id} is deleted."}, 200
        else:
            return {"Error": "You are not a admin member and cannot delete Outings."}, 404
    except AttributeError:
        return {"Error": "Invalid token used. Delete not allowed."}, 401

    