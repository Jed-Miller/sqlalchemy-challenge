# Import the dependencies.
import datetime as dt
import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

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
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<b.r/>"
        f"/api/v1.0/<start<br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation values for different dates"""
    # Query all precipitation values
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    for date in latest_date:
        the_date = pd.to_datetime(date)
    date_year_ago = dt.date(the_date.year-1,the_date.month,the_date.day)
    one_year_data = session.query(Measurement.date,Measurement.prcp).\
            filter(Measurement.date >= date_year_ago).all()
    
    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp in one_year_data:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        #precipitation_dict["precipitation"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of data of all of the stations in the database"""
    # Query all stations
    stations = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    
    session.close()
    
     # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station, name, latitude, longitude, elevation in stations:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        stations_dict["latitude"] = latitude
        stations_dict["longitude"] = longitude
        stations_dict["elevation"] = elevation
        all_stations.append(stations_dict)
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create a dictionary from the row data and append to a list of all_active_station
    session = Session(engine)

    """Return data for the most active station (USC00519281)"""
    # Query data for most active station
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    for date in latest_date:
        the_date = pd.to_datetime(date)
    date_year_ago = dt.date(the_date.year-1,the_date.month,the_date.day)
    
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.prcp).desc())
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.prcp).desc()).first()[0]
    temp_last12_most_active = session.query(Measurement.station,Measurement.date,Measurement.prcp,Measurement.tobs).\
        filter((Measurement.station == most_active_station)).\
        filter(Measurement.date >= date_year_ago).all()
    
    session.close()
    
   
    #Convert list of tuples into normal list
    all_active_station = []
    for station, date, prcp, tobs in temp_last12_most_active:
        active_station_dict = {}
        active_station_dict["station"] = station
        active_station_dict["date"] = date
        active_station_dict["precipitation"] = prcp
        active_station_dict["temperature"] = tobs
        all_active_station.append(active_station_dict)
        
    return jsonify(all_active_station)

if __name__ == '__main__':
    app.run(debug=True)
