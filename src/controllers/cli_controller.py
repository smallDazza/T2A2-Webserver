from datetime import date

from flask import Blueprint
from init import db, bcrypt
from models.member import Member
from models.bill import Bill
from models.group import Group
from models.outing import Outing
from models.invite import Invite


db_commands = Blueprint("db", __name__)

@db_commands.cli.command("create")
def setup_tables():
    db.create_all()
    print("database tables have been setup")

@db_commands.cli.command("seed")
def seed_tables():
    groups = [
        Group(
            group_name = "Family Group 1"
        ),
        Group(
            group_name = "Family Group 2"
        )
    ]
    db.session.add_all(groups)
    db.session.flush()

    members = [
        Member(
            name = "Darren Small",
            email = "dazza@email.com",
            is_admin = True,
            username = "Dazza",
            password = bcrypt.generate_password_hash("Dazza1234").decode("utf-8"),
            fam_group_id = groups[0].group_id
        ),
        Member(
            name = "Jayden",
            email = "jay@email.com",
            username = "Jay",
            password = bcrypt.generate_password_hash("Jay1234").decode("utf-8"),
            fam_group_id = groups[0].group_id
        )
    ]
    db.session.add_all(members)
    db.session.flush()

    bills = [
        Bill(
            due_date = date(2024, 11, 15),
            amount = 195.50,
            bill_title = "Sydney water bill",
            description = "Three monthly water bill for home",
            paid = False,
            member_id = members[0].member_id
        ),
        Bill(
            due_date = date(2024, 12, 15),
            amount = 85.00,
            bill_title = "Mobile phone bill",
            description = "Jays mobile phone bill",
            paid = False,
            member_id = members[1].member_id
        )
    ]
    db.session.add_all(bills)
    db.session.flush()

    outings = [
        Outing(
            start_date = date(2024, 12, 14),
            end_date = date(2024, 12, 27),
            title = "Family cruise",
            description = "Criuse from sydney to adelaide, tassie and back.",
            public = True,
            member_id = members[0].member_id
        ),
        Outing(
            start_date = date(2024, 11, 28),
            end_date = date(2024, 11, 28),
            title = "Doctor appointment",
            public = False,
            member_id = members[1].member_id
        )
    ]
    db.session.add_all(outings)
    db.session.flush()

    invites = [
        Invite(
            out_id = outings[0].out_id,
            fam_grp_id = groups[0].group_id,
            member_id = members[0].member_id
        ),
        Invite(
            out_id = outings[0].out_id,
            fam_grp_id = groups[0].group_id,
            member_id = members[1].member_id
        )
    ]
    db.session.add_all(invites)
    db.session.commit()

    print("all tables have been seeded")

@db_commands.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("all tables have been dropped")



