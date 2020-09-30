"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import json
import uuid
from flask import Flask, request, jsonify, url_for, make_response, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db, User, Todo, UserImage
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
import cloudinary.uploader as uploader
#from models import Person

app = Flask(__name__, static_folder="static")
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config.from_mapping(
    CLOUDINARY_URL=os.environ.get("CLOUDINARY_URL")
)
# cloud_config.update = ({
#     "cloud_name": os.environ.get("CLOUD_NAME"),
#     "api_key": os.environ.get("API_KEY"),
#     "api_secret": os.environ.get("API_SECRET")
# })
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
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
    if request.content_type != "application/json":
        return make_response(
            jsonify({
                "result": "this is application/json only endpoint."
            }),
            405,
            headers
        )
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
                # and also delete user images...
                user_images = UserImage.query.filter_by(user_username=username).all()
                for image in user_images:
                    url_parts = image.image_url.rsplit("/", 2)
                    path_filename = "/".join([url_parts[1], url_parts[2]])
                    if os.path.exists(os.path.join(UPLOAD_FOLDER, path_filename)):
                        os.remove(os.path.join(UPLOAD_FOLDER, path_filename))
                        db.session.delete(image)
                db.session.commit()

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
        # and also his images!!
        if len(requesting_user) > 0:
            # user exists, delete records...
            # delete current user tasks...
            # delete current user images...
            user_images = UserImage.query.filter_by(user_username=username).all()
            for image in user_images:
                url_parts = image.image_url.rsplit("/", 2)
                path_filename = "/".join([url_parts[1], url_parts[2]])
                if os.path.exists(os.path.join(UPLOAD_FOLDER, path_filename)):
                    os.remove(os.path.join(UPLOAD_FOLDER, path_filename))
                    db.session.delete(image)
            db.session.commit()

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

# user images endpoint
@app.route("/todos/<username>/images", methods=["POST", "GET"])
@app.route("/todos/<username>/images/<int:id>", methods=["DELETE"])
def handle_user_images(username, id=0):
    """ 
        GET to receive all user images as a list of objects,
        POST to create a new user image.
    """
    headers = {
        "Content-Type": "application/json"
    }
    # check if user exists
    if User.query.filter_by(username=username).first():
        # user exists

        if request.method == "GET":
            # get user images and return them
            user_images = UserImage.query.filter_by(user_username=username).all()
            response_body = []
            if len(user_images) > 0:
                for image in user_images:
                    response_body.append(image.serialize())
                status_code = 200
            else:
                response_body = []
                status_code = 200

        elif request.method == "POST":
            # check if user has less than 5 images stored
            if len(UserImage.query.filter_by(user_username=username).all()) < 5:
                # receive file, secure its name, save it and
                # create object to store title and image_url
                target = os.path.join(UPLOAD_FOLDER, "images")
                if not os.path.isdir(target):
                    os.mkdir(target)
                try:
                    image_file = request.files['file']
                    filename = secure_filename(image_file.filename)
                    extension = filename.rsplit(".", 1)[1]
                    hash_name = uuid.uuid4().hex
                    hashed_filename = ".".join([hash_name, extension])
                    destination = os.path.join(target, hashed_filename)
                    response = uploader.upload(image_file)
                    print(f"{response.items()}")
                    try:
                        new_image = UserImage(request.form.get("title"), response["public_id"], response["secure_url"], username)
                        db.session.add(new_image)

                        try:
                            db.session.commit()
                            response_body = {
                                "result": "HTTP_201_CREATED. image created for user"
                            }
                            status_code = 201
                        except Exception as error:
                            db.session.rollback()
                            response_body = {
                                "result": f"HTTP_400_BAD_REQUEST. {type(error)} {error.args}"
                            }
                            status_code = 400
                    except:
                        db.session.rollback()
                        status_code = 400
                        response_body = {
                            "result": "HTTP_400_BAD_REQUEST. no title in key/value"
                        }
                except Exception as error:
                    status_code = 400
                    response_body = {
                        "result": f"HTTP_400_BAD_REQUEST. {type(error)} {error.args}"
                    }
                
                
            else:
                # user has 5 images uploaded
                response_body = {
                    "result": "HTTP_404_BAD_REQUEST. cannot upload more than five images, please delete one first."
                }
                status_code = 404

        elif request.method == "DELETE":
            # user wants to delete a certain image, check id
            if id != 0 and UserImage.query.filter_by(id=id).first():
                image_to_delete = UserImage.query.filter_by(id=id).first()
                response = uploader.destroy(image_to_delete.public_id)
                if "result" in response and response["result"] == "ok":
                    db.session.delete(image_to_delete)
                    try:
                        db.session.commit()
                        response_body = {
                            "result": "HTTP_204_NO_CONTENT. image deleted."
                        }
                        status_code = 204
                    except Exception as error:
                        db.session.rollback()
                        response_body = {
                            "result": f"HTTP_500_INTERNAL_SERVER_ERROR. {type(error)} {error.args}"
                        }
                else:
                    response_body = {
                        "result": f"HTTP_404_NOT_FOUND. {response['result'] if 'result' in response else 'image not found...'}"
                    }
                    status_code = 404
        else:
            # bad request method...
            response_body = {
                "result": "HTTP_400_BAD_REQUEST. This is not a valid method for this endpoint."
            }
            status_code = 400
    else:
        # user doesn't exist
        response_body = {
            "result": "HTTP_400_BAD_REQUEST. cannot handle images for non existing user..."
        }
        status_code = 400

    return make_response(
        jsonify(response_body),
        status_code,
        headers
    )

# static image file serving
@app.route("/src/static/images/<filename>", methods=["GET"])
def serve_image(filename):
    
    secured_filename = secure_filename(filename)
    image_path = os.path.join("images", secured_filename)
    
    if os.path.exists(os.path.join(app.static_folder, image_path)):
        return send_from_directory(app.static_folder, image_path)
    else:
        return "HTTP_404_NOT_FOUND"

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
