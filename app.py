#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Model Helpers
#----------------------------------------------------------------------------#

def get_venue(venue_id):
  return Venue.query.get(venue_id)

def get_artist(artist_id):
  return Artist.query.get(artist_id)

def venue_past_shows(venue_id):
  return Show.query.filter(Show.start_time < datetime.now(), Show.venue_id == venue_id).all()

def venue_upcoming_shows(venue_id):
  return Show.query.filter(Show.start_time > datetime.now(), Show.venue_id == venue_id).all()

def artist_past_shows(artist_id):
  return Show.query.filter(Show.start_time < datetime.now(), Show.artist_id == artist_id).all()

def artist_upcoming_shows(artist_id):
  return Show.query.filter(Show.start_time > datetime.now(), Show.artist_id == artist_id).all()


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))

    @property
    def upcoming(self):
      venue = get_venue(self.venue_id)
      artist = get_artist(self.artist_id)

      if self.start_time > datetime.now():
        return {
          "venue_id": self.venue_id,
          "venue_name": venue.name,
          "artist_id": self.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": self.start_time.strftime("%m/%d/%Y, %H:%M")
        }
      else:
        return None

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String(120), nullable=False, default='We are looking for an exciting artist to perform here!')
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue Name: {self.name}, City: {self.city}, State: {self.state}>'

    @property
    def city_and_state(self):
      return { 'city': self.city, 'state': self.state }

    @property
    def full_details_with_shows(self):
      past_shows = venue_past_shows(self.id)
      upcoming_shows = venue_upcoming_shows(self.id)

      return {
        'id': self.id,
        'name': self.name,
        'address': self.address,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'website': self.website,
        'facebook_link': self.facebook_link,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description,
        'image_link': self.image_link,
        'past_shows': [{
          'artist_id': p.artist_id,
          'artist_name': p.artist.name,
          'artist_image_link': p.artist.image_link,
          'start_time': p.start_time.strftime("%m/%d/%Y, %H:%M")
          } for p in past_shows],
          'upcoming_shows': [{
              'artist_id': u.artist.id,
              'artist_name': u.artist.name,
              'artist_image_link': u.artist.image_link,
              'start_time': u.start_time.strftime("%m/%d/%Y, %H:%M")
          } for u in upcoming_shows],
          'past_shows_count': len(past_shows),
          'upcoming_shows_count': len(upcoming_shows)
      }


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String(120), nullable=False, default='We are looking to perform at an exciting venue!')

    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist Name: {self.name}, City: {self.city}, State: {self.state}>'
    
    @property
    def basic_details(self):
      return { 'id': self.id, 'name': self.name }

    @property
    def full_details_with_shows(self):
      past_shows = artist_past_shows(self.id)
      upcoming_shows = artist_upcoming_shows(self.id)

      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': self.genres,
        'website': self.website,
        'facebook_link': self.facebook_link,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description,
        'image_link': self.image_link,
        'past_shows': [{
          'venue_id': p.venue_id,
          'venue_name': p.venue.name,
          'venue_image_link': p.venue.image_link,
          'start_time': p.start_time.strftime("%m/%d/%Y, %H:%M")
          } for p in past_shows],
        'upcoming_shows': [{
            'venue_id': u.venue.id,
            'venue_name': u.venue.name,
            'venue_image_link': u.venue.image_link,
            'start_time': u.start_time.strftime("%m/%d/%Y, %H:%M")
        } for u in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
      }

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  try:
    areas = [v.city_and_state for v in Venue.query.distinct(Venue.city, Venue.state).all()]
    
    for a in areas:
      a['venues'] = [{'id': v.id, 'name': v.name, 'num_upcoming_shows': v.shows} for v in Venue.query.filter_by(city=a['city']).all()]

    return render_template('pages/venues.html', areas=areas)
  except:
    flash('An error occurred. No venues to display currently')
    return redirect(url_for('index'))



