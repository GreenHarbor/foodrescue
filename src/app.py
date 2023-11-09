"""
Food rescue API with Flask and SQLAlchemy.
"""
# import socket
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import math
import amqp_setup
import pika
import json

app = Flask(__name__)

if os.environ.get('stage') == "test":
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'db_conn') + '/foodrescue'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size': 100,
                                           'pool_recycle': 280}

db = SQLAlchemy(app)

CORS(app)
# pylint: disable=too-many-instance-attributes, too-many-arguments
# pylint: disable= invalid-name, too-few-public-methods


class FoodRescue(db.Model):
    """Food rescue post model."""
    __tablename__ = 'foodrescue'

    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    dateposted = db.Column(db.DateTime, nullable=False)
    datefrom = db.Column(db.DateTime, nullable=False)
    dateto = db.Column(db.DateTime, nullable=False)
    coordinate_long = db.Column(db.String(64), nullable=False)
    coordinate_lat = db.Column(db.String(64), nullable=False)
    location = db.Column(db.String(64), nullable=False)
    foodtype = db.Column(db.String(64), nullable=False)
    verified = db.Column(db.Boolean, nullable=False)

    def __init__(self, title, description, dateposted, datefrom,
                 dateto, coordinate_long, coordinate_lat, location,
                 foodtype, verified):
        self.title = title
        self.description = description
        self.dateposted = dateposted
        self.datefrom = datefrom
        self.dateto = dateto
        self.coordinate_long = coordinate_long
        self.coordinate_lat = coordinate_lat
        self.location = location
        self.foodtype = foodtype
        self.verified = verified

    def to_dict(self):
        data = {
            'post_id': self.post_id,
            'title': self.title,
            'description': self.description,
            'dateposted': self.dateposted,
            'datefrom': self.datefrom,
            'dateto': self.dateto,
            'coordinate_long': self.coordinate_long,
            'coordinate_lat': self.coordinate_lat,
            'location': self.location,
            'foodtype': self.foodtype,
            'verified': self.verified,
        }
        if hasattr(self, 'distance'):
            data['distance'] = self.distance

        return data


@app.route("/health")
def health_check():
    # hostname = socket.gethostname()
    # local_ip = socket.gethostbyname(hostname)

    return jsonify(
        {
            "message": "Service is healthy. (3)",
            "service:": "food-rescue"
        }
    ), 200


@app.route("/posts")
def get_all():
    posts = FoodRescue.query.all()

    if posts:
        return jsonify({
            "data": {
                "posts": [post.to_dict() for post in posts]
            }
        }), 200

    return jsonify({
        "message": "There are no posts."
    }), 404


@app.route("/posts/<int:post_id>")
def find_by_id(post_id):

    post = db.session.scalars(
        db.select(FoodRescue).
        filter_by(post_id=post_id).
        limit(1)
    ).first()

    if post:
        return jsonify({
            "data": post.to_dict()
        }), 200

    return jsonify(
        {
            "message": "Post not found."
        }
    ), 404


@app.route("/posts", methods=['POST'])
def new_post():
    try:
        data = request.get_json()

        post = FoodRescue(**data)
        db.session.add(post)
        db.session.commit()
        j = post.to_dict()
        j['datefrom'] = data['datefrom']
        j['dateposted'] = data['dateposted']
        j['dateto'] = data['dateto']
    except Exception as e:
        return jsonify({
            "message": "An error occurred creating the post.",
            "error": str(e)
        }), 500

    connection = pika.BlockingConnection(amqp_setup.parameters)

    channel = connection.channel()
    channel.basic_publish(
        exchange=amqp_setup.exchange_name, routing_key="foodrescue_post.*",
        body=json.dumps(j),
        properties=pika.BasicProperties(delivery_mode=2))

    connection.close()

    return jsonify({
        "data": post.to_dict()
    }), 201


