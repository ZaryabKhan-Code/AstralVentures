from model.database import *

auth = Blueprint("auth", __name__)
login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(agent_id: int):
    return db.session.query(User).get(agent_id)


@auth.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin.portal"))
        else:
            return redirect(url_for("user.user_dashboard"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print(email)
        print(password)
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == "admin":
                return redirect(url_for("admin.portal"))
            else:
                return redirect(url_for("user.user_dashboard"))
    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    logout_user()
    return redirect(url_for("auth.login"))
