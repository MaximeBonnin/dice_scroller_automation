from flask import Flask, render_template, request, url_for, session, redirect
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, set_access_cookies, unset_jwt_cookies
import hashlib
import pandas as pd
import asyncio
from translate import translate, translate_logger, delete_log_file
from tranlation_overview import get_all_posts
from Post import Post
import os

delete_log_file()
app = Flask(__name__)
app.secret_key = os.environ["APP_SECRET_KEY"]
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
jwt = JWTManager(app)

translate_logger.info("App started. Ready to serve requests")


def handle_input(request):
    srch = request.form["srch"]
    translate_logger.info(f"URL to translate: {srch}")
    translate(srch)
    return render_template("index.html")


def load_affiliates():
    df = pd.read_csv("affiliate_links.csv")
    df = df.replace("'", "’", regex=True)
    return df.to_dict("records")


def login_user(email: str, password: str) -> bool:
    encoded_string = f"{email}:{password}".encode(encoding="utf-8")
    encrypted_credentials = hashlib.sha256(encoded_string).hexdigest()
    valid_user = encrypted_credentials == os.environ["USER_CREDS"]
    if valid_user:
        session["email"] = email
        response = redirect(url_for("index"))
        access_token = create_access_token(identity=request.form["Email"])
        set_access_cookies(response=response, encoded_access_token=access_token)
        return response
    else:
        return False


@jwt.unauthorized_loader
def custom_unauthorized_response(_err):
    # TODO log this
    print(_err)
    return redirect(url_for('login'))


@app.route("/", methods=['GET', "POST"])
@jwt_required()
def index():
    if request.method == "POST":
        return handle_input(request)

    url = request.args.get("url", default=None)
    return render_template("index.html", url_to_search = url)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    login_reponse = login_user(email=request.form["Email"], password=request.form["Password"])

    if not login_reponse:
        return render_template("login.html")

    return login_reponse


@app.route("/logout", methods=["GET"])
@jwt_required()
def logout():
    session.pop("email", None)
    response = redirect(url_for("login"))
    unset_jwt_cookies(response)

    return response
    

@app.route("/log", methods=["GET"])
@jwt_required()
def get_log():
    with open("app.log", "r") as logfile:
        log_list = logfile.readlines()
        filtered_logs = [l for l in log_list if "translate" in l]
    return render_template("log.html", log=filtered_logs)


@app.route("/translations", methods=["GET"])
@jwt_required()
def translations():
    return render_template("translations.html")


@app.route("/affiliate", methods=["GET"])
@jwt_required()
def affiliate():
    return render_template("affiliate.html", table=load_affiliates())


@app.route("/translations_table", methods=["GET"])
@jwt_required()
def translations_table():
    list_of_posts: list["Post"] = asyncio.run(get_all_posts()) 

    filtered_list_of_posts = [p for p in list_of_posts if p.language == "de"]

    return render_template("translations_table.html", all_posts = filtered_list_of_posts)


if __name__ == "__main__":
    print("Starting...")
    app.run(debug=True)