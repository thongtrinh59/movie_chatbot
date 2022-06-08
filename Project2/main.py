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
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://root:root@db/main'
db = SQLAlchemy(app)
engine = create_engine('postgresql://root:root@db/main')
Session = sessionmaker(bind = engine)
session = Session()

# building model
class Cinema(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    snack = db.Column(db.String(200))
    capacity = db.Column(db.Integer)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(500))
    actors = db.Column(db.String(500))
    duration = db.Column(db.Integer)

class Timeslots(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mid = db.Column(db.Integer)
    cid = db.Column(db.Integer)
    starttime = db.Column(db.String(100))
    endtime = db.Column(db.String(100))
    # days = db.Column(db.String(100))

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timeslotid = db.Column(db.Integer)
    typeticket = db.Column(db.String(50))
    seat = db.Column(db.Integer)
    status = db.Column(db.String)

# Get available cinemas
@app.route('/cinemas')
def get_avai_cinema():
    parser = reqparse.RequestParser()
    parser.add_argument('status', type=str,  required=False)
    parser.add_argument('movie_title', type=str,  required=False)
    
    args = parser.parse_args()
    # get all avalable cinemas
    if args['status'] is not None and args['movie_title'] is None:
        list_of_avai_cinema = []

        with engine.connect() as con:
            q_str = "SELECT * FROM cinema;"
            rs = con.execute(q_str)
            for _ in rs:
                dict_result = {
                    "id": _.id,
                    "name": _.name,
                    "address": _.address,
                    "phone": _.phone,
                    "snack": _.snack,
                    "capacity": _.capacity
                }
                list_of_avai_cinema.append(dict_result)

        return jsonify({'return': list_of_avai_cinema}), 200

    # search cinemas by movie title
    if args['status'] is not None and args['movie_title'] is not None:
        result = []
        with engine.connect() as con:
            q_str = "SELECT DISTINCT(c.name) FROM movie as m,  \
                timeslots as t, cinema as c WHERE m.id = t.mid AND \
                c.id = t.cid AND LOWER(m.title) = LOWER('{}');".format(args['movie_title'])

            rs = con.execute(q_str)
            for row in rs:
                result.append(row.name)
        return jsonify({'return': result}), 200
        
@app.route('/cinemas/<cinemaname>')
def get_info_cinema(cinemaname):
    list_cinema_by_name = []
    with engine.connect() as con:
        q_str = "SELECT * FROM cinema WHERE LOWER(name) = LOWER('{}');".format(cinemaname)
        rs = con.execute(q_str)
        for _ in rs:
            dict_result = {
                "id": _.id,
                "name": _.name,
                "address": _.address,
                "phone": _.phone,
                "snack": _.snack,
                "capacity": _.capacity
            }
            list_cinema_by_name.append(dict_result)
    return jsonify({'return': list_cinema_by_name}), 200

@app.route('/cinemas/movies')
def find_now_showing_movie():
    parser = reqparse.RequestParser()
    parser.add_argument('status', type=str, required=False)
    args = parser.parse_args()

    if args['status'] == 'now showing':
        with engine.connect() as con:
            q_str = "SELECT c.name, m.title FROM movie as m,  \
                timeslots as t, cinema as c WHERE m.id = t.mid AND c.id = t.cid;"
            rs = con.execute(q_str)
            dict_result = {}
            for _ in rs:
                if _.name not in dict_result.keys():
                    dict_result[_.name] = []
                else:
                    dict_result[_.name].append(_.title)
    return jsonify({'return': dict_result})


@app.route('/movies/<moviename>/timeslots')
def find_available_ticket(moviename):
    parser = reqparse.RequestParser()
    parser.add_argument('status', type=str, required=False)
    parser.add_argument('starttime', type=str, required=False)
    parser.add_argument('endtime', type=str, required=False)

    args = parser.parse_args()

    if args['starttime'] is not None and args['endtime'] is not None:

        ticket_status = args['status']
        startTime = args['starttime']
        endTime = args['endtime']
        with engine.connect() as con:
            q_str = "SELECT c.name, m.title, t.starttime, t.endtime, t.id, tk.seat, tk.status, \
                        tk.typeticket FROM movie as m, timeslots as t, cinema as c, ticket as tk  \
                        WHERE m.id = t.mid AND c.id = t.cid AND t.id = tk.timeslotid \
                        AND tk.status = '{}' AND LOWER(m.title) = LOWER('{}') \
                        AND t.starttime = '{}' AND t.endtime = '{}';".format(ticket_status,
                        moviename, startTime, endTime)
            rs = con.execute(q_str)
            # print(rs[1])

            count = 0
            set_of_tuple = set()
            temp_dict = {} 
            for _ in rs:
                count += 1
                temp_str = _.name + "****" + str(_.id) + "++++" + _.typeticket
                if temp_str not in set_of_tuple:
                    set_of_tuple.add(temp_str)
                    temp_dict[temp_str] = 1
                else:
                    temp_dict[temp_str] += 1
            new_dict = {}
            for item in temp_dict.items():
                str_split = item[0].split("++++")
                new_str = str_split[1] + "++++" + str(item[1])

                if str_split[0] not in new_dict.keys():
                    new_dict[str_split[0]] = [new_str]

                else:
                    new_dict[str_split[0]].append(new_str)

            gg = []
            for item in new_dict.items():
                hh_dict = {}
                tt_dict = {}
                for j in item[1]:
                    str_split = j.split("++++")
                    tt_dict[str_split[0]] = int(str_split[1])

                jjj = item[0].split("****")    

                hh_dict['name'] = jjj[0]
                hh_dict['time slot id'] = int(jjj[1])
                hh_dict['ticket'] = tt_dict
                gg.append(hh_dict)

            final = {}
            final["movie name"] = moviename
            final["total available"] = count
            final["time slot"] = [startTime, endTime]
            final["cinema"] = gg
            print(final)

        return jsonify({'return': final}), 200

    else:
        ticket_status = args['status']

        with engine.connect() as con:
            q_str = "SELECT c.name, t.starttime, t.endtime, count(seat) \
                    FROM movie as m, timeslots as t, cinema as c, ticket as tk \
                    WHERE m.id = t.mid AND c.id = t.cid AND t.id = tk.timeslotid \
                    AND tk.status = '{}' AND LOWER(m.title) = LOWER('{}') \
                    GROUP BY name, starttime, endtime;".format(ticket_status, moviename)
            rs = con.execute(q_str)

            list_result = []
            temp_dict = {}
            for _ in rs:
                temp_dict['cinema'] = _.name
                temp_dict['starttime'] = _.starttime
                temp_dict['endtime'] = _.endtime
                temp_dict['seat available'] = _.count
                tt = copy.copy(temp_dict)
                list_result.append(tt)

        return jsonify({'return': list_result}), 200



@app.route('/cinemas/<cinemaname>/snacks')
def find_snack_in_cinema(cinemaname):    
    with engine.connect() as con:
        q_str = "SELECT snack FROM cinema WHERE LOWER(name) = LOWER('{}')".format(cinemaname)
        rs = con.execute(q_str)
        for _ in rs:
            snack_str = _.snack
            snack_list = snack_str.split(", ")
            
    return jsonify({"return": snack_list}), 200


# internal api
@app.route('/timeslots/<timeslotsid>/order', methods=['POST'])
def order_ticket(timeslotsid):

    if request.method == 'POST':
        request_data = request.get_json()

        ticket_type = request_data["ticket type"]
        num_ticket = request_data["number of tickets"]
        timeslotID = request_data["timeslotID"]
        print(ticket_type)
        ticket_type = str(ticket_type)
        with engine.connect() as con:
            q_str = "SELECT tk.id AS tkid, tk.seat, tk.status, tk.typeticket, t.id FROM timeslots as t, ticket as tk \
                        WHERE t.id = tk.timeslotid AND t.id = {} AND tk.status = 'available' \
                        AND LOWER(tk.typeticket) = LOWER('{}');".format(timeslotID, ticket_type)
            rs = con.execute(q_str)
            temp_list = []
            for _ in rs:
                temp_list.append((_.seat, _.tkid))
            print(temp_list)
            new_list = temp_list[0:num_ticket]

            for id2 in new_list:
                q_str2 = "UPDATE ticket SET status = 'booked' WHERE seat = {};".format(id2[0])
                con.execute(q_str2)
            return_tkid = []
            for _ in new_list:
                return_tkid.append(_[1])

        headers = {'Content-Type': 'application/json'}
        rt_body = json.dumps({"ticket ID": return_tkid, "username": request_data['username']})
        res = requests.post("http://booking_booking_1:5000/timeslots/<{}>/orderUpdate".format(timeslotID), data=rt_body, headers=headers)

    return 200

# cancel order
@app.route('/timeslots/<timeslotsid>/orderCancel', methods = ['POST'])
def cancel_ticket(timeslotsid):
    if request.method == 'POST':
        request_data = request.get_json()

        ticket_type = request_data["ticket type"]
        num_ticket = request_data["number of tickets"]
        timeslotID = request_data["timeslotID"]

        with engine.connect() as con:
            q_str = "SELECT tk.id AS tkid, tk.seat, tk.status, tk.typeticket, t.id FROM timeslots as t, ticket as tk \
                        WHERE t.id = tk.timeslotid AND t.id = {} AND tk.status = 'booked' \
                        AND tk.typeticket = '{}';".format(timeslotID, ticket_type)
            rs = con.execute(q_str)
            temp_list = []
            for _ in rs:
                temp_list.append((_.seat, _.tkid))
            new_list = temp_list[0:num_ticket]
            for id2 in new_list:
                q_str2 = "UPDATE ticket SET status = 'available' WHERE seat = {};".format(id2[0])
                con.execute(q_str2)
        return {"return": "ok"}, 200


# @app.before_first_request
# def create_tables():
#     print("---------------------------------------")
#     db.create_all()
#     db.session.commit()


if __name__ == '__main__':
    
    app.run(debug=True, host='0.0.0.0')
