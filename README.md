Fyyur
-----

### Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

### Features

* creating new venues, artists, and creating new shows.
* searching for venues and artists.
* learning more about a specific artist or venue.

### Tech Stack

* **SQLAlchemy ORM**
* **PostgreSQL**
* **Python3** and **Flask**
* **Flask-Migrate** 
* **HTML**, **CSS**, and **Javascript** with [Bootstrap 3](https://getbootstrap.com/docs/3.4/customize/)

### Development Setup

To start and run the local development server,

1. Install the dependencies:
  ```
  $ pip install -r requirements.txt
  ```

2. Run the development server:
  ```
  $ export FLASK_APP=myapp
  $ export FLASK_ENV=development # enables debug mode
  $ python3 app.py
  ```

3. Navigate to Home page [http://localhost:5000](http://localhost:5000)
