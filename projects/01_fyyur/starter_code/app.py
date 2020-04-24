#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import  render_template, request, Response, flash, redirect, url_for

import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from model import *

#----------------------------------------------------------------------------#
# App Config and Models are in model.py
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# the app can also be initialized with data using the /sampledb route
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/')
def index():
    return render_template('pages/home.html')

@app.route('/sampledb')
def sampledb():
    # Create a sample database to seed app
    seed_db(db)
    return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
    # show venues by city
    data = City.query.all()
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term','')
    data = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    response = {'count': len(data), 'data': data}
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    data = Venue.query.get(venue_id)
    data = VenueSchema().dump(data)

    # pull up city and state a level
    data['city'] = data['cities']['city']
    data['state'] = data['cities']['state']

    # shows at venue
    past, upcoming = sorted_venue_shows(data['id'])
    data['past_shows_count'] = len(past)
    data['past_shows'] = past
    data['upcoming_shows_count'] = len(upcoming)
    data['upcoming_shows'] = upcoming

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = request.form
    
    # insert form data as a new Venue record in the db ig it does not exits
    venue = Venue()
    venue.name = form.get('name')
    # test to make sure it does not already exist
    exists = Venue.query.filter_by(name=venue.name).first()
    if exists:
        flash('An error occurred. Venue ' + venue.name + ' already exists.  Please edit instead.')
        return render_template('pages/home.html')

    venue.city_id=add_city(form.get('city'), form.get('state'))
    venue.address=form.get('address')
    venue.phone=form.get('phone')
    venue.genres=form.getlist('genres')
    venue.facebook_link=form.get('facebook_link')

    try:
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + venue.name + ' was successfully listed!')
    except Exception as exception:
        db.session.rollback()
        print(exception)
        #on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + form.get('name') + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    # Bonus: add delete button on venue page to use this endpoint
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Deleted venue ' + venue.name)
        print('Deleted ',venue.name)
    except Exception as exception:
        db.session.rollback()
        flash('Could not delete Venue with id='+ venue_id)
        print(exception)
    finally:
        db.session.close()

    return render_template('pages/home.html'), 200

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    data = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    response = {'data':data, 'count':len(data)}
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    data = Artist.query.get(artist_id)
    data = ArtistSchema().dump(data)

    # pull up city and state a level
    data['city'] = data['cities']['city']
    data['state'] = data['cities']['state']

    # shows at venue
    past, upcoming = sorted_artist_shows(data['id'])
    data['past_shows_count'] = len(past)
    data['past_shows'] = past
    data['upcoming_shows_count'] = len(upcoming)
    data['upcoming_shows'] = upcoming
    return render_template('pages/show_artist.html', artist=data)

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    # endpoint for taking a artist_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    # Bonus: add delete button on artist page to use this endpoint
    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
        flash('Deleted artist ' + artist.name)
        print('Deleted ',artist.name)
    except Exception as exception:
        db.session.rollback()
        flash('Could not delete artist with id='+ artist_id)
        print(exception)
    finally:
        db.session.close()

    return render_template('pages/home.html'), 200

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # update artists data in edit form
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = request.form
    artist = Artist.query.get(artist_id)
    
    # update city if new
    artist.city_id = add_city(form.get('city'), form.get('state'))

    artist.name = form.get('name')
    artist.phone = form.get('phone')
    artist.facebook_link = form.getlist('facebook_link')
    artist.genres = form.getlist('genres')

    try:
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + artist.name + ' was successfully listed!')
    except Exception as exception:
        db.session.rollback()
        print(exception)
        #on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
    finally:
        db.session.close()
        
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.cities.city
    form.state.data = venue.cities.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = request.form
    venue = Venue.query.get(venue_id)
    
    # update city if new
    venue.city_id = add_city(form.get('city'), form.get('state'))

    venue.name = form.get('name')
    venue.address= form.get('address')
    venue.phone = form.get('phone')
    venue.facebook_link = form.get('facebook_link')
    venue.genres = form.getlist('genres')

    try:
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + venue.name + ' was successfully listed!')
    except Exception as exception:
        db.session.rollback()
        print(exception)
        #on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('venues', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # insert form data as a new Artist record in the db
    form = request.form
    
    # insert form data as a new Artist record in the db ig it does not exits
    artist = Artist()
    artist.name = form.get('name')
    # test to make sure it does not already exist
    exists = Artist.query.filter_by(name=artist.name).first()
    if exists:
        flash('An error occurred. Artist ' + artist.name + ' already exists.  Please edit instead.')
        return render_template('pages/home.html')

    artist.city_id=add_city(form.get('city'), form.get('state'))
    artist.address=form.get('address')
    artist.phone=form.get('phone')
    artist.genres=form.getlist('genres')
    artist.facebook_link=form.get('facebook_link')

    try:
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + artist.name + ' was successfully listed!')
    except Exception as exception:
        db.session.rollback()
        #on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
    # displays list of shows at /shows
    all_shows = Show.query.all()
    data = [{
        "venue_id": show.venue_id,
        "venue_name": show.venues.name,
        "artist_id": show.artist_id,
        "artist_name": show.artists.name, 
        "artist_image_link": show.artists.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    } for show in all_shows]
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/search', methods=['POST'])
def search_shows():
    # search on artists/venues with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
   
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
    all_shows = []
    for a in artists:
        for i in a.shows:
            all_shows.append(i.id)
    
    for v in venues:
        for i in v.shows:
            all_shows.append(i.id)

    all_shows = Show.query.filter(Show.id.in_(all_shows)).all()
    data = [{
        "venue_id": show.venue_id,
        "venue_name": show.venues.name,
        "artist_id": show.artist_id,
        "artist_name": show.artists.name, 
        "artist_image_link": show.artists.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    } for show in all_shows]

    print(data)
    response = {'data':data, 'count':len(data)}
    return render_template('pages/search_shows.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = request.form
    show = Show()
    show.artist_id = form.get('artist_id')
    show.venue_id = form.get('venue_id')
    show.start_time = form.get('start_time')

    try:
        # on successful db insert, flash success
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except Exception as exception:
        db.session.rollback()
        #on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
