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
# the addition here of 'ondelete="set null" means if a member from the family_member table is deleted all associated bill records to that member will be set to null.
    member_id = db.Column(db.Integer, db.ForeignKey("family_member.member_id", ondelete= "set null"), nullable=True)

# member creates the relationship with the family_member table
    member = db.relationship("Member", back_populates= "bills")


class BillSchema(ma.Schema):
    member = fields.Nested("MemberSchema", exclude= ["bills"])


    class Meta:
        fields = ("bill_id", "due_date", "amount", "bill_title", "description", "paid", "member")

bill_schema = BillSchema()

bills_schema = BillSchema(many=True)