from datetime import datetime
from flask import render_template,session,redirect,url_for, flash, abort, request, jsonify
from flask_login import login_required, current_user
from . import main
from . forms import NameForm, EditProfileForm, UploadForm, WaterMarkForm, DiyfilterForm
from .. import db
from .. models import User
from .. import photos
from .methods import add_watermark, skyRegion1, seamClone, myfilter, cartoon_add

@main.route('/',methods=['GET','POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        #...
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form,name=session.get('name'),
                            known=session.get('known',False),
                            current_time=datetime.utcnow())

@main.route('/user/<username>')   #资料页面的路由
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html',user=user)

@main.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('您的个人资料已更新！')
        return redirect(url_for('.user',username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.about_me
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form = form)

@main.route('/image', methods=['GET', 'POST'])
def image():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)  #文件数据不再从request对象获取，而是使用data方法获取
        file_url = photos.url(filename)
    else:
        file_url = None
    return render_template('image.html', form=form, file_url=file_url)

@main.route('/diyfilter', methods=['GET', 'POST'])
def diyfilter():
    form = DiyfilterForm()
    if form.submit.data and form.is_submitted():
            filename = photos.save(form.photo1.data)  # 文件数据不再从request对象获取，而是使用data方法获取
            file_url = '../static/tmp/' + filename

            skyname = photos.save(form.photo2.data)
            sky_url = '../static/tmp/' + skyname

            region = skyRegion1(filename)
            result = seamClone(skyname,filename,region)
    else:
        file_url=None
        sky_url=None
        result = None

    return render_template('diyfilter.html', form=form, file_url=file_url,  sky_url=sky_url, result=result)

@main.route('/filter', methods=['GET', 'POST'])
def filter():
    form = UploadForm()
    if form.is_submitted():
        filename = photos.save(form.photo.data)
        file_url = '../static/tmp/' + filename
    else:
        file_url = None
    return render_template('filter.html',form=form,file_url=file_url)

@main.route('/watermark', methods=['GET', 'POST'])
def watermark():
    form = UploadForm()
    form1 = WaterMarkForm()
    if 'file_url' not in session:
        session['file_url'] = None
    if form1.submit2.data and form1.is_submitted():
        if session['file_url']:
            mark_url = add_watermark(in_file=session['file_url2'], text=form1.text.data, opacity=form1.opacity.data)
            flash('水印添加完成！')
    else:
            mark_url = None


    if form.submit.data and form.is_submitted():
            filename = photos.save(form.photo.data)  # 文件数据不再从request对象获取，而是使用data方法获取
            session['file_url'] = '../static/tmp/' + filename
            session['file_url2'] = filename
            return redirect(url_for('main.watermark'))

    return render_template('watermark.html', form=form, file_url=session['file_url'], form1=form1, mark_url=mark_url)

@main.route('/imgfilter', methods=['GET', 'POST'])
def imgfilter():
    imgId = request.args.get('id')
    img_src = request.args.get('src')
    if imgId:
        filter_name = 'app/static/img/'+'filter'+imgId+'.jpg'
        img_url = myfilter(img_src,filter_name)
        flash('滤镜添加完成！')
    else:
        img_url = None

    res = jsonify({'img_url':img_url})

    return res

@main.route('/cartoon', methods=['GET', 'POST'])
def cartoon():
    form = UploadForm()
    if form.is_submitted():
        filename = photos.save(form.photo.data)
        file_url = '../static/tmp/' + filename
        cartoon_url = cartoon_add(filename)
    else:
        file_url=None
        cartoon_url=None
    return render_template('cartoon.html', form=form, file_url=file_url, cartoon_url=cartoon_url)