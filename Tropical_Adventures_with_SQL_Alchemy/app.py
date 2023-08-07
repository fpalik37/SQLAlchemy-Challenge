# IMPORT DEPENDENCIES
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# DATABASE SETUP
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# REFLECT AN EXISTING DATABASE INTO A NEW MODEL
Base = automap_base()

# REFLECT THE TABLES
Base.prepare(autoload_with=engine)

# SAVE REFERENCES TO EACH TABLE
Measurement = Base.classes.measurement
Station = Base.classes.station

# CREATE SESSION (LINK) FROM PYTHON TO THE DATABASE
session = Session(engine)

# FLASK SETUP
app = Flask(__name__)


# FLAST ROUTES
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"        
        f"<p>'start' and 'end' date should be in the format MMDDYYYY"
        
    )
 
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data from last year"""
    # CALCULATE THE DATE 1 YEAR AGO FROM LAST DATE IN DATABASE
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    session=Session(engine)
    
    # QUERY FOR THE DATE AND PRECIPITATION FOR THE LAST YEAR
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year)
        
    session.close()    
    # DICTIONARY WITH DATE AS THE KEY AND PRECP AS THE VALUE
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations. """  
    
    session=Session(engine)
       
    results = session.query(Station.station).all()
    
    session.close()
    
    # UNRAVEL RESULTS INTO AN ID ARRAY AND CONVERT TO A LIST
    stations = list(np.ravel(results))
    return jsonify(stations=stations)
    
@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for the previous year."""
    session=Session(engine)
    # CALCULATE THE DATE 1 YEAR PREVIOUS TO LAST DATE IN DATABASE
    
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # QUERY THE PRIMARY STATION FOR ALL TOBS FROM THE LAST YEAR
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    session.close()

    # UNRAVEL RESULTS INTO AN ID ARRAY AND CONVERT TO A LIST
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVGE, TMAX."""
    session=Session(engine)
    
    # SELECT STATEMENT
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
 
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
         
        session.close()
         
        temps = list(np.ravel(results))
        return jsonify(temps)

    # CALCLULATE TMIN, TAVG, TMAX WITH START AND STOP
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
        
    session.close()    

    # UNRAVEL RESULTS INTO AN ID ARRAY AND CONVERT TO A LIST
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run()
    
######################################################################################################################
# PROGRAMMING NOTES:
# I implemented new session for each function. Resson being, when trying to run all functions withon one session,
# my server appeared to become overloaded - and would render a 500 error when trying back-to-back search endpoints.
# Giving each function in its own respective session fixed this.
######################################################################################################################


    