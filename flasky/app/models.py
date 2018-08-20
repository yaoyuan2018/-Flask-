from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import  current_app, request
from . import db
from flask_moment import datetime
import hashlib

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

#定义Role和User模型
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff,False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name = r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))                       #用户真实姓名
    location = db.Column(db.String(64))                   #所在地
    about_me = db.Column(db.Text())                       #自我介绍，db.Text()和db.String()的最大区别在于不需要指定最大长度
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  #注册日期
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)      #最后访问时期
    avatar_hash = db.Column(db.String(32))

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)                              #每次收到用户的请求时都要调用ping()方法。由于auth蓝本中的before_app_request处理程序会在每次请求前运行，所以能很轻松地实现这个需求。

    """生成头像"""
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'https://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

    '''检查用户是否有指定的权限'''
    def can(self, permissions):
        return self.role is not None and\
               (self.role.permissions & permissions) == permissions
    def is_administrtor(self):
        return self.can(Permission.ADMINISTER)

    '''检查用户是否有指定的权限'''

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm':self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return '<User %r>' % self.username

class AnonymousUser(AnonymousUserMixin):
        def can(self, permissions):
            return False

        def is_administrator(self):
            return False

login_manager.anonymous_user = AnonymousUser

# class Album(db.Model):
#     __tablename__ = 'albums'
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(64))   #相册标题
#     about = db.Column(db.Text)         #相册信息
#     cover = db.Column(db.String(64))   #相册封面图片url
#     timestam = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     photos = db.relationship('Photo', backref='album', lazy='dynamic')
#
# class Photo(db.Model):
#     __tablename__ = 'photos'
#     id = db.Column(db.Integer, primary_key=True)
#     url = db.Column(db.String(64))   #原图url
#     url_s = db.Column(db.String(64)) #展示图url
#     url_t = db.Column(db.String(64)) #略缩图url
#     aboout = db.Column(db.Text)      #图片介绍
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     album_id = db.Column(db.Integer, db.ForeignKey('albums.id'))
#     comments = db.relationship('Comment',backref='photo', lazy='dynamic')
