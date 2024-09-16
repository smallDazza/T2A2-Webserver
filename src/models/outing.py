from init import db, ma
from marshmallow import fields


class Outing(db.Model):
    __tablename__ = "outing"

    out_id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    public = db.Column(db.Boolean)
    member_id = db.Column(db.Integer, db.ForeignKey("member.member_id"), nullable=False)


    class OutingSchema(ma.Schema):