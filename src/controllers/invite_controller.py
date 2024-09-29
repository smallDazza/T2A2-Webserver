from flask import Blueprint, request
from models.invite import Invite, InviteSchema, invite_schema, invites_schema
from models.outing import Outing, OutingSchema
from models.member import Member, MemberSchema
from models.group import Group, GroupSchema
from init import db

from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, ProgrammingError, DataError, StatementError
from marshmallow import ValidationError


invite_bp = Blueprint("invite", __name__, url_prefix="/invite")
# this function is called to create a private invite,
# from a new outing being created in out_controller & only if outing.public = false:
def private_invite(outing_id, group_id):
    priv_invite = Invite(
        out_id = outing_id,
        fam_grp_id = group_id
    )
# adds the outing id & family group id, then commits to the invite table in database:
    db.session.add(priv_invite)
    db.session.commit()
# return this response to the out_controller:
    response = "A private invitation for your family group only has been created."
    return response
# this is the route location and method to be used to create a public invite (token required):
@invite_bp.route("/public", methods= ["POST"])
@jwt_required()
def public_invite():
    try:
        body_data = request.get_json()
        outing_id = body_data.get("outing_id")
        group_id = body_data.get("group_id")
        stmt = db.select(Outing).filter_by(out_id = outing_id)
        outing = db.session.scalar(stmt)
        stmt2 = db.select(Member).filter_by(member_id = get_jwt_identity())
        member = db.session.scalar(stmt2)
# if the member with the token does not belong to the same family group as the member that created the outing
# that this invite is going to be for, then display error:
        if outing.member.fam_group_id != member.fam_group_id or outing.public == False:
            return {"Error": "Cannot create a public invite for outings not created by members in your family group or that are private family outings."}, 401

        pub_invite = Invite(
            out_id = outing_id,
            fam_grp_id = group_id,
            member_id = member.member_id,
            invite_message = body_data.get("invite_message")
        )
# member with token must be a admin member to create a invite:
        if member.is_admin:
            db.session.add(pub_invite)
            db.session.commit()
            
            return {
                "A public invitation for your outing has been created.": {
                    "The outing id": pub_invite.out_id,
                    "Group id to invite": pub_invite.fam_grp_id,
                    "Your message": pub_invite.invite_message }
            }, 201
        else:
            return {"Error": "You are not an admin and cannot create public invites."}, 401
    except AttributeError:
        return {"Error": "The outing_id or group_id entered do not exist."}, 404
    except (ProgrammingError, DataError, StatementError):
        return {"Error": "Incorrect field format. Please enter correct format."}, 400
# this is the route location and method to be used to view all invites (token required):
@invite_bp.route("/view", methods= ["GET"])
@jwt_required()
def view_invites():
        try:
            stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
            member = db.session.scalar(stmt)
            group_id = member.fam_group_id
            stmt3 = db.select(Invite).where(Invite.fam_grp_id == group_id)
            invites = db.session.scalars(stmt3).all()
# display all invites where the family group id belongs to same family group id as member with token:
            if member and invites:
                return {"Your family group invites": invites_schema.dump(invites)}, 200
            else:
                return {"No Invites Found": "There are no invites found for your family group"}, 200
        except AttributeError:
            return {"Error": "Invalid token. Cannot view invites"}, 400
    
# this is the route location and method to be used to update a invite (token required):  
@invite_bp.route("/response/<int:invite_id>", methods= ["PUT", "PATCH"])
@jwt_required()
def invite_response(invite_id):
    try:
        body_data = InviteSchema().load(request.get_json(), partial=True)
        
        stmt = db.select(Member).filter_by(member_id=get_jwt_identity())
        member = db.session.scalar(stmt)
        stmt2 = db.select(Invite).filter_by(id = invite_id)
        invite = db.session.scalar(stmt2)
# if the member with token belongs to same family group id as the invite id entered = allow,
# or display error:
        if member.fam_group_id == invite.fam_grp_id:
            pass
        else:
            return {"Error": "The invite id does not belong to your family group. No response allowed."},401

        
# Update the fields if they exist in the json request data, or keep the current values:       
        accept_invite = invite.accept_invite
        response_message = invite.response_message
        if "accept_invite" in body_data:
            accept_invite = body_data.get("accept_invite")
        if "response_message" in body_data:
            response_message = body_data.get("response_message")
            
        invite.accept_invite = accept_invite
        invite.response_message = response_message
# commit the changes to the invite table in database:       
        db.session.commit()
        return {
                "Invitation Response": "Invite fields have been updated"
            }, 200
    except AttributeError:
            return {"Error": "Invalid token. No resonse is allowed."}, 401
    except (ValueError, ValidationError, StatementError):
        return {"Error": "Incorrect field format"}, 400




    
    
    
    
    

    



