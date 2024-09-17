from init import db, ma
from marshmallow import fields


class Bill(db.Model):
    __tablename__ = "bill"

    bill_id = db.Column(db.Integer, primary_key=True)
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    bill_title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100))
    paid = db.Column(db.Boolean)
    member_id = db.Column(db.Integer, db.ForeignKey("member.member_id"), nullable=False)


    class BillSchema(ma.Schema):


        class Meta:
            fields = ("bill_id", "due_date", "amount", "bill_title", "description", "paid", "member_id")

    bill_schema = BillSchema()

    bills_schema = BillSchema(many=True)