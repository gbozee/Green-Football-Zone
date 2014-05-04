Green-Football-Zone
===================

Social Soccer Form


There are two sections of the app. The initial website which exposes the api and the mobile 
app being built with phonegap.

For the website which exposes the api, you will need google app engine

As a result of poor documentation on my path, some of the api exposed 
to the client from the server are as follows

GET /mobile/v1.0/topics/{topic_id}
POST /mobile/v1.0/topic/{topic_id}/replies
GET /mobile/v1.0/topics/{topic_id}/replies
GET /api/v2.0/leagues
POST /api/v2.0/leagues
POST /mobile/v1.0/connect
GET /mobile/v1.0/api/token
GET /mobile/v1.0/me/profile
POST /api/v2.0/teams
GET /api/v2.0/leagues/{team_name}/teams
GET /mobile/v1.0/my-teams

The main file to study the api access is the client_auth.py and breeze_api.py



for the mobile phonegap app, I made use of ionic framework so you would need to install
ionic from npm globally

You would need to create a new ionic project and coppy the www, and plugins directory into it.

The javascript framework used for the mobile app is angularjs so you should be familiar with
it.

i Hope you would be able to continue with the project.

links to help
http://ionicframework.com/docs/
https://angularjs.org/
http://cordova.apache.org
https://developers.google.com/appengine/docs/python/
http://flask.pocoo.org/docs/

