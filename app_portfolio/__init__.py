from datetime import datetime

from flask import Flask, redirect, url_for, request
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_migrate import Migrate
from flask_security import SQLAlchemyUserDatastore, Security, RoleMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from config import DevelopementConfig


app = Flask(__name__, template_folder='templates', static_folder='static')
csrf = CSRFProtect(app)

app.config.from_object(DevelopementConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


###################  Models #################

class Signup(db.Model):
    __tablename__ = 'signups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256))
    subject = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    message = db.Column(db.Text(1000))

    def __str__(self):
        return self.email


class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))

    def __str__(self):
        return self.email



roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
                       )


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

# end Models

###########  Flask Security ##################
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Admin panel
class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))


class HomeAdminView(AdminMixin, AdminIndexView):
    pass


admin = Admin(app, 'MyPortfolio', url='/', index_view=HomeAdminView())
admin.add_view(ModelView(Signup, db.session))
admin.add_view(ModelView(Subscriber, db.session))

from app_portfolio import views
