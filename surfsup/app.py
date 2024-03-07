# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
#these are listed in the climate_starter jupyter notebook
Measurement=Base.classes.measurement
Station=Base.classes.station

# Create our session (link) from Python to the DB
#Global session used for learning purposes, for real life application-
#-it should be written within the route code as you see below commented #
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

#Starting at HOME PAGE
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def preciptitation():
    #session = Session(engine)
    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    year_ago_prec= session.query(Measurement.date , Measurement.prcp).\
        filter(Measurement.date >= year_ago).all()
    #session.close()
    # Convert list of tuples into normal list
    stations_list = list(np.ravel(year_ago_prec))
    return jsonify(stations_list)

@app.route("/api/v1.0/stations")
def stations():
    #session = Session(engine)
    stations = session.query(Measurement.station).distinct().all()
    #session.close()
    # Convert list of tuples into normal list
    station_list = list(np.ravel(stations))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #session = Session(engine)
    past_year_temp = session.query(Measurement.tobs).\
        filter(Measurement.station =="USC00519281").\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).all()
    # Convert list of tuples into normal list
    tobs = list(np.ravel(past_year_temp))
    return jsonify(tobs)
    session.close()

@app.route("/api/v1.0/<start>")
def start(start):
    # Validate the date format (YYYY-MM-DD)
    date_format = "%Y-%m-%d"
    # Parsing the start and end dates to ensure they are in the correct format
    #w/out this code: code will return some values even with a month set at 22 which doesn't exist.
    try:
        date_start = dt.datetime.strptime(start, date_format)
    except ValueError:
        return jsonify({"error": "Invalid date format, should be YYYY-MM-DD"}), 400
    #gave this one it's own session(engine) b/c it ran correctly every other attempt
    session = Session(engine)
    sel = [func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs)]
    calculations = session.query(*sel).\
        filter(Measurement.date>=start).all()
    calculations
    start_results= list(np.ravel(calculations))
    # Convert list of tuples into normal list
    return jsonify(start_results)
    session.close()

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Validate the date format (YYYY-MM-DD)
    date_format = "%Y-%m-%d"
    # Parsing the start and end dates to ensure they are in the correct format
    #w/out this code: code will return some values even with a month set at 22 which doesn't exist.
    try:
        date_start = dt.datetime.strptime(start, date_format)
        date_end = dt.datetime.strptime(end, date_format)
    except ValueError:
        return jsonify({"error": "Invalid date format, should be YYYY-MM-DD"}), 400
    #gave this one it's own session(engine) b/c it ran correctly every other attempt
    session = Session(engine)
    sel = [func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs)]
    calculations_range = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    calculations_range
    # Convert list of tuples into normal list
    start_range_results= list(np.ravel(calculations_range))
    return jsonify(start_range_results)
    session.close()

if __name__ == "__main__":
    app.run(debug=True)