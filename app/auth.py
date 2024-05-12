from flask import blueprints, flash, redirect, url_for

auth = blueprints.Blueprint("auth", __name__)


@auth.route("/register/success")
def register_success():
    flash("You have successfully registered!", "success")
    return redirect(url_for("views.home"))


@auth.route("/login/success")
def login_success():
    flash("You have successfully logged in!", "success")
    return redirect(url_for("views.home"))


@auth.route("/logout/success")
def logout_success():
    flash("You have successfully logged out!", "success")
    return redirect(url_for("views.home"))
