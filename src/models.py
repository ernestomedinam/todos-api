from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """ todo list user """
    username = db.Column(db.String(30), primary_key=True)
    todos = db.relationship("Todo", back_populates="user")
    images = db.relationship("UserImage", back_populates="user")

    def __init__(self, username):
        self.username = username.strip()

class Todo(db.Model):
    """ users to do tasks """
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(30), nullable=False, default="sample taks")
    done = db.Column(db.Boolean, default=False)
    user_username = db.Column(db.String(30), db.ForeignKey("user.username"), nullable=False)
    user = db.relationship("User", back_populates="todos")

    def __init__(self, label, user_username):
        self.label = label.strip()
        self.user_username = user_username.strip()

    def serialize(self):
        return {
            "label": self.label,
            "done": self.done
        } 

class UserImage(db.Model):
    """ image uploaded by user """
    __table_args__ = (
        db.UniqueConstraint("title", "user_username", name="unique_img_title_user"),
    )
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    image_url = db.Column(db.String(500), nullable=False, unique=True)
    user_username = db.Column(db.String(30), db.ForeignKey("user.username"), nullable=False)
    user = db.relationship("User", back_populates="images")

    def __init__(self, title, image_url, user_username):
        self.title = title.strip()
        self.image_url = image_url.strip()
        self.user_username = user_username.strip()

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "image_url": self.image_url
        }
