from init import db, ma
from marshmallow import fields


class Invite(db.Model):
    __table_name__ = "invite_outing"

    id = db.Column(db.Integer, primary_key=True)
    accept_invite = db.Column(db.Boolean)
    invite_message = db.Column(db.String(100))
    response_message = db.Column(db.String(100))
    out_id = db.Column(db.Integer, db.ForeignKey("outing.out_id", ondelete= "cascade"), nullable=False)
# the addition here of 'ondelete="set null" means if a group from the family_group table is deleted all associated invite records to that group will be set to null.
    fam_grp_id = db.Column(db.Integer, db.ForeignKey("family_group.group_id", ondelete= "set null"), nullable=False)
# the addition here of 'ondelete="set null" means if a member from the family_member table is deleted all associated invite records to that member will be set to null.
    member_id = db.Column(db.Integer, db.ForeignKey("family_member.member_id", ondelete= "set null"), nullable=True)

# member creates the relationship with the family_member table
    member = db.relationship("Member", back_populates= "invites") 
# group creates the relationship with the Group table
    group = db.relationship("Group", back_populates= "invites")
# outing creates the relationship with the Outing table
    outing = db.relationship("Outing", back_populates= "invites")


class InviteSchema(ma.Schema):
    member = fields.Nested("MemberSchema", exclude= ["invites"])
    group = fields.Nested("GroupSchema", exclude= ["invites"])
    outing = fields.Nested("OutingSchema", exclude= ["invites"])


    class Meta:
        fields = ("id", "accept_invite", "invite_message", "response_message","member", "group", "outing")

invites_schema = InviteSchema(many=True)

invite_schema = InviteSchema()

