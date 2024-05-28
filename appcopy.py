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
# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement

Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Find the most recent date in the data set.
recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

# Calculate the date one year from the last date in data set.
query_date = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=366)

#################################################
# Flask Routes
#################################################
# Home route
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query precipitation data
    precipitation = session.query(Measurement.date, Measurement.prcp).all()
    
    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitations
    all_precipitations = []
    for date, prcp in precipitation:
        precipitation_dict= {}
        precipitation_dict["key"]= date
        precipitation_dict["prcp"]= prcp
        all_precipitations.append(precipitation_dict)

    # Return the JSON representation of your dictionary
    return jsonify(all_precipitations)


# Station route
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    stations = session.query(Station.station).all()
    
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(stations))

    # Return a JSON list of stations from the dataset
    return jsonify(all_stations)


# Tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most active station 
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()[0][0]

    # Query the last 12 months of temperature observation data for this station
    last_12_months_temp = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > query_date).\
            filter(Measurement.station == most_active_station).all()

    session.close()

    # Create a dictionary from the row data and append to a list of last_year_temp_list
    last_year_temp_list = []
    for date, temperature in last_12_months_temp:
        tempt_dict= {}
        tempt_dict["date"]= date
        tempt_dict["temperature"]= temperature
        last_year_temp_list.append(tempt_dict)

    # Return the JSON representation of your dictionary
    return jsonify(last_year_temp_list)


@app.route("/api/v1.0/<start>")
def temperature_by_start_date(start):
    temp_stats = session.query(func.min(Measurement.tobs),
                               func.max(Measurement.tobs),
                               func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    # Convert list of tuples into normal list
    temp_start = list(np.ravel(temp_stats))

     # Return the JSON representation of your dictionary
    return jsonify(temp_start)

if __name__ == '__main__':
    app.run(debug=True)
