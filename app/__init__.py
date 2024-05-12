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

from datetime import datetime


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
                username="admin",
                password=hash_password("password"),
                roles=["admin"],
            )
        db_session.commit()

        if not db_session.query(Blog).all():
            blogs = [
                Blog(
                    title="Innovate to Thrive: The Power of Business Creativity",
                    subtitle="Unleashing Innovation for Sustainable Growth and Success",
                    content="In today's rapidly evolving business landscape, innovation is not just a buzzword but a necessity for survival. Research underscores the correlation between innovation and long-term business success. Here are actionable insights to foster a culture of creativity within your organization: encourage experimentation, embrace diversity, prioritize customer feedback, empower employees, and foster a growth mindset. By harnessing the power of innovation, businesses can adapt to change, stay ahead of the competition, and thrive in an ever-changing market. Let's embark on a journey of business creativity and unlock new possibilities for growth and prosperity.",
                    created_at=datetime.now(),
                    author=db_session.query(User)
                    .filter(User.email == "admin@flaskblog.com")
                    .first(),
                ),
                Blog(
                    title="Finding Balance: Navigating Work and Life",
                    subtitle="Strategies for a Harmonious and Fulfilling Existence",
                    content="In the modern world, the line between work and life often blurs, leaving us feeling overwhelmed and disconnected. However, achieving balance is not only possible but essential for our well-being. Research highlights the importance of maintaining boundaries and prioritizing self-care. Here are practical tips to reclaim balance: set boundaries, prioritize tasks, schedule downtime, cultivate hobbies, and practice mindfulness. By nurturing equilibrium, we unlock a life of fulfillment and joy, where work and leisure coexist harmoniously. Let's embark on the journey to finding balance and living our best lives.",
                    created_at=datetime.now(),
                    author=db_session.query(User)
                    .filter(User.email == "admin@flaskblog.com")
                    .first(),
                ),
                Blog(
                    title="The Gratitude Advantage",
                    subtitle="Unlocking Happiness and Success Through Thankfulness",
                    content="In the hustle and bustle of modern life, gratitude often goes unnoticed. Yet, it holds immense power to transform our well-being and achievements. Research reveals its profound impact on mental health and productivity. Here are simple ways to integrate gratitude into your daily routine: keep a gratitude journal, express appreciation to loved ones, practice mindfulness, and reframe challenges as opportunities for growth. In a world of challenges, gratitude becomes our guiding light, illuminating the path to happiness and success. Let's cultivate gratitude and reap its abundant rewards.",
                    created_at=datetime.now(),
                    author=db_session.query(User)
                    .filter(User.email == "admin@flaskblog.com")
                    .first(),
                ),
            ]
            db_session.add_all(blogs)
            db_session.commit()
    return app