@app.route('/venues/search', methods=['POST'])
def search_venues():

  try:
    search_term = request.form.get('search_term', '')

    results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

    response = {
      "count": len(results),
      "data": [{
        "id": v.id,
        "name": v.name,
        "num_upcoming_shows": len(v.shows)
      } for v in results]
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  except:
    flash('An error occurred while searching, please try again')
    return redirect(url_for('venues'))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  try:
    data = Venue.query.filter_by(id=venue_id).all()[0]

    return render_template('pages/show_venue.html', venue=data.full_details_with_shows)
  except:
    flash('Sorry, we couldn\'t show that venue')
    return redirect(url_for('index'))


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  error = False

  try:
    new_venue = Venue(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      address=request.form.get('address'),
      # genres=request.form.getlist('genres'),
      phone=request.form.get('phone'),
      facebook_link=request.form.get('facebook_link'),
      image_link=request.form.get('image_link'),
      website=request.form.get('website'),
      seeking_talent=request.form.get('seeking_talent') == 'True',
      seeking_description=request.form.get('seeking_description')
    )
    db.session.add(new_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + new_venue.name + ' could not be listed.')
    
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  error = None

  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    flash('An error occurred when deleting venue, please try again later')
    return redirect(url_for('index'))
  else:
    flash('Successfully deleted venue')
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  try:
    data = [a.basic_details for a in Artist.query.all()]

    return render_template('pages/artists.html', artists=data)
  except:
    flash('An error occurred. No artists to display currently')
    return redirect(url_for('index'))

@app.route('/artists/search', methods=['POST'])
def search_artists():

  try:
    search_term = request.form.get('search_term', '')

    results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

    response = {
      "count": len(results),
      "data": [{
        "id": a.id,
        "name": a.name,
        "num_upcoming_shows": len(a.shows)
      } for a in results]
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  except:
    flash('An error occurred while searching, please try again')
    return redirect(url_for('artists'))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  try:
    data = Artist.query.filter_by(id=artist_id).all()[0]

    return render_template('pages/show_artist.html', artist=data.full_details_with_shows)
  except:
    flash('Sorry, we couldn\'t show that artist')
    return redirect(url_for('index'))



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist = Artist.query.filter_by(id=artist_id).all()[0]

  form = ArtistForm(
    name=artist.name,
    city=artist.city,
    state=artist.state,
    genres=artist.genres,
    phone=artist.phone,
    facebook_link=artist.facebook_link,
    website=artist.website,
    image_link=artist.image_link,
    seeking_venue=artist.seeking_venue,
    seeking_description=artist.seeking_description
  )

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  try:
    artist = Artist.query.filter_by(id=artist_id).all()[0]

    artist.name=request.form.get('name')
    artist.city=request.form.get('city')
    artist.state=request.form.get('state')
    artist.phone=request.form.get('phone')
    artist.genres=request.form.getlist('genres')
    artist.facebook_link=request.form.get('facebook_link')
    artist.website=request.form.get('website')
    artist.image_link=request.form.get('image_link')
    artist.seeking_venue=request.form.get('seeking_venue') == 'True'
    artist.seeking_description=request.form.get('seeking_description')

    db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. Artist could not be updated')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue = Venue.query.filter_by(id=venue_id).all()[0]

  form = VenueForm(
    name=venue.name,
    city=venue.city,
    state=venue.state,
    address=venue.address,
    phone=venue.phone,
    facebook_link=venue.facebook_link,
    website=venue.website,
    image_link=venue.image_link,
    seeking_talent=venue.seeking_talent,
    seeking_description=venue.seeking_description
  )

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  try:
    venue = Venue.query.filter_by(id=venue_id).all()[0]

    venue.name=request.form.get('name')
    venue.city=request.form.get('city')
    venue.state=request.form.get('state')
    venue.address=request.form.get('address')
    venue.phone=request.form.get('phone')
    venue.facebook_link=request.form.get('facebook_link')
    venue.website=request.form.get('website')
    venue.image_link=request.form.get('image_link')
    venue.seeking_talent=request.form.get('seeking_talent') == 'True'
    venue.seeking_description=request.form.get('seeking_description')

    db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be updated')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  error = False

  try:
    new_artist = Artist(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      phone=request.form.get('phone'),
      genres=request.form.getlist('genres'),
      facebook_link=request.form.get('facebook_link'),
      image_link=request.form.get('image_link'),
      website=request.form.get('website'),
      seeking_venue=request.form.get('seeking_venue') == 'True',
      seeking_description=request.form.get('seeking_description')
    )
 
    db.session.add(new_artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')

  return redirect(url_for('index'))



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def list_shows():

  try:
    available_shows = [ s.upcoming for s in Show.query.all() if s.upcoming is not None]

    return render_template('pages/shows.html', shows=available_shows)
  except:
    flash('An error occurred. No shows to display currently')
    return redirect(url_for('index'))

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  error = False

  try:
    new_show = Show(
      start_time=request.form.get('start_time'),
      venue_id=request.form.get('venue_id'),
      artist_id=request.form.get('artist_id')
    )
    db.session.add(new_show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if not error:
    flash('Show was successfully listed!')
  else:
    flash('An error occurred. Show could not be listed.')

  return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
