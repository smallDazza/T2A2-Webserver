from init import db, ma
from marshmallow import fields


class Group(db.Model):
    __tablename__ = "family_group"
    
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)

# member creates a one to many relationship with family_member table.
# cascade & passive_deletes works with 'ondelete=CASCADE' in the Member foreign key to delete all members in a group if the group is deleted.
    members = db.relationship("Member", back_populates= "group", cascade= "all, delete", passive_deletes=True)
# invites creates a one to many relationship with invite_outing table.
# cascade & passive_deletes works with 'ondelete= set null' in the Invite foreign key to set all invites to null if the group is deleted.
    invites = db.relationship("Invite", back_populates= "group",  cascade= "all", passive_deletes=True)


class GroupSchema(ma.Schema):
    members = fields.Nested("MemberSchema", exclude= ["group"])
    invites = fields.Nested("InviteSchema", many=True, exclude= ["group"])

    class Meta:
        fields = ("group_id", "group_name", "members", "invites")

group_schema = GroupSchema()

groups_schema = GroupSchema(many=True)
