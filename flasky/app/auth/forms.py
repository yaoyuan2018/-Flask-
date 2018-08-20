from flask_wtf import Form, FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, TextAreaField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, DataRequired
from wtforms import ValidationError
from flask_wtf.file import FileField,FileAllowed,FileRequired
from ..models import User

class LoginForm(Form):
    email = StringField('您的邮箱', validators=[Required(message= u'密码不能为空'), Length(1,64), Email(message=u'请输入有效的地址，比如username@domain.com')], render_kw={"placeholder": "请输入邮箱地址，如example@domain.com",})
    password = PasswordField('密码', validators=[Required()],render_kw={"placeholder": "请输入密码",})
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(Form):
    email= StringField('您的邮箱', validators=[Required(), Length(1,64), Email()])
    username = StringField('用户名', validators=[Required(), Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'用户名必须包含一个以上字符,''数字，"."，或下划线')])
    password = PasswordField('密码', validators=[Required(),EqualTo('password2',message='两次密码必须一致。')])
    password2 = PasswordField('再次确认密码', validators=[Required()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册！')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在！')

class CommentForm(Form):
    name = StringField('', validators=[Length(0, 64)], render_kw={"placeholder": "Your name",
                                                                  "style": "background: url(/static/login-locked-icon.png) no-repeat 15px center;text-indent: 28px"})
    email = StringField('', description='* We\'ll never share your email with anyone else.', validators= \
        [DataRequired(), Length(4, 64), Email(message=u"邮件格式有误")], render_kw={"placeholder": "E-mail: yourname@example.com"})
    comment = TextAreaField('', description=u"请提出宝贵意见和建议", validators=[DataRequired()],
                            render_kw = {"placeholder": "Input your comments here"})
    submit = SubmitField(u'提交')