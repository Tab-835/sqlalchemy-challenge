import numpy as numpy
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt 

################################################
# Database Setup
################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

################################################
# Flask Setup
################################################
app = Flask(__name__)

################################################
# Flask Routes
################################################

@app.route("/")
def welcome():
    "List all available api routes."
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

################################################
# /api/v1.0/precipitation
################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_date = dt.date(2017,8,23)
    year_from_last = recent_date - dt.timedelta(days=365)

    temp = (session.query(Measurement.date, Measurement.prcp)
                .filter(Measurement.date <= recent_date)
                .filter(Measurement.date >= year_from_last)
                .order_by(Measurement.date).all())

    precipitation = {date: prcp for date, prcp in temp}

    return jsonify(precipitation)

################################################
# /api/v1.0/stations
################################################
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station).all()

    return jsonify(stations)

################################################
# /api/v1.0/tobs
################################################
@app.route("/api/v1.0/tobs")
def tobs():
    recent_date = dt.date(2017,8,23)
    year_from_last = recent_date - dt.timedelta(days=365)

    prev_year = (session.query(Measurement.tobs)
                .filter(Measurement.station == 'USC00519281')
                .filter(Measurement.date <= recent_date)
                .filter(Measurement.date >= year_from_last)
                .order_by(Measurement.tobs).all())

    return jsonify(prev_year)

################################################
# /api/v1.0/<start>
################################################
@app.route("/api/v1.0/<start>")
def start(start=None):
    tobs = (session.query(Measurement.tobs).filter(Measurement.date.between(start, '2017-08-23')).all())
    tobs_df = pd.DataFrame(tobs)
    
    tavg = tobs_df["tobs"].mean()
    tmax = tobs_df["tobs"].max()
    tmin = tobs_df["tobs"].min()

    return jsonify(tavg, tmax, tmin)

################################################
# /api/v1.0/<start>/<end>
################################################
@app.route("/api/v1.0/<start>/<end>")
def startend(start=None, end=None):
    tobs = (session.query(Measurement.tobs).filter(Measurement.date.between(start, end)).all())
    tobs_df = pd.DataFrame(tobs)
    
    tavg = tobs_df["tobs"].mean()
    tmax = tobs_df["tobs"].max()
    tmin = tobs_df["tobs"].min()

    return jsonify(tavg, tmax, tmin)

if __name__ == "__main__":
    app.run(debug=True)