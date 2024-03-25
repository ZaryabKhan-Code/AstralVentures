from model.database import *
from route.auth import *
from route.admin import *
from route.user import *

app = Flask(__name__)

secret_key = secrets.token_hex(16)
app.config["SECRET_KEY"] = secret_key
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_NAME"] = "my_custom_session_cookie"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ZK.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
login_manager.init_app(app)
Session(app)
migrate = Migrate(app, db)
app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(user)


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = (
        "no-cache, no-store, must-revalidate, post-check=0, pre-check=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
