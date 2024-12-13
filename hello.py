from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm

# Flask instance
app = Flask(__name__)
app.config["SECRET_KEY"] ="my super secret key"
# Add Database
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
# MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root@/users"
# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Create a Login Page
@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successful!")
                return redirect(url_for("dashboard"))
            else:
                flash("Wrong Password, Try Again!")
        else:
            flash("User doesn't exist, Try Again!")

    return render_template("login.html", form=form)

# Create a Logout Page
@app.route("/logout", methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!")
    return redirect(url_for("login"))


# Create a Dashboard Page
@app.route("/dashboard", methods=["GET","POST"])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.institution = request.form["institution"]
        name_to_update.username = request.form["username"]

        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash("Error! Looks like there was a problem... Try again?")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template("dashboard.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)
    return render_template("dashboard.html")


@app.route("/posts/delete/<int:id>")
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()

        flash("Blog Post Was Deleted!") 

        posts = Posts.query.order_by(Posts.date_posted)   
        return render_template("posts.html", posts=posts)
    
    except:
        flash("There was a problem deleting the post. Please, try again!")
        
        posts = Posts.query.order_by(Posts.date_posted)   
        return render_template("posts.html", posts=posts)


@app.route("/posts")
def posts():
    # Grab all the posts
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

@app.route("/posts/edit/<int:id>", methods=["GET","POST"])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        #post.author = form.author.data
        post.slug = form.slug.data
        #post.author = form.author.data
        # Update db
        db.session.add(post)
        db.session.commit()
        flash("Post has Been Updated!")
        return redirect(url_for("post", id=post.id))
    form.title.data = post.title
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template("edit_post.html", form=form)

# Add Post Page
@app.route("/add-post", methods=["GET","POST"])
#@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster= current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
        # Clear The Form
        form.title.data = ""
        form.content.data = ""
        #form.author.data = ""
        form.slug.data = ""

        # Add post data to db
        db.session.add(post)
        db.session.commit()

        # Return a message
        flash("Blog Post Submitted Successfully!")

    # Redirect to the webpage
    return render_template("add_post.html",form=form)
        
# Update Database Record
@app.route("/update/<int:id>",methods=["GET","POST"])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.institution = request.form["institution"]
        name_to_update.username = request.form["username"]

        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash("Error! Looks like there was a problem... Try again?")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template("update.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)

 # Delete Database Record
@app.route("/delete/<int:id>")
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html", 
            form=form,
            name=name,
            our_users=our_users)
    except:            
        flash("Error! Looks like there was a problem... Try again?")
        return render_template("add_user.html", 
            form=form,
            name=name,
            our_users=our_users)

#with app.app_context():
#        db.create_all()

@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # hash the password
            hashed_pw=generate_password_hash(form.password_hash.data, "pbkdf2:sha256")
            user = Users(name=form.name.data, 
                         username=form.username.data,
                         email=form.email.data,
                         institution=form.institution.data, 
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.username.data = ""
        form.email.data = ""
        form.institution.data = ""
        form.password_hash.data = ""
        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", 
        form=form,
        name=name,
        our_users=our_users)
        
@app.route("/")

def index():
    first_name = "Petr"
    fav_pizza = ["4formaggi","provolone","funghi"]
    return render_template("index.html",
                           first_name=first_name,
                           fav_pizza=fav_pizza)

@app.route("/user/<name>")
def user(name):
    return render_template("user.html",user_name=name)

@app.route("/name", methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = " "
        flash("Form Submitted Succesfully!")
    return render_template("name.html", name = name, form = form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# Create Password Test Page
@app.route("/test_pw", methods=["GET", "POST"])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = " "
        form.password_hash.data = " "
        # Lookup user
        pw_to_check = Users.query.filter_by(email=email).first()
        # Check hash pw
        passed = check_password_hash(pw_to_check.password_hash,
                            password)

    return render_template("test_pw.html", 
                           email = email, 
                           password = password,
                           pw_to_check = pw_to_check,
                           passed = passed,
                           form = form)


# Create the model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    institution = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Passwords
    password_hash = db.Column(db.String(128))
    # User can have many posts
    posts = db.relationship("Posts", backref="poster")


    @ property
    def password(self):
        raise AttributeError("password is not a readable attribute")
    
    @ password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a string
    def __repr__(self):
        return "<Name %r>" % self.name

# Create a Blog Post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # create a foreign key
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))


if __name__== "__main__":
    app.run(debug=True)

# to update changes to GIT
# git add .
# git commit -am "comments added"
# git push