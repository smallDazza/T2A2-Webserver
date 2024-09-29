from flask import Blueprint, request
from models.bill import Bill, BillSchema, bill_schema, bills_schema
from models.member import Member, MemberSchema
from init import db
from datetime import datetime

from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import ProgrammingError, DataError, StatementError
from marshmallow import ValidationError


bill_bp = Blueprint("bill", __name__, url_prefix= "/bill")
# this is the route location and method to be used to create a new bill (token required):
@bill_bp.route("/create", methods= ["POST"])
@jwt_required()
def create_bill():
    try:
        body_data = BillSchema().load(request.get_json())
        if all(body_data.get(field) for field in ["due_date", "amount", "bill_title"]):
    # Proceed if these 3 fields are present , if not will display a error to advise them , they must add in.
            pass
        else:
            return {"Error": "Some fields are missing or empty = due_date, amount & bill_title must have data entered."}, 404
 # the bill variable will be assigned the json file details:       
        bill = Bill(
            due_date = body_data.get("due_date"),
            amount = body_data.get("amount"),
            bill_title = body_data.get("bill_title"),
            description = body_data.get("description"),
            paid = body_data.get("paid")
            
        )
        # checking the member id has a token:
        stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
        member = db.session.scalar(stmt)
        # if the token is ok , proceed to create the new bill and commit to the bill table in the database:
        if member:
            bill.member_id = member.member_id
            db.session.add(bill)
            db.session.commit()

            return {
            "Created Bill": bill_schema.dump(bill)
            }, 201
        else:
            return {"Error": "You do not have the authority to create Bills"}, 401
    except (ProgrammingError, DataError, StatementError, ValidationError):
        return {"Error": "Incorrect field format. Please enter correct format."}, 400
# this is the route location and method to be used to view a list of all the bills (token required):
@bill_bp.route("/", methods= ["GET"])
@jwt_required()
def display_bills():
    try:
         # checking the member id has a token:
        stmt = db.select(Member).filter_by(member_id = get_jwt_identity())
        member = db.session.scalar(stmt)
        if not member:
            return {"Error": "Invalid token or member not found."}, 404
        # assigning the group id variable with the member using the tokens , family group id they belong to:
        group_id = member.fam_group_id
        # requesting the json data to a variable:
        body_data = request.get_json()
        # getting the date the member entered:
        user_date = body_data.get("bills_due_date_past")
        # if the date is blank:
        if not user_date:
            return {"Error": "Must enter a date , cannot be blank."}, 400
        # using the datetime module & function to format the date entered. If incorrect format entered will display a error:
        user_date = datetime.strptime(user_date, "%Y-%m-%d")
    except (ValueError, TypeError):
        return {"Error": f"Invalid date format entered. Please enter YYYY-MM-DD."},400
# getting from the database where all the members that belong to the same group as the member using the token,
# and then all the bills with a due date equal to or greater than the date entered.
# Then joining these to only get the bills with that member id:
    stmt2 = (
        db.select(Bill).join(Member).where(Member.fam_group_id == group_id, Bill.due_date >= user_date)
    )
    bills = db.session.scalars(stmt2).all()
# if no bills with the same member id as token user or past the date range entered, display a message to member:
    if not bills:
        return {"message": f"There are no bills with a due date past: {user_date} ."}, 200
# display the bills schema of the matching results above: 
    return {
        "Bills due date list": bills_schema.dump(bills)
    }, 200
# this is the route location and method to be used to update the details of a  bill (token required):
@bill_bp.route("/update/<int:id>", methods= ["PUT", "PATCH"])
@jwt_required()
def update_bill(id):
    try:
        body_data = BillSchema().load(request.get_json(), partial=True)
# checking the member id has a token:     
        stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
        member = db.session.scalar(stmt)
# checking the id entered matches a bill id in the database:
        group_id = member.fam_group_id
        stmt2 = db.select(Bill).filter_by(bill_id = id)
        bill = db.session.scalar(stmt2)
# if no bill id exists, display a error:      
        if bill.member.fam_group_id != member.fam_group_id:
            return {"Error": "Update of Bills not in your same family group is not allowed. "}, 401

# Update the fields if they exist in the json request data, or keep the current values:
        bill.due_date = body_data.get("due_date") or bill.due_date  
        bill.amount = body_data.get("amount") or bill.amount       
        bill.bill_title = body_data.get("bill_title") or bill.bill_title
        bill.description = body_data.get("description") or bill.description
        bill.paid = body_data.get("paid") or bill.paid
        bill.member_id = member.member_id
# commit to the bill table in databse and display message:           
        db.session.commit()
        return {
                "Bill updated": f"The bill fields of bill id: {id} -have been updated."
            }, 200

    except AttributeError:
        return {"Error": "This bill does not exist or invalid token."}, 404
    except (ProgrammingError, DataError, StatementError, ValidationError):
        return {"Error": "Incorrect field format. Please enter correct format."}, 400

# this is the route location and method to be used to delete a bill (token required):
@bill_bp.route("/delete/<int:id>", methods= ["DELETE"])
@jwt_required()
def delete_bill(id):
    try:
# checking the id entered matches a bill id in the database:
        stmt = db.select(Bill).filter_by(bill_id = id)
        bill = db.session.scalar(stmt)
# checking the member id has a token: 
        stmt2 = db.select(Member).filter_by(member_id = get_jwt_identity())
        member = db.session.scalar(stmt2)
        
        if not bill:
            return {"Error": f"Bill with id: {id}, does not exist."}, 404
# checking if the bill id entered , has the same family group id as the member with the token.
# If not then the bill cannot be deleted by the member: 
        if bill.member.fam_group_id != member.fam_group_id:
                return {"Error": "Deletion of Bills not in your same family group is not allowed."},400
# checking if the member with the token is a admin. If not cannot delete. 
# If is a admin user delete from bill table in database:      
        if member.is_admin and member:
            db.session.delete(bill)
            db.session.commit()
            return {"message": f"Bill with id: {id} is deleted."}, 200
        else:
            return {"Error": "You are not a admin member and cannot delete Bills."}, 404
    except AttributeError:
        return {"Error": "Invalid token used. Delete not allowed."}, 401

    



