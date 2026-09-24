from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)

db = client["flask_db"]
collection = db["users"]

@app.route("/", methods=["GET", "POST"])
def form():
    error = None

    if request.method == "POST":
        try:
            name = request.form["name"]
            email = request.form["email"]
            skill = request.form["skill"]

            if not name or not email or not skill:
                error = "All fields are required!"
                return render_template("form.html", error=error)

            collection.insert_one({
                "name": name,
                "email": email,
                "skill": skill
            })

            return redirect(url_for("success"))

        except Exception as e:
            error = str(e)

    return render_template("form.html", error=error)


@app.route("/success")
def success():
    return render_template("success.html")


if __name__ == "__main__":
    app.run(debug=True)