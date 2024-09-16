from init import db, ma
from marshmallow import fields


class Group(db.Model):
    __tablename__ = "family_group"
    
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)


class GroupSchema(ma.Schema):