@app.route("/posts/<int:post_id>", methods=['PUT'])
def replace_post(post_id):

    post = db.session.scalars(
        db.select(FoodRescue).
        filter_by(post_id=post_id).
        limit(1)
    ).first()

    if post is None:
        return jsonify({
            "message": "Post not found."
        }), 404

    data = request.get_json()

    if all(key in data.keys() for
           key in ('title', 'description', 'dateposted', 'datefrom',
                   'dateto', 'coordinate_long', 'coordinate_lat', 'location',
                   'foodtype', 'verified')):
        post.title = data['title']
        post.description = data['description']
        post.dateposted = data['dateposted']
        post.datefrom = data['datefrom']
        post.dateto = data['dateto']
        post.coordinate_long = data['coordinate_long']
        post.coordinate_lat = data['coordinate_lat']
        post.location = data['location']
        post.foodtype = data['foodtype']
        post.verified = data['verified']

        try:
            db.session.commit()
        except Exception as e:
            return jsonify(
                {
                    "message": "An error occurred replacing the post.",
                    "error": str(e)
                }
            ), 500
        return jsonify(
            {
                "data": post.to_dict()
            }
        ), 200
    return jsonify(
        {
            "message": "An error occurred replacing the post.",
            "error": "Keys are missing from the JSON object. " + " Consider HTTP PATCH instead."
        }
    ), 500


@app.route("/posts/<int:post_id>", methods=['PATCH'])
def update_post(post_id):
    post = db.session.scalars(
        db.select(FoodRescue).
        with_for_update(of=FoodRescue).
        filter_by(post_id=post_id).
        limit(1)
    ).first()
    if post is None:
        return jsonify(
            {
                "data": {
                    "post_id": post_id
                },
                "message": "Post not found."
            }
        ), 404
    data = request.get_json()

    if 'title' in data.keys():
        post.title = data['title']
    if 'description' in data.keys():
        post.description = data['description']
    if 'dateposted' in data.keys():
        post.dateposted = data['dateposted']
    if 'datefrom' in data.keys():
        post.datefrom = data['datefrom']
    if 'dateto' in data.keys():
        post.dateto = data['dateto']
    if 'coordinate_long' in data.keys():
        post.coordinate_long = data['coordinate_long']
    if 'coordinate_lat' in data.keys():
        post.coordinate_lat = data['coordinate_lat']
    if 'location' in data.keys():
        post.location = data['location']
    if 'foodtype' in data.keys():
        post.foodtype = data['foodtype']
    if 'verified' in data.keys():
        post.verified = data['verified']
    try:
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred updating the post.",
                "error": str(e)
            }
        ), 500
    return jsonify(
        {
            "data": post.to_dict()
        }
    ), 200


@app.route("/posts/<int:post_id>", methods=['DELETE'])
def delete_game(post_id):
    post = db.session.scalars(
        db.select(FoodRescue).
        filter_by(post_id=post_id).
        limit(1)
    ).first()
    if post is not None:
        try:
            db.session.delete(post)
            db.session.commit()
        except Exception as e:
            return jsonify(
                {
                    "message": "An error occurred deleting the post.",
                    "error": str(e)
                }
            ), 500
        return jsonify(
            {
                "data": {
                    "post_id": post_id
                }
            }
        ), 200
    return jsonify(
        {
            "data": {
                "post_id": post_id
            },
            "message": "Post not found."
        }
    ), 404


def get_distance(lat1, lon1, lat2, lon2):
    # Haversine formula to calculate distance
    r = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = r * c
    return d


def add_distance_attribute(posts, curr_lat, curr_long):
    for post in posts:
        post.distance = get_distance(curr_lat, curr_long, float(
            post.coordinate_lat), float(post.coordinate_long))
    return sorted(posts, key=lambda x: x.distance)


