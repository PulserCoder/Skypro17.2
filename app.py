# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

"""START CONFIG PROGRAMM"""
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)
api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
gernes_ns = api.namespace('genres')


class Movie(db.Model):
    """movie model for sqlalchemy"""
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    """director model for sqlalchemy"""
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Integer()
    name = fields.String()


director_schema = DirectorSchema()


class Genre(db.Model):
    """genre model for sqlalchemy"""
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    """movie schema model for sqlalchemy"""
    id = fields.Integer()
    title = fields.String()
    description = fields.String()
    trailer = fields.String()
    year = fields.Integer()
    rating = fields.String()
    genre_id = fields.Integer()
    director_id = fields.Integer()


@movie_ns.route('/')
class MoviesView(Resource):
    """views movie"""

    def get(self):
        data_dir = request.args.get('director_id', 0)
        data_gen = request.args.get('genre_id', 0)
        if data_dir and data_gen:
            if Movie.query.join(Director, Genre,
                                Movie.genre_id == Genre.id and Movie.director_id == Director.id).filter(
                Director.id == data_dir, Genre.id == data_gen):
                print(2)
                sql = movies_schema.dump(Movie.query.join(Director, Genre,
                                                          Movie.genre_id == Genre.id and Movie.director_id == Director.id).filter(
                    Director.id == data_dir, Genre.id == data_gen))
                return sql, 200
            else:
                return "", 404
        if data_dir:
            print(3)
            if Movie.query.join(Director, Director.id == Movie.director_id).filter(Director.id == data_dir):
                sql = movies_schema.dump(Movie.query.join(Director).filter(Director.id == data_dir))
                return sql, 200
            else:
                return "", 404
        elif data_gen:
            print('1')
            if Movie.query.join(Genre, Genre.id == Movie.genre_id).filter(Genre.id == data_gen):
                sql = movies_schema.dump(Movie.query.join(Genre).filter(Genre.id == data_gen))
                return sql, 200
            else:
                return "", 404
        movies = movies_schema.dump(Movie.query.all())
        return movies, 200


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    """one movie view"""

    def get(self, uid=None):
        if Movie.query.filter(Movie.id == uid):
            sql = movies_schema.dump(Movie.query.join(Genre, Movie.genre_id == Genre.id).filter(Movie.id == uid))
            return sql, 200
        else:
            return "", 404


@director_ns.route('/')
class DirectorsView(Resource):
    def post(self):
        data = request.json
        director = Director(**data)
        db.session.add(director)
        db.session.commit()
        return "", 200


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def put(self, uid):
        data = request.json
        director = Director.query.filter(Director.id == uid).one()
        director.name = data["name"]
        db.session.add(director)
        db.session.commit()
        return "", 200

    def patch(self, uid):
        director = Director.query.get(uid)
        data = request.json
        if data.get('name'):
            director.name = data["name"]
        db.session.add(director)
        return "", 200

    def delete(self, uid):
        Director.query.filter(Director.id == uid).delete()
        db.session.commit()


@gernes_ns.route('/')
class GenresView(Resource):
    def post(self):
        data = request.json
        genre = Genre(**data)
        db.session.add(genre)
        print(11)
        db.session.commit()
        return "", 200


@gernes_ns.route('/<int:uid>')
class GenreView(Resource):
    def put(self, uid):
        data = request.json
        genre = Genre.query.filter(Genre.id == uid).one()
        print(genre)
        genre.name = data["name"]
        db.session.add(genre)
        db.session.commit()
        return "", 200

    def patch(self, uid):
        genre = Genre.query.get(uid)
        data = request.json
        if data.get('name'):
            genre.name = data["name"]
        db.session.add(genre)
        return "", 200

    def delete(self, uid):
        Genre.query.filter(Genre.id == uid).delete()
        db.session.commit()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

if __name__ == '__main__':
    app.run(debug=True)
