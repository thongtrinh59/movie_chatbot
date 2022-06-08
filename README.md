# movie_chatbot
1, Deployment
- There are 3 folders in the zip file which are “bot” for webhook and chat bot and front end, “Project2” for cinema, movie and timeslot database and “booking” for booking database.
- Firstly, change directory to “bot” folder and command:
Docker-compose up –build
- Secondly, change directory to “Project 2” folder and command:
Docker-compose up –build
- Thirdly, change directory to “booking” folder and command:
Docker-compose up –build
- The front end can be accessed by address in the browser: “localhost:3001” - To access wit.ai account, using this account

2, Usage instruction
- Firstly, you can start with normal greeting with bot such as “Hello”
“Hey, bot”
- Secondly, the bot can ask you name. The bot need information to determine who is booking order “My name is ABC”
- Next, you can start booking now by choosing the movie you want to order
“I want to book ticket for movie "Star War"”
- Then you can ask bot some question to get more information such as
+ List all available cinemas: “List all available cinemas”
+ Get cinema information: “Could you tell me about HOYTS?”
+ Search cinema by movie title: “Show me all the cinema with the movie "Star War"”
+ Get available snack in cinema: “List all available snack in HOYTS”
- After get enough information, you can check if selected timeslot is available and bot can suggest another timeslot if the timeslot is full:
 
“Do you have 5 seats available from 4-6 pm?”
- The chatbot can provide a list of available timeslots for the selected movie: “I need to know available timeslots for the chosen movie”
- Now with enough information, user can book seats, timeslot
“I want to choose 2 Saver seats with timeslot from 5-7pm in HOYTS”
- If you want to cancel the ticket, we can do:
“I want to cancel my order”
