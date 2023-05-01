from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView,expose

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)


admin = Admin(app,'my admin_page',template_mode='bootstrap3', url='/')


class Person(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))
    workouts = db.relationship('Work',backref='user',lazy="dynamic")

    def __repr__(self):
        return '<User %r>' % (self.name)

class PersonView(ModelView):
    forms = ['id', 'name', 'workout']

class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    bodyweight = db.Column(db.Numeric)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer,db.ForeignKey('person.id'))

    def __repr__(self):
        return '<User %r>' % (self.id)

class Notification(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/notify.html')


admin.add_view(PersonView(Person,db.session))
admin.add_view(ModelView(Work,db.session))
admin.add_view(Notification(name='notifications',endpoint='notify'))

if __name__ == '__main__':
    app.run(debug=True)
