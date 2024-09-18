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
# the addition here of 'ondelete="set null" means if a member from the family_member table is deleted all associated outing records to that member will be set to null.
    member_id = db.Column(db.Integer, db.ForeignKey("family_member.member_id", ondelete= "set null"), nullable=True)

# member creates the relationship with the family_member table
    member = db.relationship("Member", back_populates= "outings")
# invites creates a one to many relationship with invite_outing table.
# cascade & passive_deletes works with 'ondelete= cascade' in the Outing foreign key to delete all invites for a outing if the Outing is deleted.
    invites = db.relationship("Invite", back_populates= "outing", cascade= "all, delete", passive_deletes=True)


    class OutingSchema(ma.Schema):
        member = fields.Nested("MemberSchema", exclude= ["outings"])
        invites = fields.Nested("InviteSchema", many=True, exclude= ["outing"])


        class Meta:
            fields = ("out_id", "start_date", "end_date", "title", "description", "public", "member", "invites")

    outing_schema = OutingSchema()
    
    outings_schema = OutingSchema(many=True)