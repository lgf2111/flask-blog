from flask import flash, redirect, render_template, blueprints, request, url_for
from flask_login import current_user
from flask_security import auth_required
from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField
from app.models import Blog
from app.database import db_session
from wtforms.validators import DataRequired
from datetime import datetime

views = blueprints.Blueprint("views", __name__)


@views.route("/")
@auth_required()
def home():
    blogs = db_session.query(Blog).all()
    return render_template("views/home.html", blogs=blogs)


@views.route("/user")
@auth_required()
def user_home():
    return render_template("Hello {{ current_user.email }} you are a user!")


@views.route("/blog/create", methods=["GET", "POST"])
@auth_required()
def create_blog():
    class CreateBlogForm(Form):
        title = StringField("Title", validators=[DataRequired()])
        subtitle = StringField("Subtitle", validators=[DataRequired()])
        content = TextAreaField("Content", validators=[DataRequired()])
        submit = SubmitField("Submit")

    form = CreateBlogForm(request.form)

    if request.method == "POST" and form.validate():
        blog = Blog(
            title=form.title.data,
            subtitle=form.subtitle.data,
            content=form.content.data,
            created_at=datetime.now(),
            author=current_user,
        )
        db_session.add(blog)
        db_session.commit()
        flash("Your blog has been created!", "success")
        return redirect(url_for("views.home"))

    return render_template("views/create_blog.html", create_blog_form=form)
