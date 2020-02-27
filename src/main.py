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
from models import db


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

@app.route('/casacadena/submit_register/', methods=['POST', 'GET'])
def handle_submit_register():
    email_from_register_form = request.form['register_email']
    username_from_register_form = request.form['register_username']
    cedula_from_register_form = request.form['register_document_id']
    password_from_register_form = request.form['register_password']
    city_from_register_form = request.form['register_city']
    headers = {
        "Content-Type": "application/json"
    }
    # check if user exists.
    requesting_user = User.query.filter_by(email=email_from_register_form).one_or_none()

    # user is requesting todos or user creation and sample todo.
    if request.method == "POST":
        print("hello, working!")
        if len(requesting_user) > 0:
            # user exists, this is a no go...
            response_body = {
                "status": "HTTP_400_BAD_REQUEST. User cannot be created again..."
            }
            status_code = 400

        else:
            # user does not exist, creating succesfully
            document_id_from_register_form = request.form['register_document_id']
            name_from_register_form = request.form['register_name']
            name2_from_register_form = request.form['register_name2']
            last_name_from_register_form = request.form['register_last_name']
            last_name2_from_register_form = request.form['register_last']
            username_from_register_form = request.form['register_username']
            password_from_register_form = request.form['register_password']
            phone_number_from_register_form = request.form['register_phone_number']
            city_from_register_form = request.form['register_city']


            print("creating user with this username")
            new_user = User(username)
            db.session.add(new_user)
           
            
            
            db.session.commit()

            response_body = {
                "status": "HTTP_201_OK. Ok"
            }
            status_code = 201


    return jsonify(response_body), status_code

@app.route('/casacadena/submit_signin', methods=['POST', 'GET'])
def handle_submit_signin():
    email_from_form = request.form['signin_email']
    headers = {
        "Content-Type": "application/json"
    }
    # check if user exists.
    requesting_email = User.query.filter_by(email=email_from_form).one_or_none()
    
    if len(requesting_email) > 0:
        password_from_signin_form = request.form['signin_password']
        if password_from_signin_form == requesting_email.password:
            response_body = {
                'id':requesting_email.id,
                'username':requesting_email.username,
                'email':requesting_email.email,
                'authentic':true
            }
            status_code = 200
        else:
            response_body = {
                "status": "HTTP_400_BAD_REQUEST. Username and password doesn't match..."
            }
            status_code = 400

    return jsonify(response_body), status_code

    # user is requesting todos or user creation and sample todo.
    if request.method == "POST":
        print("hello, working!")
        if len() > 0:
            # user exists and password is correct, send user id...
            response_body = {
                "status": "HTTP_400_BAD_REQUEST. User cannot be created again..."
            }
            status_code = 400

        else:
              # user does not exist, creating succesfully
            
            print("creating user with this username")
            new_user = User(username)
            db.session.add(new_user)
            
            
            db.session.commit()
            response_body = {
                "status": "HTTP_200_OK. Ok"
            }
            status_code = 200

    

    return jsonify(response_body), 200













# Todo endpoint!
@app.route("/todos/<username>", methods=["GET", "POST", "PUT", "DELETE"])
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
            # user exists, this is a no go...
            response_body = {
                "status": "HTTP_400_BAD_REQUEST. User cannot be created again..."
            }
            status_code = 400

        else:
            # user does not exist, creating succesfully
            
            print("creating user with this username")
            new_user = User(username)
            db.session.add(new_user)
            
            
            db.session.commit()
            response_body = {
                "status": "HTTP_200_OK. Ok"
            }
            status_code = 200

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
            new_tasks = json.loads(request.data)
            
            for task in new_tasks:
                # task["user_username"] = username
                new_task = Todo(task["label"], username)
                db.session.add(new_task)

            db.session.commit()
            result = f"A list with {len(new_tasks)} todos was succesfully saved"
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
