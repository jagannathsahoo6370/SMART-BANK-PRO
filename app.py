from flask import Flask, render_template, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from config import Config
from models import db, User, Account, Transaction
from forms import RegistrationForm, LoginForm, DepositForm, WithdrawForm, TransferForm

import random
import os

app = Flask(__name__)

print("Current Directory:", os.getcwd())
print("App Root:", app.root_path)
print("Template Folder:", app.template_folder)

app.config.from_object(Config)

# -----------------------------
# Flask App Configuration
# -----------------------------
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Extensions
db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please login to access this page."

# Create Database Tables
with app.app_context():
    db.create_all()


# -----------------------------
# Flask-Login User Loader
# -----------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# Register
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = RegistrationForm()

    if form.validate_on_submit():

        # Check email already exists
        existing_user = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_user:
            flash("Email already registered!", "danger")
            return redirect(url_for("register"))

        # Hash Password
        hashed_password = bcrypt.generate_password_hash(
            form.password.data
        ).decode("utf-8")

        # Create User
        new_user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        # Automatically Create Bank Account
        account = Account(
            account_number=str(random.randint(1000000000, 9999999999)),
            user_id=new_user.id
        )

        db.session.add(account)
        db.session.commit()

        flash("Registration Successful! Please login.", "success")

        return redirect(url_for("login"))

    return render_template(
        "register.html",
        form=form
    )


# -----------------------------
# Login
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and bcrypt.check_password_hash(
            user.password,
            form.password.data
        ):

            login_user(user)

            flash("Welcome to SmartBank Pro!", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid Email or Password", "danger")

    return render_template(
        "login.html",
        form=form
    )


# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
@login_required
def dashboard():

    account = current_user.account

    transactions = Transaction.query.filter_by(
        account_id=account.id
    ).all()

    total_deposit = sum(
        t.amount
        for t in transactions
        if t.transaction_type == "Deposit"
    )

    total_withdraw = sum(
        t.amount
        for t in transactions
        if t.transaction_type == "Withdraw"
    )

    total_transfer = sum(
        t.amount
        for t in transactions
        if t.transaction_type == "Transfer"
    )

    recent_transactions = Transaction.query.filter_by(
        account_id=account.id
    ).order_by(
        Transaction.id.desc()
    ).limit(5).all()

    return render_template(
        "dashboard.html",
        account=account,
        total_deposit=total_deposit,
        total_withdraw=total_withdraw,
        total_transfer=total_transfer,
        recent_transactions=recent_transactions
    )

@app.route("/profile")
@login_required
def profile():
    return render_template(
        "profile.html",
        user=current_user
    )

from flask import request
from forms import EditProfileForm
@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():

    form = EditProfileForm()

    if form.validate_on_submit():

        current_user.full_name = form.full_name.data
        current_user.phone = form.phone.data

        db.session.commit()

        flash("Profile updated successfully!", "success")

        return redirect(url_for("profile"))

    if request.method == "GET":
        form.full_name.data = current_user.full_name
        form.phone.data = current_user.phone

    return render_template(
        "edit_profile.html",
        form=form
    )


# -----------------------------
# Deposit Money
# -----------------------------
@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():

    form = DepositForm()

    account = current_user.account

    if form.validate_on_submit():

        amount = form.amount.data

        account.balance += amount

        transaction = Transaction(
            transaction_type="Deposit",
            amount=amount,
            description=form.description.data,
            account_id=account.id
        )

        db.session.add(transaction)
        db.session.commit()

        flash("Money deposited successfully!", "success")

        return redirect(url_for("dashboard"))

    return render_template(
        "deposit.html",
        form=form,
        account=account
    )

@app.route("/withdraw", methods=["GET", "POST"])
@login_required
def withdraw():

    form = WithdrawForm()

    account = current_user.account

    if form.validate_on_submit():

        amount = form.amount.data

        # Check balance
        if amount > account.balance:
            flash("Insufficient Balance!", "danger")
            return redirect(url_for("withdraw"))

        # Update balance
        account.balance -= amount

        # Save transaction
        transaction = Transaction(
            transaction_type="Withdraw",
            amount=amount,
            description=form.description.data,
            account_id=account.id
        )

        db.session.add(transaction)
        db.session.commit()

        flash("Money withdrawn successfully!", "success")

        return redirect(url_for("dashboard"))

    return render_template(
        "withdraw.html",
        form=form,
        account=account
    )

@app.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():

    form = TransferForm()

    sender = current_user.account

    if form.validate_on_submit():

        receiver = Account.query.filter_by(
            account_number=form.account_number.data
        ).first()

        # Receiver doesn't exist
        if receiver is None:
            flash("Receiver account not found!", "danger")
            return redirect(url_for("transfer"))

        # Can't transfer to yourself
        if receiver.id == sender.id:
            flash("You cannot transfer money to your own account!", "danger")
            return redirect(url_for("transfer"))

        amount = form.amount.data

        # Insufficient balance
        if amount > sender.balance:
            flash("Insufficient balance!", "danger")
            return redirect(url_for("transfer"))

        # Update balances
        sender.balance -= amount
        receiver.balance += amount

        # Sender transaction
        sender_transaction = Transaction(
            transaction_type="Transfer",
            amount=amount,
            description=f"To {receiver.account_number} - {form.description.data}",
            account_id=sender.id
        )

        # Receiver transaction
        receiver_transaction = Transaction(
            transaction_type="Received",
            amount=amount,
            description=f"From {sender.account_number} - {form.description.data}",
            account_id=receiver.id
        )

        db.session.add(sender_transaction)
        db.session.add(receiver_transaction)

        db.session.commit()

        flash("Transfer Successful!", "success")

        return redirect(url_for("dashboard"))

    return render_template(
        "transfer.html",
        form=form,
        account=sender
    )


@app.route("/transactions")
@login_required
def transactions():

    transactions = (
        Transaction.query
        .filter_by(account_id=current_user.account.id)
        .order_by(Transaction.timestamp.desc())
        .all()
    )

    return render_template(
        "transactions.html",
        transactions=transactions
    )

# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "info")

    return redirect(url_for("home"))


from forms import ChangePasswordForm
from flask_login import login_required, current_user
from flask import flash, redirect, render_template, request, url_for
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():

    form = ChangePasswordForm()

    if form.validate_on_submit():

        # Check current password
        if not bcrypt.check_password_hash(
            current_user.password,
            form.current_password.data
        ):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("change_password"))

        # Hash the new password
        new_hashed_password = bcrypt.generate_password_hash(
            form.new_password.data
        ).decode("utf-8")

        # Update password
        current_user.password = new_hashed_password

        db.session.commit()

        flash("Password changed successfully!", "success")

        return redirect(url_for("profile"))

    return render_template(
        "change_password.html",
        form=form
    )

