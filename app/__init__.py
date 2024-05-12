from flask import Flask, flash, redirect, request, url_for
from flask_login import current_user
from flask_mailman import Mail
from app.admin import AdminIndexView, BlogView
from app.config import Config
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_security import SQLAlchemySessionUserDatastore, Security, hash_password
import logging
from flask_admin import Admin, AdminIndexView as BaseAdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_security.signals import user_registered

from app.database import init_db, db_session
from app.models import Blog, Role, User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mail = Mail(app)

    # Proxy Configuration
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    # manage sessions per request - make sure connections are closed and returned
    app.teardown_appcontext(lambda exc: db_session.close())

    # Setup Flask-Security
    user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
    app.security = Security(app, user_datastore)

    @user_registered.connect_via(app)
    def user_registered_signal_handler(app, user, **kwargs):
        default_role = user_datastore.find_role("user")
        user_datastore.add_role_to_user(user, default_role)
        db_session.commit()

    # Silence passlib logging
    logging.getLogger("passlib").setLevel(logging.ERROR)

    # Admin Configuration
    admin = Admin(
        app, name="flask-blog", template_mode="bootstrap4", index_view=AdminIndexView()
    )

    admin.add_view(ModelView(User, db_session))
    admin.add_view(ModelView(Role, db_session))
    admin.add_view(BlogView(Blog, db_session))

    # Views
    from app.views import views
    from app.auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")

    # Init Database
    with app.app_context():
        init_db()

        # Create a user and role to test with
        app.security.datastore.find_or_create_role(
            name="user", permissions={"user-read", "user-write"}
        )
        app.security.datastore.find_or_create_role(
            name="admin", permissions={"admin-read", "admin-write"}
        )
        db_session.commit()

        if not app.security.datastore.find_user(email="admin@flaskblog.com"):
            app.security.datastore.create_user(
                email="admin@flaskblog.com",
                password=hash_password("password"),
                roles=["admin"],
            )
        db_session.commit()
    return app
