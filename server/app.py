#!/usr/bin/env python3
from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User, UserSchema

# Create schema instance
user_schema = UserSchema()


class ClearSession(Resource):

    def delete(self):

        session['page_views'] = None
        session['user_id'] = None

        return {}, 204


# SIGNUP
class Signup(Resource):

    def post(self):

        data = request.get_json()

        try:
            user = User(
                username=data['username']
            )

            # Hash password
            user.password_hash = data['password']

            db.session.add(user)
            db.session.commit()

            # Log user in
            session['user_id'] = user.id

            return user_schema.dump(user), 201

        except Exception as e:
            return {"error": str(e)}, 422


# CHECK SESSION
class CheckSession(Resource):

    def get(self):

        user_id = session.get('user_id')

        if user_id:

            user = User.query.filter_by(id=user_id).first()

            if user:
                return user_schema.dump(user), 200

        return {}, 204


# LOGIN
class Login(Resource):

    def post(self):

        data = request.get_json()

        user = User.query.filter_by(
            username=data['username']
        ).first()

        if user and user.authenticate(data['password']):

            session['user_id'] = user.id

            return user_schema.dump(user), 200

        return {"error": "Unauthorized"}, 401


# LOGOUT
class Logout(Resource):

    def delete(self):

        session['user_id'] = None

        return {}, 204


# Routes
api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')


if __name__ == '__main__':
    app.run(port=5555, debug=True)