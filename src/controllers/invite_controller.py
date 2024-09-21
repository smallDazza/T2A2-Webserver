from flask import Blueprint, request
from models.invite import Invite, InviteSchema, invite_schema, invites_schema
from models.outing import Outing, OutingSchema
from models.member import Member, MemberSchema
from models.group import Group, GroupSchema
from init import db

from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError


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
    try:
        body_data = request.get_json()
        outing_id = body_data.get("outing_id")
        group_id = body_data.get("group_id")
        stmt = db.select(Member).filter_by(member_id = get_jwt_identity())
        member = db.session.scalar(stmt)

        if not member:
            return {"Error": "Member not found."}, 404

        pub_invite = Invite(
            out_id = outing_id,
            fam_grp_id = group_id,
            member_id = member.member_id,
            message = body_data.get("message")
        )
        if member.is_admin:
            db.session.add(pub_invite)
            db.session.commit()
            
            return {
                "A public invitation for your outing has been created.": {
                    "The outing id": pub_invite.out_id,
                    "Group id to invite": pub_invite.fam_grp_id,
                    "Your message": pub_invite.message }
            }, 200
        else:
            return {"Error": "You are not an admin and cannot create public invites."}, 401
    except IntegrityError:
        return {"Error": "The outing_id or group_id entered do not exist."}, 404

@invite_bp.route("/private", methods= ["GET"])
@jwt_required()
def private_invites():
    stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
    member = db.session.scalar(stmt)
    stmt2 = db.select(Outing).where(Outing.public == False)
    private = db.session.scalar(stmt2)
    stmt3 = db.select(Invite).where(Invite.fam_grp_id == member.fam_group_id)
    group_id = db.session.scalars(stmt3)
    if member and private and group_id:
        return {"Your private family group invites": invites_schema.dump(group_id)}, 200
    
@invite_bp.route("/public", methods= ["GET"])
@jwt_required()
def public_invites():
    stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
    member = db.session.scalar(stmt)
    stmt2 = db.select(Outing).where(Outing.public == True)
    public = db.session.scalar(stmt2)
    stmt3 = db.select(Invite).where(Invite.fam_grp_id == member.fam_group_id)
    group_id = db.session.scalars(stmt3)
    if member and public and group_id:
        return {"Your public family group invites": invites_schema.dump(group_id)}, 200
    
@invite_bp.route("/response", methods= ["POST"])
@jwt_required()
def invite_response():
    body_data = request.get_json()
    if all(body_data.get(field) for field in ["outing_id", "family_group_id", "accept_invite"]):
# Proceed if these 3 fields are present.
        pass
    else:
        return {"Error": "Some fields are missing or empty = outing_id, family_group_id & accept_invite must have data entered."}, 404
    stmt = db.select(Member).filter_by(member_id = get_jwt_identity())
    member = db.session.scalar(stmt)

    accept = Invite(
        out_id = body_data.get("outing_id"),
        fam_grp_id = body_data.get("family_group_id"),
        accept_invite = body_data.get("accept_invite"),
        message = body_data.get("message"),
        member_id = member.member_id
    )
    if member:
        db.session.add(accept)
        db.session.commit()
        return {
            "Invitation Response": invite_schema.dump(accept)
        }, 200




    
    
    
    
    

    



