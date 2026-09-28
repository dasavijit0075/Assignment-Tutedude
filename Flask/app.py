from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = "mongodb://localhost:27017/"
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
    db = client["flask_db"]
    collection = db["users"]
    todos_collection = db["todos"]
except Exception:
    client = None
    db = None
    collection = None
    todos_collection = None

# In-memory storage fallback if MongoDB is offline
in_memory_todos = []

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


@app.route("/todo", methods=["GET", "POST"])
def todo():
    error = None
    if request.method == "POST":
        item_name = request.form.get("item_name")
        item_description = request.form.get("item_description")

        if not item_name or not item_description:
            error = "Both Item Name and Item Description are required!"
        else:
            todo_item = {
                "item_name": item_name,
                "item_description": item_description,
                "completed": False
            }
            try:
                if todos_collection is not None:
                    todos_collection.insert_one(todo_item)
            except Exception:
                pass
            in_memory_todos.append(todo_item)
            return redirect(url_for("todo"))

    # Fetch tasks
    todos = []
    try:
        if todos_collection is not None:
            todos = list(todos_collection.find({}, {"_id": 0}))
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
            if todos_collection is not None:
                item = in_memory_todos[index]
                todos_collection.update_one(
                    {"item_name": item["item_name"]},
                    {"$set": {"completed": item["completed"]}}
                )
    except Exception:
        pass
    return redirect(url_for("todo"))


@app.route("/todo/delete/<int:index>", methods=["POST"])
def delete_todo(index):
    try:
        if 0 <= index < len(in_memory_todos):
            item = in_memory_todos.pop(index)
            if todos_collection is not None:
                todos_collection.delete_one({"item_name": item["item_name"]})
    except Exception:
        pass
    return redirect(url_for("todo"))


if __name__ == "__main__":
    app.run(debug=True)