@app.route("/posts/verified")
def get_verified_posts():
    '''Defaults to not include expired posts and sort by distance'''
    try:
        data = request.get_json()
        curr_lat = float(data['coordinate_lat'])
        curr_long = float(data['coordinate_long'])

        now = datetime.now()
        verified_posts = FoodRescue.query.filter(
            FoodRescue.verified == True).filter(FoodRescue.dateto > now).all()

        sorted_distance_posts = add_distance_attribute(
            verified_posts, curr_lat, curr_long)
        if len(sorted_distance_posts) == 0:
            return jsonify({
                "message": "There are no posts."
            }), 404
        return jsonify({
            "data": {
                "posts": [post.to_dict() for post in sorted_distance_posts]
            }
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Please include your coordinates",
            "error": str(e)
        }), 500


@app.route("/posts/sortbydistance")
def get_posts_by_distance():
    '''Defaults to not include expired posts'''
    try:
        data = request.get_json()
        curr_lat = float(data['coordinate_lat'])
        curr_long = float(data['coordinate_long'])

        now = datetime.now()
        active_posts = FoodRescue.query.filter(FoodRescue.dateto > now).all()

        sorted_posts = add_distance_attribute(
            active_posts, curr_lat, curr_long)

        return jsonify({
            "data": {
                "posts": [post.to_dict() for post in sorted_posts]
            }
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Please include your coordinates",
            "error": str(e)
        }), 500


@app.route("/posts/organic")
def get_organic_posts():
    '''Defaults to not include expired posts and sort by distance'''
    try:
        data = request.get_json()
        curr_lat = float(data['coordinate_lat'])
        curr_long = float(data['coordinate_long'])

        now = datetime.now()
        organic_posts = FoodRescue.query.filter(
            FoodRescue.foodtype == 'Organic').filter(FoodRescue.dateto > now).all()

        sorted_distance_posts = add_distance_attribute(
            organic_posts, curr_lat, curr_long)
        if len(sorted_distance_posts) == 0:
            return jsonify({
                "message": "There are no posts."
            }), 404
        return jsonify({
            "data": {
                "posts": [post.to_dict() for post in sorted_distance_posts]
            }
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Please include your coordinates",
            "error": str(e)
        }), 500


@app.route("/posts/vegan")
def get_vegan_posts():
    '''Defaults to not include expired posts and sort by distance'''
    try:
        data = request.get_json()
        curr_lat = float(data['coordinate_lat'])
        curr_long = float(data['coordinate_long'])

        now = datetime.now()
        vegan_posts = FoodRescue.query.filter(
            FoodRescue.foodtype == 'Vegan').filter(FoodRescue.dateto > now).all()

        sorted_distance_posts = add_distance_attribute(
            vegan_posts, curr_lat, curr_long)
        if len(sorted_distance_posts) == 0:
            return jsonify({
                "message": "There are no posts."
            }), 404
        return jsonify({
            "data": {
                "posts": [post.to_dict() for post in sorted_distance_posts]
            }
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Please include your coordinates",
            "error": str(e)
        }), 500


@app.route("/posts/new")
def get_new_posts():
    '''Defaults to not include expired posts'''
    try:
        now = datetime.now()
        new_posts = FoodRescue.query.filter(FoodRescue.dateto > now).order_by(
            FoodRescue.dateposted.desc()).all()

        if len(new_posts) == 0:
            return jsonify({
                "message": "There are no posts."
            }), 404
        return jsonify({
            "data": {
                "posts": [post.to_dict() for post in new_posts]
            }
        }), 200
    except Exception as e:
        return jsonify({
            "message": "There is an error retriving posts",
            "error": str(e)
        }), 500


@app.route("/posts/urgent")
def get_urgent_posts():
    '''nz'''
    try:
        now = datetime.now()
        urgent_posts = FoodRescue.query.filter(FoodRescue.dateto > now).all()

        if len(urgent_posts) == 0:
            return jsonify({
                "message": "There are no posts."
            }), 404
        urgent_posts = sorted(urgent_posts, key=lambda p: abs(p.dateto - now))

        return jsonify({
            "data": {
                "posts": [post.to_dict() for post in urgent_posts]
            }
        }), 200
    except Exception as e:
        return jsonify({
            "message": "There is an error retriving posts",
            "error": str(e)
        }), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
