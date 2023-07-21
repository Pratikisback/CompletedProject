from datetime import datetime, timedelta
import jwt
from flask import make_response, jsonify, request, Blueprint
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
import bcrypt
from app import api, Resource
from app.register.controller import add_user, find_user, update_Verify, update_password, remove_user, \
    show_user_details,check_email_password
from app.register.utils import send_emails
from app.celery_config.celery_task import *
from celery import shared_task

User_Registration_Blueprint = Blueprint("Register_User", __name__)


class Register(Resource):
    def post(self):
        try:
            email = request.json.get("email")
            username = request.json.get("username")
            password = request.json.get("password")
            encoded_password = password.encode()
            hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt(5))
            is_verified = False
            role = "Admin"
            new_user = {"email": email, "username": username, "password": hashed_password,
                        "is_verified": is_verified, "role": role}
            if not new_user:
                return make_response(jsonify({"message": "fill in the details"}))

            existing_user = find_user(email)
            if existing_user:
                return make_response(jsonify({"message": "user already exists"}))
            try:
                token_expire_time = datetime.now() + timedelta(minutes=15)
                token_expire_time_epoch = int(token_expire_time.timestamp())

                payload = {"email": email, "exp": token_expire_time_epoch}
                print(payload)
                token = jwt.encode(payload, "zanc", algorithm="HS256")
                print(token)
                a = add_user(new_user)
                print(a)
                if a:
                    result_from_task = send_emails.apply_async(args=[email,token],countdown=3)
                    return make_response(jsonify({"message": "user registered successfully"}))
                else:
                    return make_response(jsonify({"message": "email not found"}))


                # if send_emails(email, token):
                #     return make_response(jsonify({"message": "user registered successfully"}))
                # else:
                #     return make_response(jsonify({"message": "email not found"}))

            except Exception as e:
                return make_response(jsonify({"message": str(e)}))

        except Exception as e:
            return make_response(jsonify({"message": str(e)}))


class VerifyTheEmail(Resource):
    def get(self):
        try:
            # token = request.headers.get("authentication_key")
            token = request.args.get('token')

            if token:
                token_dict = jwt.decode(token, "zanc", algorithms=["HS256"])
                email = token_dict[
                    "email"]  # We get the whole dictionary in token dict containing the email and the epoch time,
                # but we only need the email
                email_db = find_user(
                    email)  # Here we get the whole info on the email in db , to get the email we took the email from
                # the dictionary
                print(email)
                if email == email_db["email"]:
                    a = update_Verify(email)
                    print(a)
                return make_response(jsonify({"message": "Your account has been verified"}))
        except Exception as e:
            return make_response(jsonify({'message': str(e)}))
        return make_response(jsonify({"message": "updated"}))


class Login(Resource):

    def post(self):
        # Credentials from API

        email = request.json.get("email")
        password = request.json.get("password")
        encoded_password = password.encode()

        # print(hashed_password)
        # Info from db as the dictionary will be returned in infodb we fetch the required values from the infodb for
        # validation
        infodb = find_user(email)
        if infodb in [None, " "]:
            return make_response(jsonify({'message': "user not found or the password is wrong "}))
        emaildb = infodb["email"]
        passworddb = infodb["password"]
        print(passworddb)
        is_verified = infodb["is_verified"]

        if is_verified:
            if email == emaildb and bcrypt.checkpw(encoded_password, passworddb):
                access_token = create_access_token(identity=email, expires_delta=timedelta(minutes=15))
                refresh_token = create_refresh_token(identity=email, expires_delta=timedelta(days=30))
                return make_response(jsonify({"message": "You have logged in succesfully",
                                              "access_token": access_token,
                                              "refresh_token": refresh_token}))
            else:
                return make_response(jsonify({"Message": "Invalid credentials"}))
        else:
            return make_response(jsonify({"Message": "Your account is not verified"}))


class UpdateInfo(Resource):
    @jwt_required()
    def post(self):

        email = get_jwt_identity()
        current_password = request.json.get("current_password")
        current_encoded_password = current_password.encode()

        new_password = request.json.get("new_password")
        encoded_password = new_password.encode()
        new_hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())

        info_db = find_user(email)
        passworddb = info_db["password"]
        if info_db["is_verified"]:
            if bcrypt.checkpw(current_encoded_password, passworddb):
                update_password(email, new_hashed_password)
                return make_response(jsonify({"message": "password updated successfully"}))
            else:
                return make_response(jsonify({"message": "your password does not match with the current password"}))
        else:
            return make_response(jsonify({"message": "your account is not verified"}))


class RemoveUser(Resource):
    @jwt_required()
    def post(self):
        email = get_jwt_identity()
        password = request.json.get("password").encode()

        info_db = check_email_password(email,password)
        user_details = find_user(email)
        role = user_details["role"]
        # password_db = info_db["password"]
        # print(password_db)
        # print(hashed_password)
        if role == "Admin":
            if info_db:
                remove_user(email)
                return make_response(jsonify({"message": "user has been deleted successfully and you cannot login "
                                                         "from this account now"}))
            else:
                return make_response(jsonify({"message": "invalid credentials"}))
        else:
            return make_response(jsonify({"message": "you don't have the authority to delete account"}))


class Details(Resource):
    def get(self, email):
        username = None
        if email:
            email_info = show_user_details(email)
            username = email_info["username"]
        return make_response(jsonify({"message": "your details are as follow",
                                      "email": email,
                                      "username": username}))


class Default(Resource):
    def get(self):
        return make_response(jsonify({"Message": "Success"}))


api.add_resource(Default, "/")
api.add_resource(Details, '/details/<email>')
api.add_resource(VerifyTheEmail, '/verify')
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(UpdateInfo, '/updatepassword')
api.add_resource(RemoveUser, '/deleteuser')
