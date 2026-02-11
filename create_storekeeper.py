# create_storekeeper.py
from werkzeug.security import generate_password_hash
from app import app, db        # adjust if your app/import paths differ
from models import User

USERNAME = "storekeeper"
PASSWORD = "storekeeper123#"
ROLE = "storekeeper"
EMAIL = "storekeeper@example.com"   # change or leave as dummy if email required by model

with app.app_context():
    user = User.query.filter_by(username=USERNAME).first()
    pw_hash = generate_password_hash(PASSWORD, method='sha256')  # matches your register()
    if user:
        user.password = pw_hash
        user.role = ROLE
        # update email only if model requires and it's empty
        if getattr(user, 'email', None) in [None, '']:
            try:
                user.email = EMAIL
            except Exception:
                pass
        db.session.commit()
        print(f"Updated existing user '{USERNAME}'.")
    else:
        new_user = User(
            username=USERNAME,
            password=pw_hash,
            role=ROLE
        )
        # set email if column exists / required
        try:
            new_user.email = EMAIL
        except Exception:
            pass
        db.session.add(new_user)
        db.session.commit()
        print(f"Created user '{USERNAME}' with role '{ROLE}'.")
