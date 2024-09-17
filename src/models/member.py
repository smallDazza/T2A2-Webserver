from init import db, ma
from marshmallow import fields


class Member(db.Model):
    __tablename__ = "family_member"

    member_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.Integer)
    email = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    fam_group_id = db.Column(db.Integer, db.ForeignKey("group.group_id"), nullable=False)


    class MemberSchema(ma.Schema):

        class Meta:
            fields = ("member_id", "name", "phone_number", "email", "is_admin", "username", "password", "fam_group_id")

    member_schema = MemberSchema(exclude=["password"])

    members_schema = MemberSchema(many=True, exclude=["password"])



        

