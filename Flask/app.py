import hashlib
import uuid
from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = "mongodb://localhost:27017/"
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
    db = client["flask_db"]
    collection = db["users"]
    todo_collection = db["todos"]
except Exception:
    client = None
    db = None
    collection = None
    todo_collection = None

# In-memory storage fallback if MongoDB is offline
in_memory_todos = []


@app.route("/api", methods=["GET", "POST"])
def form():
    error = None

    if request.method == "POST":
        try:
            name = request.form.get("name")
            email = request.form.get("email")
            skill = request.form.get("skill")

            if not name or not email or not skill:
                error = "All fields are required!"
                return render_template("form.html", error=error)

            if collection is not None:
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
            item_id = data.get("itemId") or data.get("item_id")
            item_uuid = data.get("itemUuid") or data.get("item_uuid") or str(uuid.uuid4())
            item_hash = data.get("itemHash") or data.get("item_hash")
            item_name = data.get("itemName") or data.get("item_name")
            item_description = data.get("itemDescription") or data.get("item_description")
        else:
            item_id = request.form.get("itemId") or request.form.get("item_id")
            item_uuid = request.form.get("itemUuid") or request.form.get("item_uuid") or str(uuid.uuid4())
            item_hash = request.form.get("itemHash") or request.form.get("item_hash")
            item_name = request.form.get("itemName") or request.form.get("item_name")
            item_description = request.form.get("itemDescription") or request.form.get("item_description")

        if not item_hash and (item_id or item_uuid):
            item_hash = hashlib.sha256(f"{item_id}:{item_uuid}".encode()).hexdigest()

        if not item_name or not item_description:
            return jsonify({"error": "Both itemName and itemDescription are required"}), 400

        todo_item = {
            "itemId": item_id,
            "item_id": item_id,
            "itemUuid": item_uuid,
            "item_uuid": item_uuid,
            "itemHash": item_hash,
            "item_hash": item_hash,
            "itemName": item_name,
            "item_name": item_name,
            "itemDescription": item_description,
            "item_description": item_description,
            "completed": False
        }

        try:
            if todo_collection is not None:
                todo_collection.insert_one(todo_item)
        except Exception:
            pass

        in_memory_todos.append(todo_item)

        if request.is_json:
            return jsonify({
                "message": "To-Do item added successfully!",
                "itemId": item_id,
                "itemUuid": item_uuid,
                "itemHash": item_hash,
                "itemName": item_name,
                "itemDescription": item_description
            }), 201
        else:
            return redirect(url_for("todo_page"))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/todo", methods=["GET", "POST"])
def todo_page():
    error = None
    if request.method == "POST":
        item_id = request.form.get("item_id") or request.form.get("itemId")
        item_uuid = request.form.get("item_uuid") or request.form.get("itemUuid") or str(uuid.uuid4())
        item_hash = request.form.get("item_hash") or request.form.get("itemHash")
        if not item_hash and (item_id or item_uuid):
            item_hash = hashlib.sha256(f"{item_id}:{item_uuid}".encode()).hexdigest()
        item_name = request.form.get("item_name") or request.form.get("itemName")
        item_description = request.form.get("item_description") or request.form.get("itemDescription")

        if not item_name or not item_description:
            error = "Both Item Name and Item Description are required!"
        else:
            todo_item = {
                "item_id": item_id,
                "itemId": item_id,
                "item_uuid": item_uuid,
                "itemUuid": item_uuid,
                "item_hash": item_hash,
                "itemHash": item_hash,
                "item_name": item_name,
                "itemName": item_name,
                "item_description": item_description,
                "itemDescription": item_description,
                "completed": False
            }
            try:
                if todo_collection is not None:
                    todo_collection.insert_one(todo_item)
            except Exception:
                pass
            in_memory_todos.append(todo_item)
            return redirect(url_for("todo_page"))

    todos = []
    try:
        if todo_collection is not None:
            todos = list(todo_collection.find({}, {"_id": 0}))
        if not todos:
            todos = in_memory_todos
    except Exception:
        todos = in_memory_todos

    return render_template("todo.html", todos=todos, error=error)


@app.route("/todo/toggle/<int:index>", methods=["POST"])
def toggle_todo(index):
    try:
        if 0 <= index < len(in_memory_todos):
            in_memory_todos[index]["completed"] = not in_memory_todos[index]["completed"]
            if todo_collection is not None:
                item = in_memory_todos[index]
                todo_collection.update_one(
                    {"item_id": item.get("item_id")},
                    {"$set": {"completed": item["completed"]}}
                )
    except Exception:
        pass
    return redirect(url_for("todo_page"))


@app.route("/todo/delete/<int:index>", methods=["POST"])
def delete_todo(index):
    try:
        if 0 <= index < len(in_memory_todos):
            item = in_memory_todos.pop(index)
            if todo_collection is not None:
                todo_collection.delete_one({"item_id": item.get("item_id")})
    except Exception:
        pass
    return redirect(url_for("todo_page"))


if __name__ == "__main__":
    app.run(debug=True)
