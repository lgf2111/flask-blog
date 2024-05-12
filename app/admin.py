from flask import flash, redirect, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView as BaseAdminIndexView
from flask_login import current_user


class AdminIndexView(BaseAdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("security.login", next=request.url))


class BlogView(ModelView):
    keys = ("title", "subtitle", "content", "user_id")
    column_list = keys
    form_columns = keys
