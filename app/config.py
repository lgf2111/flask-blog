import os


class Config:
    DEBUG = os.environ.get("DEBUG", False)

    # Generate a nice key using secrets.token_urlsafe()
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "zobMWBXvwf9Byp6tR456LXhXx3QDKL2tg1aF8VdRAuU"
    )

    # Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
    # Generate a good salt using: secrets.SystemRandom().getrandbits(128)
    SECURITY_PASSWORD_SALT = os.environ.get(
        "SECURITY_PASSWORD_SALT", 196371843893757062036268117248830453616
    )

    # Don't worry if email has findable domain
    SECURITY_EMAIL_VALIDATOR_ARGS = {"check_deliverability": False}

    # Mail Configuration
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # Auth Configuration
    SECURITY_REGISTERABLE = True
    SECURITY_USERNAME_ENABLE = True
    SECURITY_REGISTER_URL = "/auth/register"
    SECURITY_LOGIN_URL = "/auth/login"
    SECURITY_LOGOUT_URL = "/auth/logout"
    SECURITY_POST_REGISTER_VIEW = "/auth/register/success"
    SECURITY_POST_LOGIN_VIEW = "/auth/login/success"
    SECURITY_POST_LOGOUT_VIEW = "/auth/logout/success"
