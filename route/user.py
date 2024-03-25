from model.database import *

user = Blueprint("user", __name__)


@user.route("/my/chat_bot", methods=["GET", "POST"])
@login_required
def user_dashboard():
    if current_user.role == "admin":
        return redirect(url_for("admin.portal"))
    return render_template("success.html")


@user.route("/tokenized_link/<token>", methods=["GET", "POST"])
def tokenized_link(token):
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin.portal"))
        else:
            return redirect(url_for("user.user_dashboard"))
    try:
        token_obj = Token.query.filter_by(token=token).first()
        print(token_obj)
        if token_obj:
            email = token_obj.email
            user = User.query.filter_by(email=email).first()
            if user:
                print("user exists")
                if user.is_active:
                    print("user is active")
                    return redirect(url_for("auth.login"))
                else:
                    return redirect(url_for("user.signup_post", token=token))
            else:
                return redirect(url_for("user.signup_post", token=token))
        else:
            return render_template("error.html")
    except Exception as e:
        print(e)
        return render_template("error.html")


@user.route("/signup", methods=["POST", "GET"])
def signup_post():
    token = request.args.get("token")
    email = None

    if token:
        token_obj = Token.query.filter_by(token=token).first()
        if token_obj:
            user = User.query.filter_by(email=token_obj.email).first()
            if user and user.is_active:
                flash("You're already signed up. Please log in.", "info")
                return redirect(url_for("auth.login"))
            email = token_obj.email

    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        password = request.form.get("password")
        organization = request.form.get("organization")
        designation = request.form.get("designation")
        name = first_name + " " + last_name
        points = 0

        if all([first_name, last_name, email, password, organization, designation]):
            points = 5
        elif all([first_name, last_name, email, password]):
            points = 2

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password, method="scrypt"),
            is_active=True,
            organization=organization,
            designation=designation,
            points=points,
        )
        db.session.add(new_user)
        db.session.commit()
        flash(f"You earned {points} points for signing up!", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html", token=token, email=email)


def get_chat_history(user_id, workflow):
    chat_logs = ChatbotMemory.query.filter_by(user_id=user_id, workflow=workflow).all()
    chat_history = ""
    for log in chat_logs:
        chat_history += log.content + "\n"
        chat_history += log.content + "\n"
    return chat_history


def get_chat_limit(user_id):
    chat_limit = ChatbotMemory.query.filter_by(user_id=user_id).count()
    return chat_limit


openai.api_key = "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"


@user.route("/submit", methods=["POST"])
def submit():
    user_input = request.form["user_input"]
    user_id = request.form["user_id"]
    workflow = "HTML"

    user = User.query.filter_by(email=user_id).first()

    user_chat_history = ChatbotMemory.query.filter_by(
        user_id=user_id, speaker="user"
    ).count()
    if user_chat_history >= user.points:
        return "Your point limit has been exceeded. You cannot submit more requests at this time."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}],
    )

    bot_response = response.choices[0].message.content

    # Log user input and bot response
    chat_log_user = ChatbotMemory(
        user_id=user_id,
        workflow=workflow,
        speaker="user",
        content=user_input,
    )
    db.session.add(chat_log_user)

    chat_log_bot = ChatbotMemory(
        user_id=user_id,
        workflow=workflow,
        speaker="bot",
        content=bot_response,
    )
    db.session.add(chat_log_bot)

    db.session.commit()

    return bot_response


@user.route("/update_user", methods=["POST"])
def update_user():
    user_id = request.form.get("userId")
    name = request.form.get("name")
    email = request.form.get("email")
    points = request.form.get("points")
    user = User.query.get(user_id)
    if user:
        user.name = name
        user.email = email
        user.points = points
        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200
    return jsonify({"error": "User not found"}), 404


@user.route("/delete_user", methods=["POST"])
def delete_user():
    user_id = request.form.get("userId")
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    return jsonify({"error": "User not found"}), 404


@user.route("/get_user", methods=["GET"])
def get_user():
    user_id = request.args.get("userId")
    user = User.query.get(user_id)
    if user:
        return jsonify(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "points": user.points,
            }
        )
    return jsonify({}), 404
