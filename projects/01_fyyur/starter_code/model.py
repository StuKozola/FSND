
from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)
ma = Marshmallow(app)

migrate = Migrate(app, db)
db.init_app(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # added fields, as a database migration using Flask-Migrate from original
    genres = db.Column(db.ARRAY(db.String(40)))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(500))

    # normalization of tables with realationships
    # note we've moved city and state into a separate City table
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    shows = db.relationship('Show', backref='venues',
                             cascade='all, delete-orphan', lazy=True)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # added fields, as a database migration using Flask-Migrate from original
    genres = db.Column(db.ARRAY(db.String(40)))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(500))

    # normalization of tables with realationships
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    shows = db.relationship('Show', backref='artists',
                             cascade='all, delete-orphan', lazy=True)

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class City(db.Model):
    __tablename__ = 'city'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(40))
    state = db.Column(db.String(40))

    # normalization of tables with realationships
    venues = db.relationship('Venue', backref='cities',  lazy=True)
    artist = db.relationship('Artist', backref='cities', lazy=True)

#----------------------------------------------------------------------------#
# Marshmallow schemas for dumping to dictionaries
#----------------------------------------------------------------------------#
class CitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = City
        include_relationships = True
        load_instance = True

class ArtistSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Artist
        include_relationships = True
        load_instance = True 

    cities = ma.Nested(CitySchema)

class VenueSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Venue
        include_relationships = True
        load_instance = True
    
    cities = ma.Nested(CitySchema)
    artists = ma.Nested(ArtistSchema, many=True)

class ShowSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Show
        include_relationships = True
        load_instance = True
    
    artists = ma.Nested(ArtistSchema, many=True)
    venues = ma.Nested(VenueSchema, many=True)
#----------------------------------------------------------------------------#
# Utilitiy functions for working with data
#----------------------------------------------------------------------------#
def isiterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True

def get_city_id(city_name,state_abbr):
    return db.session.query(City.id).filter_by(city=city_name, state=state_abbr)

def get_venue_id(venue_name):
    return db.session.query(Venue.id).filter_by(name=venue_name)

def add_city(city, state):
    # check if city exists and add or just retrun city_id
    exists = City.query.filter_by(city=city, state=state).first()
    if not exists:
        c = City()
        c.city = city
        c.state = state
        db.session.add(c)
        db.session.commit()
    
    return get_city_id(city, state)

def sorted_venue_shows(venue_id):
    past_shows = db.session.query(Show).filter(
        Show.start_time < datetime.now(),
        Show.venue_id == venue_id).all()
    
    future_shows = db.session.query(Show).filter(
        Show.start_time >= datetime.now(),
        Show.venue_id == venue_id).all()
 
    past = [{'artist_id': p.artists.id,
            'artist_name': p.artists.name,
            'artist_image_link': p.artists.image_link,
            'start_time': p.start_time.strftime("%m/%d/%Y, %H:%M")
            } for p in past_shows]
    
    future = [{'artist_id': p.artists.id,
            'artist_name': p.artists.name,
            'artist_image_link': p.artists.image_link,
            'start_time': p.start_time.strftime("%m/%d/%Y, %H:%M")
            } for p in future_shows]
    
    return past, future

def sorted_artist_shows(artist_id):
    past_shows = db.session.query(Show).filter(
        Show.start_time < datetime.now(),
        Show.venue_id == artist_id).all()
    
    future_shows = db.session.query(Show).filter(
        Show.start_time >= datetime.now(),
        Show.venue_id == artist_id).all()
 
    past = [{'venue_id': p.venues.id,
            'venue_name': p.venues.name,
            'venue_image_link': p.venues.image_link,
            'start_time': p.start_time.strftime("%m/%d/%Y, %H:%M")
            } for p in past_shows]
    
    future = [{'venue_id': p.venues.id,
            'venue_name': p.venues.name,
            'venue_image_link': p.venues.image_link,
            'start_time': p.start_time.strftime("%m/%d/%Y, %H:%M")
            } for p in future_shows]
    
    return past, future

#----------------------------------------------------------------------------#
# Sample data to initialize database
#----------------------------------------------------------------------------#
def seed_db(db):
    # clear database
    Show.query.delete()
    Venue.query.delete()
    Artist.query.delete()
    City.query.delete()

    db.session.execute("ALTER SEQUENCE city_id_seq RESTART WITH 1")
    db.session.execute("ALTER SEQUENCE artist_id_seq RESTART WITH 1")
    db.session.execute("ALTER SEQUENCE venue_id_seq RESTART WITH 1")
    db.session.execute("ALTER SEQUENCE show_id_seq RESTART WITH 1")

    [cities, artists, venues, shows] = seed_data()

    # Add data to database
    for c in cities:
        update_city = City(**c)
        db.session.add(update_city)

    db.session.commit()

    for a in artists:
        update_artist = Artist(**a)
        db.session.add(update_artist)

    db.session.commit()

    for v in venues:
        update_venue = Venue(**v)
        db.session.add(update_venue)

    db.session.commit()

    for s in shows:
        update_show = Show(**s)
        db.session.add(update_show)

    db.session.commit()


def seed_data():
    cities = [
        {"city": "San Francisco",
         "state": "CA"
         }, {
            "city": "New York",
            "state": "NY"
        }
    ]

    venues = [{
        "name": "The Musical Hop",
        "address": "1015 Folsom Street",
        "phone": "123-123-1234",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "city_id": 1,
    }, {
        "name": "The Dueling Pianos Bar",
        "genres": ["Classical", "R&B", "Hip-Hop"],
        "address": "335 Delancey Street",
        "city_id": 2,
        "phone": "914-003-1132",
        "website": "https://www.theduelingpianos.com",
        "facebook_link": "https://www.facebook.com/theduelingpianos",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    }, {
        "name": "Park Square Live Music & Coffee",
        "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
        "address": "34 Whiskey Moore Ave",
        "city_id": 1,
        "phone": "415-000-1234",
        "website": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    }]

    artists = [{
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city_id": 1,
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    }, {
        "name": "Matt Quevedo",
        "genres": ["Jazz"],
        "city_id": 2,
        "phone": "300-400-5000",
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    }, {
        "name": "The Wild Sax Band",
        "genres": ["Jazz", "Classical"],
        "city_id": 1,
        "phone": "432-325-5432",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    }]

    shows = [{
        "venue_id": 1,
        "artist_id": 1,
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 2,
        "artist_id": 3,
        "start_time": "2035-04-15T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "artist_id": 2,
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "artist_id": 1,
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "artist_id": 3,
        "start_time": "2035-04-01T20:00:00.000Z"
    }]

    return cities, artists, venues, shows
