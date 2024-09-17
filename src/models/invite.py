from init import db, ma
from marshmallow import fields


class Invite(db.Model):
    __table_name__ = "invite_outing"

    id = db.Column(db.Integer, primary_key=True)
    out_id = db.Column(db.Integer, db.ForeignKey("outing.out_id"), nullable=False)
    fam_grp_id = db.Column(db.Integer, db.ForeignKey("family_group.group_id"), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("family_member.member_id"), nullable=True)


class InviteSchema(ma.Schema):


    class Meta:
        fields = ("id", "out_id", "fam_grp_id", "member_id")

invites_schema = InviteSchema(many=True)

invite_schema = InviteSchema()

