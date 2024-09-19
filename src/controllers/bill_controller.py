from flask import Blueprint, request
from models.bill import Bill, BillSchema, bill_schema, bills_schema
from models.member import Member, MemberSchema
from init import db

from flask_jwt_extended import jwt_required, get_jwt_identity

bill_bp = Blueprint("bill", __name__, url_prefix= "/bill")

@bill_bp.route("/create", methods= ["POST"])
@jwt_required()
def create_bill():
    body_data = BillSchema().load(request.get_json())
    if all(body_data.get(field) for field in ["due_date", "amount", "bill_title"]):
# Proceed if these 3 fields are present.
        pass
    else:
        return {"Error": "Some fields are missing or empty. Due_date, amount & bill_title must have data entered."}, 404
    
    bill = Bill(
        due_date = body_data.get("due_date"),
        amount = body_data.get("amount"),
        bill_title = body_data.get("bill_title"),
        description = body_data.get("description"),
        paid = body_data.get("paid"),
        
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
        {"Error": "You do not have the authority to create Bills"}, 401

@bill_bp.route("/update/<int:id>", methods= ["PUT", "PATCH"])
@jwt_required()
def update_bill(id):
    body_data = BillSchema().load(request.get_json(), partial=True)
    
    stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
    member = db.session.scalar(stmt)
    stmt2 = db.select(Bill).filter_by(bill_id = id)
    bill = db.session.scalar(stmt2)

    if bill and member:
# Update the fields if they exist in the request data, or keep the current values
        bill.due_date = body_data.get("due_date", bill.due_date)  
        bill.amount = body_data.get("amount", bill.amount)       
        bill.bill_title = body_data.get("bill_title", bill.bill_title)
        bill.description = body_data.get("description", bill.description)
        bill.paid = body_data.get("paid", bill.paid)
        bill.member_id = member.member_id
        
        db.session.commit()
        return {
            "Bill updated": "The bill fields have been updated."
        }, 201
    else:
        return {"Error": "This bill does not exist or you dont have authority."}


@bill_bp.route("/delete/<int:id>", methods= ["DELETE"])
@jwt_required()
def delete_bill(id):
    stmt = db.select(Bill).filter_by(bill_id = id)
    bill = db.session.scalar(stmt)
    stmt2 = db.select(Member).filter_by(member_id = get_jwt_identity())
    member = db.session.scalar(stmt2)
    if not bill:
        return {"Error": f"Bill with id: {id}, does not exist."}, 404
    if member.is_admin and member:
        db.session.delete(bill)
        db.session.commit()
        return {"message": f"Bill with id: {id} is deleted."}, 200
    else:
        return {"Error": "You are not a admin member and cannot delete Bills."}, 404

    



