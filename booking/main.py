from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Resource, Api
from flask_restx import fields
from flask_restx import inputs
from flask_restx import reqparse
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
import copy
import requests
import json


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://root:root@dbbooking/main'
db = SQLAlchemy(app)
engine = create_engine('postgresql://root:root@dbbooking/main')
Session = sessionmaker(bind = engine)
session = Session()


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100))
    ticketid = db.Column(db.Integer)
    

@app.route('/timeslots/<timeslotsid>/order', methods = ['POST'])
def book_ticket(timeslotsid):
    if request.method == 'POST':
        request_data = request.get_json()
        res_body = json.dumps(request_data)
        headers = {'Content-Type' : 'application/json'}
        print(res_body)
        res = requests.post("http://project2_backend_1:5000/timeslots/<{}>/order".format(timeslotsid), data=res_body, headers=headers)
        return 200
        # return {"return": request_data}, 200


@app.route('/timeslots/<timeslotsid>/orderUpdate', methods = ['POST'])
def update_booking(timeslotsid):
    if request.method == 'POST':
        request_data = request.get_json()
        usrname = request_data['username'].lower()
        with engine.connect() as con:
            for tkid in request_data['ticket ID']:
                q_str = "INSERT INTO booking(username, ticketid) VALUES('{}', {});".format(usrname, tkid)
                con.execute(q_str)
        return 200


@app.route('/timeslots/<timeslotsid>/orderCancel', methods = ['POST'])
def cancel_ticket(timeslotsid):
    if request.method == 'POST':
        request_data = request.get_json()
        res_body = json.dumps(request_data)
        headers = {'Content-Type' : 'application/json'}
        res = requests.post("http://project2_backend_1:5000/timeslots/<{}>/order".format(timeslotsid), data=res_body, headers=headers)
        usrname = request_data["username"]
        with engine.connect() as con:
            q_str = "DELETE FROM booking WHERE LOWER(username) = LOWER('{}');".format(usrname)
            con.execute(q_str)
        return 200
        # return {"return": request_data}, 200


@app.before_first_request
def create_tables():
    print("---------------------------------------")
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
