from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FloatField
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange
)


# --------------------------------
# Registration Form
# --------------------------------
class RegistrationForm(FlaskForm):

    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(min=3, max=100)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    phone = StringField(
        "Phone Number",
        validators=[
            DataRequired(),
            Length(min=10, max=15)
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo(
                "password",
                message="Passwords must match."
            )
        ]
    )

    submit = SubmitField("Create Account")


# --------------------------------
# Login Form
# --------------------------------
class LoginForm(FlaskForm):

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Login")


# --------------------------------
# Deposit Form
# --------------------------------
class DepositForm(FlaskForm):

    amount = FloatField(
        "Deposit Amount",
        validators=[
            DataRequired(),
            NumberRange(min=1)
        ]
    )

    description = StringField(
        "Description",
        validators=[
            Length(max=100)
        ]
    )

    submit = SubmitField("Deposit Money")


# --------------------------------
# Withdraw Form
# --------------------------------
class WithdrawForm(FlaskForm):

    amount = FloatField(
        "Withdraw Amount",
        validators=[
            DataRequired(),
            NumberRange(min=1)
        ]
    )

    description = StringField(
        "Description",
        validators=[
            Length(max=100)
        ]
    )

    submit = SubmitField("Withdraw Money")


# --------------------------------
# Transfer Form
# --------------------------------
class TransferForm(FlaskForm):

    account_number = StringField(
        "Receiver Account Number",
        validators=[
            DataRequired(),
            Length(min=10, max=20)
        ]
    )

    amount = FloatField(
        "Transfer Amount",
        validators=[
            DataRequired(),
            NumberRange(min=1)
        ]
    )

    description = StringField(
        "Description",
        validators=[
            Length(max=100)
        ]
    )

    submit = SubmitField("Transfer Money")

class EditProfileForm(FlaskForm):

    full_name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=3, max=100)]
    )

    phone = StringField(
        "Phone Number",
        validators=[DataRequired(), Length(min=10, max=15)]
    )

    submit = SubmitField("Update Profile")

class ChangePasswordForm(FlaskForm):

    current_password = PasswordField(
        "Current Password",
        validators=[DataRequired()]
    )

    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )

    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo(
                "new_password",
                message="Passwords must match."
            )
        ]
    )

    submit = SubmitField("Change Password")

class AdminLoginForm(FlaskForm):

    email = StringField(
        "Admin Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Admin Login")