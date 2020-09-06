import os
import secrets
import functools
from PIL import Image
from flask import render_template, url_for,flash,redirect, request,abort
from Flask_attempts.models import User,Post
from Flask_attempts.Wtforms import RegistrationForm, LoginForm, PostForm,UpdateForm
from Flask_attempts import app,db,bcrypt
from flask_login import login_user,logout_user, current_user, login_required




@app.route("/")
@app.route("/home")
def home():
    try:
        posts = Post.query.order_by(Post.date_posted.desc()).all()
        return render_template('html Hello World.html',posts=posts)
    except:
        return render_template('html Hello World.html')

@app.route("/about")
def about():
    return render_template('about page.html')

@app.route("/registration",methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account Is Ready, {form.username.data}!You can now Log in!','success')
        return redirect(url_for('Login'))
    return render_template('register.html', title='Register', form = form)

@app.route("/Login",methods = ['GET','POST'])
def Login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.memory.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'Login Error,No Account found with this combination of Email and Password,please try again','danger')           
    return render_template('login.html', title='Login', form = form)

@app.route("/Logout")
def Logout():
    logout_user()
    return redirect(url_for('home'))




def image_transpose_exif(im):
    """
    Apply Image.transpose to ensure 0th row of pixels is at the visual
    top of the image, and 0th column is the visual left-hand side.
    Return the original image if unable to determine the orientation.

    As per CIPA DC-008-2012, the orientation field contains an integer,
    1 through 8. Other values are reserved.

    Parameters
    ----------
    im: PIL.Image
       The image to be rotated.
    """

    exif_orientation_tag = 0x0112
    exif_transpose_sequences = [                   # Val  0th row  0th col
        [],                                        #  0    (reserved)
        [],                                        #  1   top      left
        [Image.FLIP_LEFT_RIGHT],                   #  2   top      right
        [Image.ROTATE_180],                        #  3   bottom   right
        [Image.FLIP_TOP_BOTTOM],                   #  4   bottom   left
        [Image.FLIP_LEFT_RIGHT, Image.ROTATE_90],  #  5   left     top
        [Image.ROTATE_270],                        #  6   right    top
        [Image.FLIP_TOP_BOTTOM, Image.ROTATE_90],  #  7   right    bottom
        [Image.ROTATE_90],                         #  8   left     bottom
    ]

    try:
        seq = exif_transpose_sequences[im._getexif()[exif_orientation_tag]]
    except Exception:
        return im
    else:
        return functools.reduce(type(im).transpose, seq, im)




def save_pic(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext=os.path.splitext(form_picture.filename)
    picture_fn = random_hex+f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)
    
    new_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(new_size)
    image_transpose_exif(i).save(picture_path)
    return picture_fn




@app.route("/account",methods = ['GET','POST'])
@login_required
def Account():
    form = UpdateForm()
    if form.validate_on_submit():
        if form.prof_pic.data:
            prof_pic_file = save_pic(form.prof_pic.data)
            previous_pic = current_user.image_file
            current_user.image_file = prof_pic_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Update Saved!",'success')
       # if previous_pic!="default.jpg":   auti itan mia mikro e3upnada gia diagrafi tis palias foto tou xristi apo to database otan autos 8a allaze prof_pic, den douleuei sto heroku giati den vlepei to directory
        #   # print(previous_pic)            Ostoso to heroku kanei ka8e toso clear cache opote tipota kainourgio den "menei",mikro to kako,apla itan wraio pou douleue locally
        #    os.remove(url_for('static',filename = "profile_pics/"+ previous_pic))
        return redirect(url_for('Account')) # den 8es na peseis sto return giati dimiourgei neo post request sto server kai egkumonei xaos
    elif request.method =='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file= url_for('static',filename = "profile_pics/"+ current_user.image_file)
    return render_template('account.html',title='Account', image_file=image_file, form = form)


@app.route("/post/new",methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content = form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash("Content Posted Succesfully!",'success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title = 'New Post',form=form,legend = 'New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id) #i fernei to template tou post i fernei 404 doesnt exist page
    return render_template('post.html',title=post.title,post=post)

@app.route("/post/<int:post_id>/edit",methods=['GET','POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403) #http error code for forbidden path
    form = PostForm()
    if form.validate_on_submit():
        post.title= form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post Updated Successfully!",'success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html',title='Edit Post',
                               form=form, legend='Edit Post')


@app.route("/post/<int:post_id>/delete",methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post is no longer part of the website','success')
    return redirect(url_for('home'))






