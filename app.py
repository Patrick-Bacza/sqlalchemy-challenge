import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#Database setup 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save References to tables
measurement = Base.classes.measurement
station = Base.classes.station

# Flask Setup
app = Flask(__name__)

#Flask Routes

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

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    results = session.query(measurement.date , measurement.prcp)\
        .filter(measurement.date.between('2016-08-23' , '2017-08-23'))\
        .order_by(measurement.date).all()
    
    session.close()

    measurement_dict = {}

    for row in results:
        measurement_dict.update({'Date' : 'Precipitation(in.)'})
        measurement_dict.update({row[0] : row[1]})

    return jsonify(measurement_dict)

    



if __name__ == '__main__':
    app.run(debug=True)

