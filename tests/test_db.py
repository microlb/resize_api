import unittest
from application import app, db
from application.models import User, Tasks


class TestDB(unittest.TestCase):
    '''Тесы базы данных'''
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user(self):
        u1 = User(username='Valera', password='1234')
        u2 = User(username='Tom', password='12')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        user1 = User.query.filter(User.username == 'Valera').first()
        user2 = User.query.filter(User.username == 'Tom', User.password == '12').first()
        self.assertEqual(user1.username, 'Valera')
        self.assertEqual(user1.password, '1234')
        self.assertEqual(user2.username, 'Tom')

    def test_task(self):
        user_id = 4
        name_pic = 'apple'
        height = 100
        width = 100
        done = False
        identifier = '123456'
        t1 = Tasks(user_id=user_id,
                   name_pic=name_pic,
                   height=height, width=width,
                   done=done, identifier=identifier)
        db.session.add(t1)
        db.session.commit()
        task = Tasks.query.filter(Tasks.user_id == user_id).first()
        self.assertEqual(task.name_pic, name_pic)
        self.assertEqual(task.height, height)
        self.assertEqual(task.width, width)
        self.assertEqual(task.done, done)
        self.assertEqual(task.identifier, identifier)