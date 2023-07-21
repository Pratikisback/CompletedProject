from app.register.views import User_Registration_Blueprint
from flask import Blueprint
from app import app

app.register_blueprint(User_Registration_Blueprint)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")