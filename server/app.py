#!/usr/bin/env python3

from models import db, Episode, Guest, Appearance
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Index(Resource):
    def get(self):
        response = make_response({"index": "Code Challenge"}, 200)
        return response

class Episodes(Resource):
    def get(self):
        episodes_dict = [episode.to_dict(rules=('-appearances',)) for episode in Episode.query.all()]
        response = make_response(episodes_dict, 200)
        return response
    
    def post(self):
        pass

class EpisodesByID(Resource):
    def get(self, id):
        episode = Episode.query.filter(Episode.id == id).first()
        if episode == None:
            response = make_response({"error": "Episode not found"}, 404)

        else:
            response = make_response(episode.to_dict(), 200)

        return response
    
    def delete(self, id):
        episode = Episode.query.filter(Episode.id == id).first()
        if episode == None:
            response = make_response({"error": "Episode not found"}, 404)

        else:
            db.session.delete(episode)
            db.session.commit()
            response = make_response({}, 204)

        return response
    


class Guests(Resource):
    def get(self):
        guests_dict = [guest.to_dict(rules=('-appearances',)) for guest in Guest.query.all()]
        response = make_response(guests_dict, 200)
        return response
    
class Appearances(Resource):
    def post(self):
        json = request.get_json()
        try:
            new_appearance = Appearance(
                rating = json["rating"],
                episode_id = json["episode_id"],
                guest_id = json["guest_id"]
            )
            db.session.add(new_appearance)
            db.session.commit()
            response = make_response(new_appearance.to_dict(), 201)
            return response
        except ValueError:
            response = make_response({"errors": ["validation errors"]}, 400)
    


api.add_resource(Index, '/')
api.add_resource(Episodes, '/episodes')
api.add_resource(EpisodesByID, '/episodes/<int:id>')
api.add_resource(Guests, '/guests')
api.add_resource(Appearances, '/appearances')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
