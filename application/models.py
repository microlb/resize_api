from application import db


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))
    tasks = db.relationship('Tasks', backref='tasks')


class Tasks(db.Model):
    __tablename__ = 'tasks'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    name_pic = db.Column(db.String(64))
    pic_base64 = db.Column(db.Text)
    height = db.Column(db.Integer)
    width = db.Column(db.Integer)
    done = db.Column(db.Boolean, default=False)
    identifier = db.Column(db.String(100), unique=True)



