from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid, search 
from .forms import LoginForm,EditForm,PostForm,SearchForm
from .models import User,Post
from datetime import datetime
from config import POSTS_PER_PAGE
from config import MAX_SEARCH_RESULTS
#from .emails import follower_notification
from .email import follower_notification

# index view function suppressed for brevity

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        
        db.session.add(g.user)
        db.session.commit()
        
        g.search_form = SearchForm()

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    else:
        return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    '''
    未解决问题：认证失败，么有提示语显示
    '''    
    print (u'经历过了认证过程...')
    print (resp.email)
    if resp.email is None or resp.email == "":
        print (u'认证失败了')
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(email=resp.email).first()
    
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        
        nickname = User.make_unique_nickname(nickname)
        
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
        
        #make the user follow him/herself
        user.follow(user)
        
        db.session.add(user)
        db.session.commit()
        
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    
    flash(u'Successfully signed in')
    g.user =  user
    return redirect(request.args.get('next') or url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
@login_required
def index(page = 1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, body = form.post.data, timestamp = datetime.utcnow(), author = g.user)
        
        db.session.add(post)
        db.session.commit()
        
        flash('Your post is now live!')
        return redirect(url_for('index'))
    
    #posts = g.user.followed_posts().all()
    #页数，从 1 开始，
    #每一页的项目数，这里也就是说每一页显示的 blog 数，
    #错误标志。如果是 True，当请求的范围页超出范围的话，一个 404 错误将会自动地返回到客户端的网页浏览器。如果是 False，返回一个空列表而不是错误。    
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    
    return render_template('index.html',
        title = 'Home',
        form = form,
        posts = posts)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page = 1):
    '''
    用户信息页¶
    
    创建一个用户信息不需要引入新的概念。我们只要创建一个新的视图函数以及与它配套的 HTML 模版。
    这里就是视图函数(文件 app/views.py):
    '''
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User' + nickname + 'not found')
        return redirect(url_for('index'))
    
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    
    return render_template('user.html', user = user, posts = posts)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        
        db.session.add(g.user)
        db.session.commit()
        
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
        
    return render_template('edit.html', form = form)


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    
    if user == g.user:
        flash("You can\'t follow yourself!")
        return redirect(url_for('user', nickname = nickname))
    
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user',nickname = nickname))
    
    db.session.add(u)
    db.session.commit()
    
    #传过去的是被关注者，关注者（当前用户）
    follower_notification(True,user, g.user)
    
    flash('You are now following ' + nickname + '!')
    return redirect(url_for('user', nickname = nickname))
     

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect (url_for('index'))
    
    if user == g.user:
        flash("You can\'t unfollow yourself!")
        return redirect(url_for('user', nickname = nickname))
    
    db.session.add(user)
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname +'.')
        return redirect(url_for('user', nickname = nickname))

    db.session.add(u)
    db.session.commit()
    
    #传过去的是被关注者，关注者（当前用户）
    follower_notification(False, user, g.user)
    
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname = nickname))


@app.route('/blogs')
@app.route('/blogs/<int:page>')
#@login_required
def blogs(page = 1):
    posts = Post.all_blogs().paginate(page, POSTS_PER_PAGE, False)
    return render_template('blogs.html', posts = posts)


@app.route('/followers/<nickname>')
@login_required
def followers(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    followers = user.followers
    return render_template('followers.html', nickname = nickname ,followers =  followers)

@app.route('/followed/<nickname>')
@login_required
def followed(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    followed = user.followed
    return render_template('followed.html', nickname = nickname ,followed =  followed)

    
@app.route('/search', methods = ['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query = g.search_form.search.data))


@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = Post.query.msearch(query, fields= ['title','body'], limit = 20)
    #print('搜索结果：',results)
    return render_template('search_results.html',
        query = query,
        results = results) 

@app.route('/del_blog/<title>')
@login_required
def del_blog(title):
    results = Post.query.filter_by(title = title).first()
    
    db.session.delete(results)
    db.session.commit()
    
    return redirect(url_for('user', nickname = g.user.nickname))

@app.route('/detail/<title>')
@login_required
def detail(title):
    post = Post.query.filter_by(title = title).first()
    
    return render_template('detail.html', post = post)