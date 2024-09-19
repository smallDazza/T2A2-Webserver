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
    password = db.Column(db.String, nullable=False)
# the addition here of 'ondelete="cascade" means if a group from the family_group table is deleted all associated member records to that group will be deleted.
    fam_group_id = db.Column(db.Integer, db.ForeignKey("family_group.group_id", ondelete= "cascade"), nullable=False)

# bills creates a one to many relationship with bill table.
# cascade & passive_deletes works with 'ondelete= set null' in the Bill foreign key to set all bills to null if the member is deleted.
    bills = db.relationship("Bill", back_populates= "member", cascade= "all", passive_deletes=True)
# outings creates a one to many relationship with outing table.
# cascade & passive_deletes works with 'ondelete= set null' in the Outing foreign key to set all outings to null if the member is deleted.
    outings = db.relationship("Outing", back_populates= "member", cascade= "all", passive_deletes=True)
# invites creates a one to many relationship with invite_outing table.
# cascade & passive_deletes works with 'ondelete= set null' in the Invite foreign key to set all invites to null if the member is deleted.
    invites = db.relationship("Invite", back_populates= "member", cascade= "all", passive_deletes=True)
# group creates a relationship with family_group table.
    group = db.relationship("Group", back_populates= "members")


class MemberSchema(ma.Schema):
    
    bills = fields.Nested("BillSchema", many= True, exclude= ["member"])
    outings = fields.Nested("OutingSchema", many=True, exclude= ["member"])
    invites = fields.Nested("InviteSchema", many=True, exclude= ["member"])
    group = fields.Nested("GroupSchema", exclude= ["members"])


    class Meta:
        fields = ("member_id", "name", "phone_number", "email", "is_admin", "username", "password", "bills", "outings", "invites", "group")

member_schema = MemberSchema(exclude=["password"])

members_schema = MemberSchema(many=True, exclude=["password"])



        

