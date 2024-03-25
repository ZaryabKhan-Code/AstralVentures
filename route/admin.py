from model.database import *

admin = Blueprint("admin", __name__)


def generate_token(length=20):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def send_email(sender_email, receiver_email, subject, body):
    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, "tezj txck tvfz irok")
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"Error while sending email: {e}")
        return False


@admin.route("/add_admin", methods=["POST"])
def add_admin_api():
    try:
        data = request.json
        print(data)
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = "admin"

        existing_agent = User.query.filter(
            (User.email == email) | (User.name == name)
        ).first()

        if existing_agent:
            response = {
                "message": "Admin with the same name or Email already exists.",
                "success": False,
            }
            return jsonify(response), 400

        new_admin = User(
            name=name,
            email=email,
            is_active=True,
            role=role,
            password=generate_password_hash(password, method="scrypt"),
        )

        db.session.add(new_admin)
        db.session.commit()

        response = {"message": "Admin added successfully!", "success": True}
        return jsonify(response), 201

    except Exception as e:
        response = {"message": e, "success": False}
        return jsonify(response), 500


@admin.route("/my/portal", methods=["GET", "POST"])
@login_required
def portal():
    if current_user.role == "user":
        return redirect(url_for("user.user_dashboard"))
    user = User.query.all()
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User with provided email already exists.", "warning")
            return redirect(url_for("admin.portal"))

        token = generate_token()
        new_token = Token(email=email, name=name, token=token)
        db.session.add(new_token)
        db.session.commit()

        sender_email = "zk126128@gmail.com"
        receiver_email = email
        subject = "Bot Access"

        email_content = f"""
        Dear {name},

        You have received a tokenized link for accessing the bot:
        {url_for('user.tokenized_link', token=token, _external=True)}

        Best regards,
        Admin
        """
        # Call the send_email function to send the email
        if send_email(sender_email, receiver_email, subject, email_content):
            flash("Email sent successfully!", "success")
        else:
            flash("Failed to send email. Please try again later.", "error")

        return redirect(url_for("admin.portal"))

    return render_template("portal.html", user=user)
