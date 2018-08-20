from flask_wtf import Form,FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, SubmitField, TextAreaField, FileField, SelectField, FloatField
from wtforms.validators import Required,Length, NumberRange
from .. import photos
# from . import main
# from ..models import photos  #导入上传集（upload set)

class NameForm(Form):
    name = StringField('What is your name?',validators=[Required()])
    submit = SubmitField('Submit')

class EditProfileForm(Form):
    name = StringField('您的真实姓名', validators=[Length(0,64)])   #表单中所有字段都是可选的，因此长度验证函数允许长度为零。
    location = StringField('个人地址', validators=[Length(0,64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('提交')

# class NewAlbumForm(FlaskForm):
#     title = StringField(u'标题')
#     about = TextAreaField(u'介绍', render_kw={'rows': 8})
#     photo = FileField(u'图片',validators=[
#         FileRequired(u'你还没有选择图片！'),
#         FileAllowed(photos, u'只能上传图片！')
#     ])
#     submit = SubmitField(u'提交')

class UploadForm(FlaskForm):
    photo = FileField(u'请选择图片', validators=[       #设置错误信息
        FileAllowed(photos, u'只能上传图片！'),  #FileAllowed()第一个参数是使用Flask-Uploads设置的set名称，如果不是用Flask-Uploads，可以替换成文件后缀组成的列表，比如['jpg','png']
        FileRequired(u'文件未选择！')])
    submit = SubmitField(u'上传')

class WaterMarkForm(Form):
    text = StringField('添加水印文字', validators=[Required])
    opacity = FloatField('请输入透明度(0-1)',validators=[Required, NumberRange(min=0.00, max=1.00)])
    submit2 = SubmitField('确定')

class DiyfilterForm(FlaskForm):

    photo1 = FileField(u'请选择背景图片', validators=[  # 设置错误信息
        FileAllowed(photos, u'只能上传图片！'),
        # FileAllowed()第一个参数是使用Flask-Uploads设置的set名称，如果不是用Flask-Uploads，可以替换成文件后缀组成的列表，比如['jpg','png']
        FileRequired(u'文件未选择！')])
    photo2 = FileField(u'请选择天空素材图片', validators=[  # 设置错误信息
        FileAllowed(photos, u'只能上传图片！'),
        # FileAllowed()第一个参数是使用Flask-Uploads设置的set名称，如果不是用Flask-Uploads，可以替换成文件后缀组成的列表，比如['jpg','png']
        FileRequired(u'文件未选择！')])
    submit = SubmitField(u'上传')