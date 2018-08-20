from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from ..models import User
from . import auth
from .forms import LoginForm, RegistrationForm
from app import db
from ..email import send_email
import os
import shutil

@auth.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():                                     #若表单在POST请求中提交时，validate_on_submit()函数会验证表单数据，然后尝试登入用户
        user = User.query.filter_by(email=form.email.data).first()    #根据表单中填写的email从数据库中加载用户。如果电子邮件对应的用户存在，再调用verify_password()方法，其参数是表单中填写的密码
        if user is not None and user.verify_password(form.password.data):   #如果密码正确，则调用Flask-Login中的login_user()函数，在用户会话中把用户标记为已登录
            login_user(user, form.remember_me.data)                         #login_user()函数的参数是要登录的用户，以及可选的“记住我”布尔值，“记住我”也在表单中填写。如果值为False，那么关闭浏览器后用户会话就会过期，所以下次用户访问时要重新登录。如果值为True，那么会在用户浏览器中写入一个长期有效的cookie，使用这个cookie可以复现用户会话。
            return redirect(request.args.get('next') or url_for('main.index')) #提交登录密令的POST请求最后也做了重定向，不过目标URL有两种可能。用户访问未授权的URL时会显示登录表单，Flask-Login会把原地址保存在查询字符串的next参数中，这个参数可以从request.args字典中读取。如果查询字符串中没有next参数，则重定向到首页。
        flash('无效的用户名或密码.')                         #如果用户输入的电子邮件或密码不正确，程序会设定一个Flash消息，再次渲染表单，让用户重试登录

    dir_path = 'app/static/tmp'
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
        os.makedirs(dir_path)

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()            #删除并重设用户会话
    flash('您已退出登录！')   #显示一个flash消息，确认这次操作
    return redirect(url_for('main.index'))  #重定向到首页

@auth.route('/register', methods=['GET', 'POST'])     #用户注册路由
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data,password=form.password.data)
        db.session.add(user)
        """"发送验证邮件"""
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email,'请确认您的账户','auth/email/confirm',user=user, token=token)
        flash('一封信息验证邮件已经发送至您的账户！')
        """发送验证邮件"""
        # flash('您现在可以进行登录了！')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您已经确认了您的账户，十分感谢！')
    else:
        flash('您的链接已经失效或过期')
    return redirect(url_for('main.index'))
"""处理程序中过滤未确认的账户"""
# @auth.before_app_request
# def before_request():
#     if current_user.is_authenticated \
#         and not current_user.confirmed \
#         and request.endpoint[:5] !='auth.' \
#         and request.endpoint != 'static':
#       return redirect(url_for('auth.unconfirmed'))
#
# @auth.route('/unconfirmed')
# def unconfirmed():
#     if current_user.is_anonymous or current_user.confirmed:
#         return redirect(url_for('main.index'))
#     return render_template('auth/unconfirmed.html')
"""处理程序中过滤未确认过的账户"""
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '请确认您的账户','auth/email/confirm',user=current_user,token=token)
    flash('一封新的信息验证邮件已发送至您的账户.')
    return redirect(url_for('main.index'))

@auth.before_app_request        #更新已登录用户的访问时间
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        # if not current_user.confirmed \
        #     and request.endpoint[:5] != 'auth.':
        #     return redirect(url_for('auth.unconfirmed'))