from forms import AdminLoginForm
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    form = AdminLoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if (
            user
            and user.is_admin
            and bcrypt.check_password_hash(
                user.password,
                form.password.data
            )
        ):

            login_user(user)

            flash(
                "Welcome Admin!",
                "success"
            )

            return redirect(
                url_for("admin_dashboard")
            )

        flash(
            "Invalid Admin Credentials",
            "danger"
        )

    return render_template(
        "admin_login.html",
        form=form
    )

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if not current_user.is_admin:

        flash("Access Denied!", "danger")

        return redirect(url_for("dashboard"))

    total_users = User.query.count()

    total_accounts = Account.query.count()

    total_transactions = Transaction.query.count()

    total_balance = sum(
        account.balance
        for account in Account.query.all()
    )

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_accounts=total_accounts,
        total_transactions=total_transactions,
        total_balance=total_balance
    )

from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
@app.route("/download_statement")
@login_required
def download_statement():

    account = current_user.account

    transactions = Transaction.query.filter_by(
        account_id=account.id
    ).all()

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("<b>SMARTBANK PRO</b>", styles["Title"]))
    elements.append(Paragraph(f"Account Holder: {current_user.full_name}", styles["Normal"]))
    elements.append(Paragraph(f"Email: {current_user.email}", styles["Normal"]))
    elements.append(Paragraph(f"Account Number: {account.account_number}", styles["Normal"]))
    elements.append(Paragraph(f"Current Balance: ₹{account.balance:.2f}", styles["Normal"]))
    elements.append(Paragraph("<br/>", styles["Normal"]))

    data = [["Type", "Amount", "Description"]]

    for t in transactions:
        data.append([
            t.transaction_type,
            f"₹{t.amount:.2f}",
            t.description if t.description else "-"
        ])

    table = Table(data, colWidths=[2*inch, 1.5*inch, 3*inch])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,1), (-1,-1), colors.beige),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Bank_Statement.pdf",
        mimetype="application/pdf"
    )

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)