# Import the dependencies.

import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
from flask import Flask, jsonify
import datetime as dt
import numpy as np
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

# Initialize Flask app
app = Flask(__name__)

# Database setup
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

# Helper function to create a new session
def get_session():
    return Session(engine)

@app.route("/")
def welcome():
    """All available API routes."""
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' dates should be in the format MMDDYYYY.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year."""
    session = get_session()
    try:
        prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
        results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
        precip_data = {date: prcp for date, prcp in results}
        return jsonify(precip_data)
    finally:
        session.close()

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    session = get_session()
    try:
        results = session.query(Station.station).all()
        station_list = list(np.ravel(results))
        return jsonify(stations=station_list)
    finally:
        session.close()

@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for the previous year."""
    session = get_session()
    try:
        prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
        results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= prev_year).all()
        temp_data = list(np.ravel(results))
        return jsonify(temps=temp_data)
    finally:
        session.close()

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start, end=None):
    """Return TMIN, TAVG, and TMAX for a given date range."""
    session = get_session()
    try:
        sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        start_date = dt.datetime.strptime(start, "%m%d%Y")
        
        if end:
            end_date = dt.datetime.strptime(end, "%m%d%Y")
            results = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        else:
            results = session.query(*sel).filter(Measurement.date >= start_date).all()

        temp_stats = list(np.ravel(results))
        return jsonify(temps=temp_stats)
    finally:
        session.close()

if __name__ == '__main__':
    app.run()
