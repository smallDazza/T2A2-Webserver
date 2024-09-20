from flask import Blueprint, request
from models.invite import Invite, InviteSchema, invite_schema, invites_schema
from models.outing import Outing, OutingSchema
from models.member import Member, MemberSchema
from models.group import Group, GroupSchema
from init import db

from flask_jwt_extended import jwt_required, get_jwt_identity


invite_bp = Blueprint("invite", __name__, url_prefix="/invite")

def private_invite(outing_id, group_id):
    priv_invite = Invite(
        out_id = outing_id,
        fam_grp_id = group_id
    )
    db.session.add(priv_invite)
    db.session.commit()
    response = "A private invitation for your family group only has been created."
    return response

@invite_bp.route("/public", methods= ["POST"])
@jwt_required()
def public_invite():
    body_data = InviteSchema().load(request.get_json())
    stmt = db.select(Member).filter_by(member_id = get_jwt_identity())
    member = db.session.scalar(stmt)

    pub_invite = Invite(
        out_id = body_data.get("outing_id"),
        fam_grp_id = body_data.get("group_id"),
        member_id = member.member_id
    )
    if member.is_admin and member:
        db.session.add(pub_invite)
        db.session.commit()
        
        return {
            "A public invitation for your this outing has been created.": invite_schema.dump(pub_invite)
        }, 200

@invite_bp.route("/private", methods= ["GET"])
@jwt_required()
def private_invites():
    stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
    member = db.session.scalar(stmt)
    stmt2 = db.select(Outing).where(public = False)
    private = db.session.scalar(stmt2)
    stmt3 = db.select(Invite).where(fam_grp_id = member.fam_group_id)
    group_id = db.session.scalar(stmt3)
    if member and private and group_id:
        return {"Your private family group invites": invites_schema.dump(group_id)}, 200
    
@invite_bp.route("/public", methods= ["GET"])
@jwt_required()
def public_invites():
    stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
    member = db.session.scalar(stmt)
    stmt2 = db.select(Outing).where(public = True)
    public = db.session.scalar(stmt2)
    stmt3 = db.select(Invite).where(fam_grp_id = member.fam_group_id)
    group_id = db.session.scalar(stmt3)
    if member and public and group_id:
        return {"Your private family group invites": invites_schema.dump(group_id)}, 200
    




    
    
    
    
    

    



