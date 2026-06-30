from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    phone = db.Column(db.String(15), nullable=False)

    password = db.Column(db.String(255), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)



    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    account = db.relationship(
        "Account",
        backref="owner",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)

    account_number = db.Column(db.String(20), unique=True)

    account_type = db.Column(
        db.String(30),
        default="Savings"
    )

    balance = db.Column(
        db.Float,
        default=0.0
    )

    ifsc_code = db.Column(
        db.String(20),
        default="SBIN0001234"
    )

    branch = db.Column(
        db.String(100),
        default="Main Branch"
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    transactions = db.relationship(
        "Transaction",
        backref="account",
        cascade="all, delete-orphan"
    )


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)

    transaction_type = db.Column(db.String(20))

    amount = db.Column(db.Float)

    description = db.Column(db.String(200))

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    account_id = db.Column(
        db.Integer,
        db.ForeignKey("accounts.id")
    )