from flask import Blueprint, request
from models.bill import Bill, BillSchema, bill_schema, bills_schema
from models.member import Member, MemberSchema
from init import db
from datetime import datetime

from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import ProgrammingError, DataError, StatementError
from marshmallow import ValidationError


bill_bp = Blueprint("bill", __name__, url_prefix= "/bill")

@bill_bp.route("/create", methods= ["POST"])
@jwt_required()
def create_bill():
    try:
        body_data = BillSchema().load(request.get_json())
        if all(body_data.get(field) for field in ["due_date", "amount", "bill_title"]):
    # Proceed if these 3 fields are present.
            pass
        else:
            return {"Error": "Some fields are missing or empty = due_date, amount & bill_title must have data entered."}, 404
        
        bill = Bill(
            due_date = body_data.get("due_date"),
            amount = body_data.get("amount"),
            bill_title = body_data.get("bill_title"),
            description = body_data.get("description"),
            paid = body_data.get("paid")
            
        )
        stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
        member = db.session.scalar(stmt)
        
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

@bill_bp.route("/", methods= ["GET"])
@jwt_required()
def display_bills():
    try:
        stmt = db.select(Member).filter_by(member_id = get_jwt_identity())
        member = db.session.scalar(stmt)
        if not member:
            return {"Error": "Invalid token or member not found."}, 404
        
        group_id = member.fam_group_id
        body_data = request.get_json()
        user_date = body_data.get("bills_due_date_past")
        if not user_date:
            return {"Error": "Must enter a date , cannot be blank."}, 400
        user_date = datetime.strptime(user_date, "%Y-%m-%d")
    except (ValueError, TypeError):
        return {"Error": f"Invalid date format entered. Please enter YYYY-MM-DD."}

    stmt2 = (
        db.select(Bill).join(Member).where(Member.fam_group_id == group_id, Bill.due_date >= user_date)
    )
    bills = db.session.scalars(stmt2).all()

    if not bills:
        return {"message": f"There are no bills with a due date past: {user_date} ."}, 200
    
    return {
        "Bills due date list": bills_schema.dump(bills)
    }, 200

@bill_bp.route("/update/<int:id>", methods= ["PUT", "PATCH"])
@jwt_required()
def update_bill(id):
    try:
        body_data = BillSchema().load(request.get_json(), partial=True)
        
        stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
        member = db.session.scalar(stmt)
        group_id = member.fam_group_id
        stmt2 = db.select(Bill).filter_by(bill_id = id)
        bill = db.session.scalar(stmt2)
        
        if bill.member.fam_group_id != member.fam_group_id:
            return {"Error": "Update of Bills not in your same family group is not allowed. "}, 401

        if bill and member:
    # Update the fields if they exist in the request data, or keep the current values
            bill.due_date = body_data.get("due_date") or bill.due_date  
            bill.amount = body_data.get("amount") or bill.amount       
            bill.bill_title = body_data.get("bill_title") or bill.bill_title
            bill.description = body_data.get("description") or bill.description
            bill.paid = body_data.get("paid") or bill.paid
            bill.member_id = member.member_id
            
            db.session.commit()
            return {
                "Bill updated": "The bill fields have been updated."
            }, 200
        else:
            return {"Error": "This bill does not exist or you dont have authority."}, 404
    except (ProgrammingError, DataError, StatementError, ValidationError):
        return {"Error": "Incorrect field format. Please enter correct format."}, 400


@bill_bp.route("/delete/<int:id>", methods= ["DELETE"])
@jwt_required()
def delete_bill(id):
    stmt = db.select(Bill).filter_by(bill_id = id)
    bill = db.session.scalar(stmt)
    stmt2 = db.select(Member).filter_by(member_id = get_jwt_identity())
    member = db.session.scalar(stmt2)
    
    if not bill:
        return {"Error": f"Bill with id: {id}, does not exist."}, 404
    if bill.member.fam_group_id != member.fam_group_id:
            return {"Error": "Deletion of Bills not in your same family group is not allowed. "}
    
    if member.is_admin and member:
        db.session.delete(bill)
        db.session.commit()
        return {"message": f"Bill with id: {id} is deleted."}, 200
    else:
        return {"Error": "You are not a admin member and cannot delete Bills."}, 404

    



