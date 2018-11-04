**An NBA player ranker**
This application allows a user create a list of NBA players, where users can also assign a ranking to that player
We call upon an API (hosted by nba.net) to fetch the models.


**Requirements/Packages**
flask
flask_wtf
wtforms
wtforms
flask_sqlalchemy
config
requests


**Description of routes -> pages**
'/' => a list of players added, as well as a form to add a player and ranking
  index() => routes to our index method, which contains a form to adding a player
             and the ranking for that player and creates objects for Player
'/rankings' => a list of the players added, sorted by rank
  rankings() => routes to our rankings, grabs all players and sorts by ranking
'/teams' => a list of all the teams
  teams() => routes to our rankings, fetches all added players and sorts by ranking
'/allstars' => a list of allstar coaches and players
  'allstars()' => calls a helper method to populate allstarcoach and allstar models


**Sources**
https://www.quora.com/Is-there-an-NBA-API-for-free-that-has-live-stats
https://stackoverflow.com/questions/17178483/how-do-you-send-an-http-get-web-request-in-python
https://stackoverflow.com/questions/6797984/how-to-lowercase-a-string-in-python
http://flask-sqlalchemy.pocoo.org/2.3/models/
