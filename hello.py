from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

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

# Create the model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    institution = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Create a string
    def __repr__(self):
        return "<Name %r>" % self.name

# Create a Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    institution = StringField("Institution")
    submit = SubmitField("Submit")

# Update Database Record
@app.route("/update/<int:id>",methods=["GET","POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.institution = request.form["institution"]

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

# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data,institution=form.institution.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.email.data = ""
        form.institution.data = ""
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


if __name__== "__main__":
    app.run(debug=True)

# to update changes to GIT
# git add .
# git commit -am "comments added"
# git push