from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)

db = client["flask_db"]
collection = db["users"]
todo_collection = db["todos"]

@app.route("/api", methods=["GET", "POST"])
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


@app.route("/submittodoitem", methods=["POST"])
def submit_todo_item():
    try:
        if request.is_json:
            data = request.get_json()
            item_name = data.get("itemName")
            item_description = data.get("itemDescription")
        else:
            item_name = request.form.get("itemName")
            item_description = request.form.get("itemDescription")

        if not item_name or not item_description:
            return jsonify({"error": "Both itemName and itemDescription are required"}), 400

        result = todo_collection.insert_one({
            "itemName": item_name,
            "itemDescription": item_description
        })

        return jsonify({
            "message": "To-Do item added successfully!",
            "id": str(result.inserted_id),
            "itemName": item_name,
            "itemDescription": item_description
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/todo", methods=["GET"])
def todo_page():
    todos = list(todo_collection.find({}, {"_id": 0}))
    return render_template("todo.html", todos=todos)


if __name__ == "__main__":
    app.run(debug=True)