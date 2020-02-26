from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """ todo list user """
    user_id= db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    name2 = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(30), nullable=False)
    last_name2 = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    ip_address = db.Column(db.String(24), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    phone_number = db.Column(db.String(11), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    verified = db.Column(db.Boolean, nullable=False)
    ping = db.Column(db.String(4), nullable=False)
    ads = db.relationship('Ads', backref='user', lazy=True)
    bank = db.relationship('Bank', backref='user', lazy=True)

    def __init__(self, username):
        self.username = username.strip()

class Ad(db.Model):
    """ users to do tasks """
    ad_id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(30), nullable=False)
    buyorsell = db.Column(db.Boolean, nullable=False)
    description = db.Column(db.String(300), nullable=False)
    min_limit = db.Column(db.Integer, nullable=False)
    max_limit = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(10), nullable=False)
    rate = db.Column(db.String(10), nullable=False)
    limit = db.Column(db.Integer, nullable=False)
    picture = db.Column(db.String(10), nullable=False)
    isavailable = db.Column(db.Boolean, nullable=False)
    ad_amount = db.Column(db.Integer, nullable=False)
    bank_ad = db.relationship('Ad_bank', backref='ad', lazy=True)
    user_id1 = db.Column(db.Integer, db.ForeignKey('user.user_id'),
        nullable=False)
    user_id2 = db.Column(db.Integer, db.ForeignKey('user.user_id'),
    nullable=False)

    def __init__(self, label, user_username):
        self.label = label.strip()
        self.user_username = user_username.strip()

    def serialize(self):
        return {
            "label": self.label,
            "done": self.done
        } 

class AdBank(db.Model):
    adbank_id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.ad_id'),
    nullable=False)
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.bank_id'),
    nullable=False)

    # def serialize(self):
    #     return {
    #         "label": self.label,
    #         "done": self.done
    #     } 

class Bank(db.Model):
    """ users to do tasks """
    bank_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), nullable=False)
    bank_ad = db.relationship('Ad_bank', backref='bank', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),
        nullable=False)

    def __init__(self, label, nombre):
        
        self.nombre = nombre.strip()

    # def serialize(self):
    #     return {
    #         "label": self.label,
    #         "done": self.done
    #     } 

class BankAccount(db.Model):
    """ users to do tasks """
    bankaccount_id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), nullable=False, default="sample taks")
    name = db.Column(db.Boolean, default=False)
    

    def __init__(self, label, user_username):
        self.label = label.strip()
        self.user_username = user_username.strip()

    #  def serialize(self):
    #     return {
    #         "label": self.label,
    #         "done": self.done
    #     }         