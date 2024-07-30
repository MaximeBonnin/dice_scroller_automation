from flask import Flask, render_template, request, redirect, url_for
from translate import translate, translate_logger, delete_log_file
import logging

delete_log_file()
app = Flask(__name__)
translate_logger.info("App started. Ready to serve requests")


def handle_input(request):
    srch = request.form["srch"]
    translate_logger.info(f"URL to translate: {srch}")
    translate(srch)
    return render_template("index.html")


@app.route("/", methods=['GET', "POST"])
def index():
    if request.method == "POST":
        return handle_input(request)

    return render_template("index.html")


@app.route("/log", methods=["GET"])
def get_log():
    with open("app.log", "r") as logfile:
        log_list = logfile.readlines()
        filtered_logs = [l for l in log_list if "translate" in l]
    return render_template("log.html", log=filtered_logs)


if __name__ == "__main__":
    print(f"Starting...")
    app.run(debug=True)