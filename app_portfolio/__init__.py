import os
import random
import re
from datetime import datetime

from flask import Flask, render_template, url_for
from flask_admin import Admin, form
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup

from app_portfolio.blog.blueprint import blog
from config import DevelopementConfig


app = Flask(__name__, template_folder='templates', static_folder='static')

app.config.from_object(DevelopementConfig)
db = SQLAlchemy(app)
app.register_blueprint(blog, url_prefix='/blog')
migrate = Migrate(app, db)


def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)


###################  Models #################

post_tags = db.Table('post_tags',
                     db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
                     )


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(140), unique=True)
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)

    def __repr__(self):
        return f'{self.title}'


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(140), unique=True)
    body = db.Column(db.Text)
    code = db.Column(db.Text, nullable=True)
    created = db.Column(db.DateTime, default=datetime.now())
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    photo = db.relationship('PhotoModel', backref='post', uselist=False)
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)

    def __repr__(self):
        return f'{self.title}'


class PhotoModel(db.Model):
    __tablename__ = 'photomodels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))
    type = db.Column(db.Unicode(3))
    create_date = db.Column(db.DateTime, default=datetime.now)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)

    def __repr__(self):
        return f'{self.name}'


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    slug = db.Column(db.String(100), unique=True)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.name:
            self.slug = slugify(self.name)

    def __repr__(self):
        return f'{self.name}'


class PhotoAdminModel(ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        url = url_for('static', filename=os.path.join('storage/', model.path))

        if model.type in ['jpg', 'jpeg', 'png', 'svg', 'gif']:
            return Markup('<img src="%s" width="100">' % url)

        if model.type in ['mp3']:
            return Markup('<audio controls="controls"><source src="%s" type="audio/mpeg" /></audio>' % url)

    column_formatters = {
        'path': _list_thumbnail
    }
    form_extra_fields = {
        'file': form.FileUploadField('file', base_path=app.config['STORAGE'])
    }

    def _change_path_data(self, _form):
        try:
            storage_file = _form.file.data

            if storage_file is not None:
                hash = random.getrandbits(128)
                ext = storage_file.filename.split('.')[-1]
                path = '%s.%s' % (hash, ext)

                storage_file.save(
                    os.path.join(app.config['STORAGE'], path)
                )

                _form.name.data = _form.name.data or storage_file.filename
                _form.path.data = path
                _form.type.data = ext

                del _form.file

        except Exception as ex:
            pass

        return _form

    def edit_form(self, obj=None):
        return self._change_path_data(
            super(PhotoAdminModel, self).edit_form(obj)
        )

    def create_form(self, obj=None):
        return self._change_path_data(
            super(PhotoAdminModel, self).create_form(obj)
        )

# end Models

# Admin panel


admin = Admin(app, name='MyPortfolio', template_mode='bootstrap3')
admin.add_view(ModelView(Tag, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(PhotoAdminModel(PhotoModel, db.session))


from app_portfolio import views
