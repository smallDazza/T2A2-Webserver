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
    member_id = db.Column(db.Integer, db.ForeignKey("family_member.member_id"), nullable=False)


    class OutingSchema(ma.Schema):


        class Meta:
            fields = ("out_id", "start_date", "end_date", "title", "description", "public", "member_id")

    outing_schema = OutingSchema()
    
    outings_schema = OutingSchema(many=True)