# This file is for unit testing of the application
#!flask/bin/python
import os
import unittest
from datetime import datetime, timedelta
from silverhorse.models import User, Post
from silverhorse import create_app, db


basedir = os.path.abspath(os.path.dirname(__file__))


app = create_app()
app.app_context().push()


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        #     os.path.join(basedir, 'site.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_follow(self):
        u1 = User(username='john', email='john@example.com',
                  password='password')
        u2 = User(username='susan', email='susan@example.com',
                  password='password')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert u1.unfollow(u2) is None
        u = u1.follow(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.follow(u2) is None
        assert u1.is_following(u2)
        assert u1.followed.count() == 1
        assert u1.followed.first().username == 'susan'
        assert u2.followers.count() == 1
        assert u2.followers.first().username == 'john'
        u = u1.unfollow(u2)
        assert u is not None
        db.session.add(u)
        db.session.commit()
        assert not u1.is_following(u2)
        assert u1.followed.count() == 0
        assert u2.followers.count() == 0

    def test_follow_posts(self):
        # make four users
        u1 = User(username='john', email='john@example.com',
                  password='password')
        u2 = User(username='susan', email='susan@example.com',
                  password='password')
        u3 = User(username='mary', email='mary@example.com',
                  password='password')
        u4 = User(username='david', email='david@example.com',
                  password='password')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        # make four posts
        utcnow = datetime.utcnow()
        p1 = Post(title='post1', content="post from john", author=u1)
        p2 = Post(title='post2', content="post from susan", author=u2)
        p3 = Post(title='post3', content="post from mary", author=u3)
        p4 = Post(title='post4', content="post from david", author=u4)
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.commit()
        # setup the followers
        u1.follow(u1)  # john follows himself
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u2)  # susan follows herself
        u2.follow(u3)  # susan follows mary
        u3.follow(u3)  # mary follows herself
        u3.follow(u4)  # mary follows david
        u4.follow(u4)  # david follows himself
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        db.session.commit()
        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        assert len(f1) == 3
        assert len(f2) == 2
        assert len(f3) == 2
        assert len(f4) == 1
        assert f1 == [p4, p2, p1]
        assert f2 == [p3, p2]
        assert f3 == [p4, p3]
        assert f4 == [p4]

    def test_who_is_following_who(self):
        user = User(username='john', email='john@example.com',
                    password='password')
        db.session.add(user)
        db.session.commit()
        user.follow(user)
        db.session.add(user)
        db.session.commit()
        assert user.is_following(user) == True


if __name__ == '__main__':
    unittest.main()
