import os
import re

SECRET_KEY = os.getenv("SECRET_KEY", "not-set")

# When deploying, set in the environment to the PostgreSQL URL
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///db.sqlite3"
)
