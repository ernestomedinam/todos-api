"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import json
from flask import Flask, request, jsonify, url_for, make_response
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db, User, Todo
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "hello": "world"
    }

    return jsonify(response_body), 200

# Todo endpoint!
@app.route("/todos/<username>/", methods=["GET", "POST", "PUT", "DELETE"])
def handle_todos(username):
    headers = {
        "Content-Type": "application/json"
    }
    # check if user exists.
    requesting_user = User.query.filter_by(username=username).all()
    # user is requesting todos or user creation and sample todo.
    if request.method == "GET":
        print("hello, working!")
        if len(requesting_user) > 0:
            # user exists, returning list of todos...
            print("user exists")
            user_todo_list = Todo.query.filter_by(user_username=username).all()
            response_body = []
            for todo in user_todo_list:
                response_body.append(todo.serialize())
            status_code = 200

        else:
            # user does not exist, returning 404 NOT FOUND
            print("user does not exist")
            response_body = {
                "status": "HTTP_404_NOT_FOUND. User does not exist"
            }
            status_code = 404

    # user to be created, check if exists first...
    elif request.method == "POST":
        print("creating user with sample task")

        if len(requesting_user) > 0:
            # user exists, this is a no go...
            response_body = {
                "status": "HTTP_400_BAD_REQUEST. User cannot be created again..."
            }
            status_code = 400

        else:
            # username not in use, create user with sample task...
            print("creating user with this username and a sample task")
            new_user = User(username)
            db.session.add(new_user)
            sample_todo = Todo("sample task", username)
            db.session.add(sample_todo)
            db.session.commit()
            response_body = {
                "status": "HTTP_200_OK. Ok"
            }
            status_code = 200

    elif request.method == "PUT":
        # user wants to refresh full list, check if user exists first...
        print(f"updating full list for {username}")

        if len(requesting_user) > 0:
            # user exists, updating whole list...
            # delete current user tasks...
            Todo.query.filter_by(user_username=username).delete()
            # this jsonifies request.data, returns a list
            # equivalent to new_tasks = request.json
            new_tasks = json.loads(request.data)

            # check update request task list is not empty
            if len(new_tasks) > 0:
                # task list to update is not empty
                for task in new_tasks:
                    # task["user_username"] = username
                    new_task = Todo(task["label"], username)
                    db.session.add(new_task)

                result = f"A list with {len(new_tasks)} todos was succesfully saved"

            else:
                # task list to update is empty, delete user and create no task...
                User.query.filter_by(username=username).delete()
                
                result = f"User has no tasks left, account was deleted."
            
            db.session.commit()
            response_body = {
                "result": result,
                "status": "HTTP_200_OK."
            }
            status_code = 200

        else: 
            # user does not exist, this is a no go...
            response_body = {
                "status": "HTTP_400_BAD_REQUEST. Cannot update task's list for non existing user..."
            }
            status_code = 400

    elif request.method == "DELETE":
        # user wants to delete his list and user registry...
        if len(requesting_user) > 0:
            # user exists, delete records...
            # delete current user tasks...
            Todo.query.filter_by(user_username=username).delete()
            User.query.filter_by(username=username).delete()
            db.session.commit()
            response_body = {
                "result": "ok",
                "status": "HTTP_204_NO_CONTENT. User and tasks deleted."
            }
            status_code = 204

        else:
            # user does not exist, this is a no go...
            response_body = {
                "status": "HTTP_400_BAD_REQUEST. Cannot delete a non existing user..."
            }
            status_code = 400

    else:
        response_body = "method is not ready for testing yet"
        status_code = 501

    return make_response(
        jsonify(response_body),
        status_code,
        headers
    )

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
