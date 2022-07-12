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
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()
    session.close()

    # Create a dictionary from the row data and append to a list of temp_data
    precip_data = []
    for date, prcp in results: 
        precip_dict = {}
        #trying to see if I can return date as a dt object rather than a string? date_dt_object =  dt.datetime.strptime(date, "%Y-%m-%d")
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_data.append(precip_dict)

#   Return the JSON representation of your dictionary.       
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

#   Return JSON list of stations
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temperature():
#   Query the dates and temperature observations of the most active station for the previous year of data.
## Learning Assistant said to first find most active station in the entire data set, then find corresponding data   

    session = Session(engine)
    
    #find station with highest count of measurements 
    most_active_station_row = session.query(Station.station).filter(Station.station == Measurement.station).group_by(Station.station).order_by(func.count(Measurement.station).desc()).first()
    most_active_station = most_active_station_row[0]
    #find most recent date in measurement table
    recent_date_string = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    #convert date string to datetime object
    recent_date = datetime.strptime(recent_date_string, "%Y-%m-%d")
    #calculate date to use in query for past year
    query_date =  recent_date - dt.timedelta(days=365)
    
    #query for dates and temperatures, using filter for: most active station, date of measurement being >= query_date -- order results by date in ascending order
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= query_date).filter(Measurement.station == most_active_station).order_by(Measurement.date).all()
    #close session
    session.close()

    #create list of temperatures
    temp_results = [result.tobs for result in results]
    temp_list = list(np.ravel(temp_results))

#   Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def start_date(start=None):
#   Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.
#   When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date.
    #print(dt.datetime.strptime(start, "%m-%d-%Y").date())

    session = Session(engine)
    
    query_start_date = dt.datetime.strptime(start, "%m-%d-%Y")
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= query_start_date).all()
    #TMAX = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= query_start_date).scalar()
    #TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= query_start_date).scalar()

    session.close()
    
    date_query_results = list(np.ravel(results))

    return jsonify(date_query_results)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
#  When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates from the start date through the end date (inclusive).
    
    session = Session(engine)
    query_start_date = dt.datetime.strptime(start, "%m-%d-%Y")
    query_end_date = dt.datetime.strptime(end, "%m-%d-%Y")

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= query_start_date).filter(Measurement.date <= query_end_date).all()

    session.close()

    date_query_results = list(np.ravel(results))

    return jsonify(date_query_results)

if __name__ == '__main__':
    app.run(debug=True)
