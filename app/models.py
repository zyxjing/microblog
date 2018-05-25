from app import db
from hashlib import md5
from werkzeug.security import generate_password_hash,check_password_hash

'''
这是对上面图表上的关系表的直接翻译。
注意我们并没有像对 users 和 posts 一样把它声明为一个模式。
因为这是一个辅助表，我们使用 flask-sqlalchemy 中的低级的 APIs 来创建没有使用关联模式。
'''
followers =  db.Table('followers', 
                      db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                      db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                      )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #nickname = db.Column(db.String(64), index=True, unique=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)    
    followed = db.relationship('User',
                               secondary = followers,
                               primaryjoin = (followers.c.follower_id == id),
                               secondaryjoin = (followers.c.followed_id == id),
                               backref = db.backref('followers',lazy = 'dynamic'),
                               lazy = 'dynamic'
                               )

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False
    
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3
    
    def avatar(self, size):
        '''
            方法 avatar 返回用户图片的 URL，以像素为单位缩放成要求的尺寸。
            有了 Gravatar 服务的协助，很容易处理头像。
            你只需要创建一个用户邮箱的 MD5 哈希，然后将其加入 URL中，像上面你看见的。
            在邮箱 MD5 后，你还需要提供一个定制头像尺寸的数字d=mm 决定什么样的图片占位符,当用户没有 Gravatar 账户,mm 选项将会返回一个“神秘人”图片，一个人灰色的轮廓。
            s=N 选项要求头像按照以像素为单位的给定尺寸缩放。
        '''
        return 'https://www.gravatar.com/avatar/' + md5(self.email.encode('utf-8')).hexdigest() + '?d=mm&s=' + str(size)
    
    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname    
    
    def is_following(self, user):
        '''
        is_following 方法在一行代码中做了很多。
        我们做了一个 followed 关系查询，这个查询返回所有当前用户作为关注者的 (follower, followed) 对。
        '''
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def follow(self, user):
        '''
        关注一个新的用户：判断是否已经关注了这个用户，如果未关注，则关注；已关注，则忽略
        '''
        if not self.is_following(user):
            self.followed.append(user)
            return self
    
    def unfollow(self, user):
        '''
        取消关注一个用户
        '''
        if self.is_following(user):
            self.followed.remove(user)
            return self
    
    def followed_posts(self):
        '''
        查出所有的关注的用户的blog
        '''
        return Post.query.join(followers,(followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())
    
    
    def __repr__(self):
        return '<User %r>' % (self.nickname)
    

class Post(db.Model):
    '''
        用户编写的blog(id,body,timestamp,user_id)
    '''
    __searchable__ = ['title', 'body']
    
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    @staticmethod
    def all_blogs():
        return Post.query
    
    def __repr__(self):
        return '<Post %r>' % (self.body)
