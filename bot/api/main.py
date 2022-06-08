from flask import Flask, jsonify, abort, request, g
import json
import requests
from flask_cors import CORS, cross_origin
from wit import Wit
import random
import re
import os
import sys
import copy
# from dotenv import load_dotenv


# load_dotenv()
# API_KEY=os.getenv("API_KEY")

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
client = Wit("FXY4E2MNQBQ4VE3N3SUAIGJEJHOTYMRE")

MOVIE_NAME = ""
USERNAME = ""
BOOKING_INFO = {}
TIMESLOTID = 0

@app.route('/')
@cross_origin()
def index():
    msg = request.args.get("message")
    resp = client.message(msg)
    # The chatbot should be able to respond to basic greetings
    if resp['intents'][0]['name'] == 'greeting':
        list_of_rep = ['Hi! Can I ask what is your name?',
        'Hello! Can you please tell me your name?',
        'Good day! How about you tell me your name?',
        'Greetings! What can I call you?']
        reply = random.choice(list_of_rep)
        return jsonify({"message":reply})

    elif resp['intents'][0]['name'] == 'AskName':
        global USERNAME
        username = resp['entities']['UserName:UserName'][0]['body']
        USERNAME = username
        rep = "Hello {}. What can I do for you today?".format(USERNAME)
        return jsonify({"message": rep})
    # select movie
    elif resp['intents'][0]['name'] == 'SelectMovie':
        namem = resp['entities']['MovieName:MovieName'][0]['body']
        global MOVIE_NAME 
        if "\"" in namem:            
            MOVIE_NAME = namem.strip("\"")
        else:
            # global MOVIE_NAME 
            MOVIE_NAME = namem
        list_of_ans = ["Good choice. ", "Great choice. ", "Excellet choice. "]
        list_of_rep = ['How can I help you next?',
        'What can I do for you next?',
        'How can I assist next?']
        rep1 = random.choice(list_of_ans)
        rep2 = random.choice(list_of_rep)
        return jsonify({"message": rep1 + rep2})

    # The chatbot can list all the available cinemas
    elif resp['intents'][0]['name'] == 'GetAllCinema':        
        pr = {'status': 'available'}
        res = requests.get("http://project2_backend_1:5000/cinemas", params=pr)
        dict_result = json.loads(res.text)
        name_of_avai_cinemas = []
        for _ in dict_result['return']:
            name_of_avai_cinemas.append(_['name'])
        answer = "This is the list of available cinemas for the movie:\n"
        for _ in name_of_avai_cinemas:
            answer += _ + ',\n'

        return jsonify({"message": answer})

    # the user can ask for more details about cinema
    elif resp['intents'][0]['name'] == 'GetCinemaInfo':
        namec = resp['entities']['CinemaName:CinemaName'][0]['body']
        namecp = namec.lower()
        namec = namec.lower().replace(" ", "%20")
        res = requests.get("http://project2_backend_1:5000/cinemas/{}".format(namec))

        ret = json.loads(res.text)
        rep_str = "The {} locate at {} with maximum capacity {}. The contact number is {}. ".format(
            ret['return'][0]['name'], ret['return'][0]['address'],
            ret['return'][0]['capacity'], ret['return'][0]['phone'])


        pr2 = {'status': 'now showing'}
        res2 = requests.get("http://project2_backend_1:5000/cinemas/movies", params=pr2)  
        ret2 = json.loads(res2.text)
        cinema2 = ret2['return']
        for _ in cinema2:
            if _.lower() == namecp:
                list_str = ", ".join(cinema2[_])
        rep_str = rep_str + "The cinema is now showing " + list_str
        return jsonify({"message":rep_str})

    # Search cinemas by movie title
    elif resp['intents'][0]['name'] == 'SearchCinemaByTitle':
        namem = resp['entities']['MovieName:MovieName'][0]['body']
        if "\"" in namem:
            namem = namem.strip("\"")
        else:
            namem = namem
        pr = {'status': 'available', 'movie_title': f'{namem}'}
        res = requests.get("http://project2_backend_1:5000/cinemas", params=pr)
        dict_result = json.loads(res.text)
        name_of_avai_cinemas = []
        for _ in dict_result['return']:
            name_of_avai_cinemas.append(_)
        answer = "This is the list of available cinemas for the movie {}:\n".format(namem)
        for _ in name_of_avai_cinemas:
            answer += _ + ',\n'
        return jsonify({"message": answer})

    # The chatbot can check if the selected timeslot for a movie is available
    elif resp['intents'][0]['name'] == 'CheckAvailableTS':    
        timerange = resp['entities']['wit$datetime:datetime'][0]['body']
        seats = resp['entities']['Seat:Seat'][0]['body']
        movie = MOVIE_NAME

        pattern = '\d+'
        result = re.findall(pattern, timerange)
        starttime = result[0] + ':00'
        endtime = result[1] + ':00'

        if "\"" in movie:
            
            movie = movie.strip("\"")
        else:
            movie = movie
        new_movie_name = movie.lower().replace(" ", "%20")
        p4 = {'status': 'available', 'starttime': starttime, 'endtime': endtime}
        res = requests.get(f"http://project2_backend_1:5000/movies/{new_movie_name}/timeslots", params=p4)
        dict_result = json.loads(res.text)

        cinemas = ""
        for _ in dict_result['return']['cinema']:
            cinemas += _['name'] + ', '


        try:
            if int(seats) <= dict_result['return']['total available']:
                rep = f"Yes, there are enough seats in the {cinemas}for the movie {dict_result['return']['movie name']} from {starttime} to {endtime} pm."
            else:
                p5 = {'status': 'available'}
                res = requests.get(f"http://project2_backend_1:5000/movies/{new_movie_name}/timeslots", params=p5)
                dict_result = json.loads(res.text)
                ret_str = "There are not enough seat. All another available timeslots are: \n"
                for _ in dict_result['return']:
                    temp = "Start from {} pm to {} pm in cinema {}.\n".format(_['starttime'], _['endtime'], _['cinema'])
                    ret_str += temp
                rep = ret_str
        except:
            pass
        return jsonify({"message": rep})


    # The chatbot can provide a list of available timeslots for the selected movie
    elif resp['intents'][0]['name'] == 'ListAvaiTS':
        movie = MOVIE_NAME
        if "\"" in movie:
            
            movie = movie.strip("\"")
        else:
            movie = movie
        new_movie_name = movie.lower().replace(" ", "%20")
        p5 = {'status': 'available'}
        res = requests.get(f"http://project2_backend_1:5000/movies/{new_movie_name}/timeslots", params=p5)
        dict_result = json.loads(res.text)
        ret_str = "List of all available timeslots are: \n"
        for _ in dict_result['return']:
            temp = "Start from {} pm to {} pm in cinema {}.\n".format(_['starttime'], _['endtime'], _['cinema'])
            ret_str += temp
        return jsonify({"message": ret_str})

    elif resp['intents'][0]['name'] == 'ChooseTS':
        timerange = resp['entities']['wit$datetime:datetime'][0]['body']
        seats = resp['entities']['Seat:Seat'][0]['body']
        typetk = resp['entities']['TypeOfTicket:TypeOfTicket'][0]['body']
        print(resp)
        print(typetk)
        movie = MOVIE_NAME

        pattern = '\d+'
        result = re.findall(pattern, timerange)
        starttime = result[0] + ':00'
        endtime = result[1] + ':00'

        if "\"" in movie:
            
            movie = movie.strip("\"")
        else:
            movie = movie
        new_movie_name = movie.lower().replace(" ", "%20")
        p4 = {'status': 'available', 'starttime': starttime, 'endtime': endtime}
        res = requests.get(f"http://project2_backend_1:5000/movies/{new_movie_name}/timeslots", params=p4)
        dict_result = json.loads(res.text)
        print(dict_result)
        timeslotID = dict_result['return']['cinema'][0]['time slot id']

        post_body = {}
        post_body['movie name'] = movie
        post_body['username'] = USERNAME
        post_body['cinema name'] = dict_result['return']['cinema'][0]['name']
        post_body['number of tickets'] = int(seats)
        post_body['ticket type'] = str(typetk)
        post_body['timeslotID'] = timeslotID
        global BOOKING_INFO
        BOOKING_INFO = post_body
        global TIMESLOTID
        TIMESLOTID = timeslotID


        res_body = json.dumps(post_body)
        headers = {'Content-Type' : 'application/json'}

        res = requests.post("http://booking_booking_1:5000/timeslots/<{}>/order".format(timeslotID), data=res_body, headers=headers)
        
        return jsonify({"message": 'Your order is success'}), 200

    elif resp['intents'][0]['name'] == 'CancelOrder':
        res_body = json.dumps(BOOKING_INFO)
        headers = {'Content-Type' : 'application/json'}

        res = requests.post("http://booking_booking_1:5000/timeslots/<{}>/orderCancel".format(TIMESLOTID), data=res_body, headers=headers)

        return jsonify({"message": 'Your booking has been successfully canceled'}), 200

    elif resp['intents'][0]['name'] == 'GetSnack':
        namec = resp['entities']['CinemaName:CinemaName'][0]['body']
        cinema_name = copy.copy(namec)
        namec = namec.lower().replace(" ", "%20")
        res = requests.get("http://project2_backend_1:5000/cinemas/{}/snacks".format(namec))
        dict_result = json.loads(res.text)
        str1 = ", ".join(dict_result['return'])
        rep = "In {}, we have ".format(cinema_name) + str1 + '.'
        return jsonify({"message": rep}), 200

    else:
        return jsonify({"message":'I do not get what you mean. Can you say it again?'})
    

# @app.route('/api1')
# def internal():
#     res = requests.get("http://project2_backend_1:5000/api")
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
