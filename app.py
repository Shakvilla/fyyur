#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify, flash
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from flask import request
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

import sys


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

 # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue', lazy='dynamic')

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.genres} {self.phone} {self.image_link} {self.facebook_link} {self.website} {self.seeking_talent} {self.seeking_description} {self.shows}>'



class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False )
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)
    
    def __repr__(self):
      return f'<Artist: {self.id} {self.name} { self.city} {self.state} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.website} {self.seeking_venue} {self.seeking_description} {self.shows} {self.website}>'


class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
  def detail(self):
    return {
      'venue_id' :self.venue_id,
      'venue_name' :self.Venue.name,
      'artist_id' :self.artist_id,
      'artist_name' :self.Artist.name,
      'artist_image_link' :self.Artist.image_link,
      'start_time' :self.start_time
    }

  def __repr__(self):
    return f'<Show: {self.id} {self.venue_id} {self.artist_id} {self.start_time}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
      date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  
  current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()

  venue_state_and_city = ''
  data = []
  for venue in venues:
    print(venue)

    upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()
    if venue_state_and_city == venue.city + venue.state:
      data[len(data) - 1]["venues"].append({
          "id": venue.id,
          "name":venue.name,
          "num_upcoming_shows": len(upcoming_shows) # a count of the number of shows
        })
    else:
      venue_state_and_city == venue.city + venue.state
      data.append({
        "city": venue.city,
        "state": venue.state,
        'venues': [{
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upcoming_shows)
        }]
      })

    # else:
    #   for i, area in enumerate(areas):
    #     if area['city'] == venue.city and area['state'] == venue.state:
    #       pos_area = i
    #       break
    #   if pos_area < 0:
    #     area_item = {
    #       "city": venue.city,
    #       "state": venue.state,
    #       "venues": []
    #     }
    #     areas.append(area_item)
    #     pos_area = len(areas) - 1
    #   else:
    #     area_item = areas[pos_area]
    # v = {
    #     "id": venue.id,
    #     "name": venue.name,
    #     "num_upcoming_shows": 4
    #   }
    # area_item['venues'].append(v)
    # areas[pos_area] = area_item
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  # venue_data = Venue.query.get(venue_id)

  data = Venue.query.filter_by(id=venue_id).first()
  data.genres = json.loads(data.genres)

  upcoming_shows = []
  past_shows = []
  for show in data.shows:
    if show.start_time > datetime.now():
      upcoming_shows.append(show)
    else:
      past_shows.append(show)
  data.upcoming_shows = upcoming_shows
  data.past_shows = past_shows
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # form = VenueForm()
  error = False
   
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    genres = json.dumps(request.form.get('genres'))
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website_link')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')
    venue_details = Venue(name=name, city=city, state=state, address=address, genres=genres, phone=phone, image_link=image_link, facebook_link=facebook_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
    if 'seeking_talent' in request.form:
      venue_details.seeking_talent = True
    db.session.add(venue_details)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    abort(500)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')




@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.order_by('name').all()
  return render_template('pages/artists.html', artists=data)



@app.route('/artists/search', methods=['POST'])
def search_artists():

  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist_data = Artist.query.filter_by(id=artist_id).first()
  artist_data.genres = json.loads(artist_data.genres)

  upcoming_shows = []
  past_shows = []

  for show in artist_data.shows :
    if show.start_time > datetime.now():
      upcoming_shows.append(show)
    else:
      past_shows.append(show)
  artist_data.upcoming_shows = upcoming_shows
  artist_data.past_shows = past_shows
  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  current_arist = Artist.query.filter_by(id=artist_id).first()

  form.name.data = current_arist.name
  form.city.data = current_arist.city
  form.state.data = current_arist.state
  form.phone.data = current_arist.phone
  form.facebook_link.data = current_arist.facebook_link
  form.website_link.data = current_arist.website
  form.image_link.data = current_arist.image_link
  form.genres.data = json.loads(current_arist.genres)
  form.seeking_venue.data = current_arist.seeking_venue
  form.seeking_description.data = current_arist.seeking_description

 
  # TODO: populate form with fields from artist with ID <artist_id>
  
  return render_template('forms/edit_artist.html', form=form, artist=current_arist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  error = False

  try:

    current_artist = Artist.query.filter_by(id=artist_id).first()
    current_artist.name = request.form.get('name')
    current_artist.city = request.form.get('city')
    current_artist.state = request.form.get('state')
    current_artist.phone = request.form.get('phone')
    current_artist.genres = json.dumps(request.form.get('genres'))
    current_artist.facebook_link = request.form.get('facebook_link')
    current_artist.website = request.form.get('website_link')
    current_artist.image_link = request.form.get('image_link')
    current_artist.seeking_venue = request.form.get('seeking_venue')
    current_artist.seeking_description = request.form.get('seeking_description')
    if 'seeking_venue' in request.form : 
      current_artist.seeking_venue = True
    db.session.add(current_artist)
    db.session.commit()
  except:
    db.session.rollback()
    error: True

  if error:
    flash('Artist ' + request.form['name'] + ' could not be edited successfully')
    abort(500)
  else:
    flash('Artist ' + request.form['name'] + ' edited successfully')

  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
 

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
    
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = json.dumps(request.form.get('genres'))
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website = request.form.get('website_link')
    seeking_venue = request.form.get('seeking_venue')
    seeking_description = request.form.get('seeking_description')
    artist_details = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)
    if 'seeking_venue' in request.form: 
      artist_details.seeking_venue = True
    db.session.add(artist_details)
    db.session.commit()
    
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.') 
    abort(500)
 # on successful db insert, flash success
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():



  show_query = Show.query.options(db.joinedload(Show.Venue), db.joinedload(Show.Artist)).all()
  data = list(map(Show.detail, show_query))
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()  
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False 
  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')

    new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(new_show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
  
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
