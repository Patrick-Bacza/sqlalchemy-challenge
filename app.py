import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from collections import OrderedDict
from flask import Flask, jsonify
import datetime as dt

#Database setup 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect hawaii  database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save References to tables
measurement = Base.classes.measurement
station = Base.classes.station

# Flask Setup
app = Flask(__name__)
#Prevent flask from sorting  dictionary keys alphabetically
app.config['JSON_SORT_KEYS'] = False

#Flask Routes
# Creat welcome page with available routes
@app.route("/")
def welcome():
    "List of available routes"
    return(
        f"Welcome to the Climate API! The available routes are:<br/>"
        f" <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate<br/>"
        f"<br/>"
        f"*Date Format: YYYY-MM-DD"
    )
# Create route to precipitation data spanning the last year of data

@app.route("/api/v1.0/precipitation")

# Function that grabs precipitation data between 2016-08-23 and 2017-08-23 and creates a dictionary to the data
def precipitation():

    session = Session(engine)

# Query find the most recent date in the dataset
    last_date_row = session.query(measurement.date).order_by(measurement.date.desc()).first()

    last_date = dt.date.fromisoformat(last_date_row[0])

# Finds the date a year prior to the most recent
    first_date = last_date - dt.timedelta(days=365)

###  Query that grabs the last year of precipitation data

    results = session.query(measurement.date , measurement.prcp)\
        .filter(measurement.date.between(first_date , last_date))\
        .order_by(measurement.date).all()
    
    session.close()

# Create dictionary 
    measurement_dict = {}

    for row in results:
        measurement_dict.update({row[0] : row[1]})
        

    return measurement_dict

### Returns a list of dictionaries for each station

@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)

    results = session.query(station.id , station.station , station.name , station.latitude , 
                            station.longitude , station.elevation).all()
    
    session.close()
    
    # for loop to create list of station dictionaries

    # List of keys for the dicitonary
    keys = ['ID' , 'Station' , 'Name'  ,'Latitude' , 'Longitude'  , 'Elevation']

    # List to house the dictionaries

    stations = []

    for row  in results:
        station_dict = {}

        for key , i in zip(keys , row):
            station_dict[key] = i

        stations.append(station_dict)

    return jsonify(stations)

#Route for temperature date for station with most observations
@app.route("/api/v1.0/tobs")    

### Query to return tempertature data for the most active station between 2016-08-23 and 2017-08-23

def tobs():
    session = Session(engine)

# Query that finds the station with the most observations

    max_count = session.query(station.station , func.count(measurement.id))\
        .filter(station.station == measurement.station)\
        .group_by(station.name)\
        .order_by(func.count(measurement.id).desc())\
        .first()

    max_station = max_count[0]

# Query find the most recent date in the dataset
    last_date_row = session.query(measurement.date).order_by(measurement.date.desc()).first()

    last_date = dt.date.fromisoformat(last_date_row[0])

# Finds the date a year prior to the most recent
    first_date = last_date - dt.timedelta(days=365)

#Query returns the dats and temperatures for station with most observations between 2016-08-23 and 2017-08-23

    results = session.query(measurement.date , measurement.tobs)\
                    .filter(measurement.station == max_station)\
                    .filter(measurement.date.between(first_date , last_date))\
                    .all()
    
    session.close()

    all_temps = list(np.ravel(results))
    
    return jsonify(all_temps)


### Dynamic route for start date to end of dataset

@app.route("/api/v1.0/<start_date>")

def date_aggregations(start_date):

    session = Session(engine)
# Query finds the min, max and average temperature 
    results = session.query(func.min(measurement.tobs) , func.max(measurement.tobs), func.round(func.avg(measurement.tobs),2))\
            .filter(measurement.date >= start_date).all()

    session.close()

    #Create dictionary to house results 
    agg_dict = {}
    keys = ['min_temperature' , 'max_temperature' , 'average_temperature']

    for row  in results:
        for i ,key in zip(row , keys):
            agg_dict[key] = i
    return agg_dict

  # Create route to grab aggregations for a specified time  period 
@app.route("/api/v1.0/<start_date>/<end_date>")

def time_periods(start_date , end_date):

    session = Session(engine)

# Query finds min, max and average tempature for a specified time period 

    results = session.query(func.min(measurement.tobs) , func.max(measurement.tobs), func.round(func.avg(measurement.tobs),2))\
            .filter(measurement.date.between(start_date , end_date)).all()

    session.close()

    #Create dictionary to house results 
    agg_dict = {}
    keys = ['min_temperature' , 'max_temperature' , 'average_temperature']

    for row  in results:
        for key , i in zip(keys , row):
            agg_dict[key] = i   
    
    return(agg_dict)


if __name__ == '__main__':
    app.run(debug=True)

