import os.path
import flask
from flask import Flask,url_for,request,session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin,form
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView,expose
from flask_babelex import Babel
from wtforms import validators



file_path = os.path.abspath(os.path.dirname(__name__))


app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)
babel = Babel(app)
@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'ru')



admin = Admin(app,'my admin_page',template_mode='bootstrap3', url='/')

#for configurate image name
# def thumb_name(filename):
#     name, _ = os.path.splitext(filename)
#     return secure_filename('%s-thumb.jpg' % name)

class Person(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20),nullable=False)
    workouts = db.relationship('Work',backref='user',lazy="dynamic")
    password_hashed = db.Column(db.String(170),nullable=False)
    avatar = db.Column(db.String(70))

    def __repr__(self):
        return '<User %r>' % (self.name)


class PersonView(ModelView):
    column_display_pk = True

    column_list = ['id','name','workouts','password','avatar']

    column_sortable_list = ['id','name']

    can_edit = True
    can_create = True
    can_delete = False
    can_export = True

    form_args = {
        'name': dict(label='Username', validators=[validators.DataRequired()]),
        'workouts': dict(label='Workout train', validators=[validators.DataRequired()]),
        'password': dict(label='pass', validators=[validators.DataRequired()]),
    }
    export_types = ['csv']

    column_descriptions = dict(
        name='First and Last name'
    )
    column_exclude_list = ['password']
    column_searchable_list = ['name']
    column_filters = ['workouts']
    column_editable_list = ['name','workouts']

    create_modal = True
    edit_modal = True

    AVAILABLE_NAME = [
        (u'Admin', u'Admin'),
        (u'Author', u'Author'),
        (u'Redactor', u'Redactor'),
        (u'User', u'User')
    ]

    form_choices = {
        'name':AVAILABLE_NAME,
    }

    def list_thumnail(view,context,model,name):
        if not model.avatar:
            return ''
        image = url_for('static', filename=os.path.join('img/',model.avatar))

        if model.avatar.split('.')[-1] in ['jpeg','jpg','gif','png']:
            return flask.Markup(f'<img src={image} width="100">')



    column_formatters = {
        'avatar': list_thumnail
    }
    form_extra_fields = {
        'avatar': form.ImageUploadField(
            'Image Avatar',
            base_path=os.path.join(file_path,'storage/user_avatar'),
            thumbnail_size=(100,100,True),
            allowed_extensions=['jpg'],
        )
    }

    def get_create_form(self):
        return super(PersonView, self).get_create_form()

    def get_edit_form(self):
        return super(PersonView, self).get_edit_form()

    def create_form(self, obj=None):
        return super(PersonView,self).create_form(obj)

    def edit_form(self, obj=None):
        return super(PersonView,self).edit_form(obj)

class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    bodyweight = db.Column(db.Numeric)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer,db.ForeignKey('person.id'))

    def __repr__(self):
        return '<Work %r>' % (self.id)

class Notification(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/notify.html')


admin.add_view(PersonView(Person,db.session))
admin.add_view(ModelView(Work,db.session))
admin.add_view(Notification(name='notifications',endpoint='notify'))




if __name__ == '__main__':
    app.run(debug=True)
