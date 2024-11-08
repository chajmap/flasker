from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config["SECRET_KEY"] ="my super secret key"

# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

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