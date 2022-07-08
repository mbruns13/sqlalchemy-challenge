# Use Flask to create your routes, as follows:
# /
#     Homepage.
#     List all available routes.
# /api/v1.0/precipitation
#     Convert the query results to a dictionary using date as the key and prcp as the value.
#     Return the JSON representation of your dictionary.
# /api/v1.0/stations
#     Return a JSON list of stations from the dataset.
# /api/v1.0/tobs
#     Query the dates and temperature observations of the most active station for the previous year of data.
#     Return a JSON list of temperature observations (TOBS) for the previous year.
# /api/v1.0/<start> and /api/v1.0/<start>/<end>
#     Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.
#     When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date.
#     When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates from the start date through the end date (inclusive).

# Hints
#     You will need to join the station and measurement tables for some of the queries.
#     Use Flask jsonify to convert your API data into a valid JSON response object.

#dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime
import datetime as dt
from flask import Flask, jsonify, Response

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def homepage():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
#   Convert the query results to a dictionary using date as the key and prcp as the value.
#   Return the JSON representation of your dictionary.   
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()
    session.close()

    # Create a dictionary from the row data and append to a list of temp_data
    precip_data = []
    for date, prcp in results: 
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_data.append(precip_dict)
    
    return jsonify(precip_data)

@app.route("/api/v1.0/stations")
def stations():
#   Return a JSON list of stations from the dataset.
    
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    # stations_list = []
    # for id, station in results:
    #     station_dict = {}
    #     station_dict["id"] = id
    #     station_dict["station"] = station
    #     stations_list.append(station_dict)
    
    station_list = list(np.ravel(results))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temperature():
#   Query the dates and temperature observations of the most active station for the previous year of data.
#   Return a JSON list of temperature observations (TOBS) for the previous year.
    
    session = Session(engine)
    
    most_active_station = session.query(Station.station).filter(Station.station == Measurement.station).group_by(Station.station).order_by(func.count(Measurement.station).desc()).first()
    recent_date_string = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    recent_date = datetime.strptime(recent_date_string, "%Y-%m-%d")
    query_date =  recent_date - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Station.station == Measurement.station).filter(Measurement.Station == most_active_station).filter(Measurement.date >= query_date).order_by(Measurement.date).all()
    session.close()

    return(results)

# @app.route("/api/v1.0/<start>")
# def ():
# #   Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.
# #   When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date.
# #   When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates from the start date through the end date (inclusive).
    
#     session = Session(engine)
#     results = session.query().all()
#     session.close()

#     return(

#     )

# @app.route("/api/v1.0/<start>/<end>")
# def ():
    
#     session = Session(engine)
#     results = session.query().all()
#     session.close()

#     return()



if __name__ == '__main__':
    app.run(debug=True)
