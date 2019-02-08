#!/usr/bin/env python
from flask import Flask, jsonify, render_template, redirect, request, url_for, flash

# importing SqlAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Movie
from flask import session as login_session

#importing json
import json

# importing oauth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# to create anit-forgery state token
import random
import string
import httplib2

from flask import make_response
import requests

app = Flask(__name__)

# Connect to Database and create database session
connect_args = {'check_same_thread': False}
engine = create_engine('sqlite:///MovieCatalog.db',connect_args=connect_args)
#engine = create_engine('sqlite:///MovieCatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# helper method to query all movie categories
def queryAllCateogries():
    movies = session.query(Movie).all()
    categories = []
    for movie in movies:
        if movie.category not in categories:
            categories.append(movie.category)
    return categories


# Main page to show movies catalog
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    #movies = session.query(Movie).all()
    categories = queryAllCateogries()
    latestMovies = session.query(Movie).order_by(
        Movie.movieID.desc()).limit(10)
    if 'username' not in login_session:
        return render_template('publicCatalog.html', categories=categories, latestMovies=latestMovies)
    else:
        return render_template('catalog.html', categories=categories, latestMovies=latestMovies)
    #return render_template('catalog.html', movies=movies)

# Query all movie items in one category
@app.route('/catalog/<string:category>/')
def queryCategory(category):
    categories = queryAllCateogries()
    movieItems = session.query(Movie).filter_by(category=category).all()
    return render_template('category.html', movieItems=movieItems, category=category, categories=categories)
    #return "This is to query all movie items in %s category in catalog." % category

# Show the detail of one movie
@app.route('/catalog/<string:category>/<int:movieID>/')
def movieDetail(category, movieID):
    movie = session.query(Movie).filter_by(category=category, movieID=movieID).first()
    if 'username' not in login_session:
        return render_template('publicDescription.html', movie=movie)
    else:
        return render_template('description.html', movie=movie)
    #return "This is to show the detail of movie item " + str(movieID) + " in %s ." % category


# Add a new movie in the catalog
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newMovie():
    if 'username' in login_session:
        # get input data from the form
        if request.method == 'POST':
            movieName=request.form['movieName']
            directorName=request.form['directorName']
            description=request.form['description']
            category=request.form['category']
            userId=login_session['userId']

            if movieName and directorName and description and category:
                newItem = Movie(movieName=movieName,
                                directorName=directorName,
                                description=description,
                                category=category,
                                userId=userId)
                session.add(newItem)
                session.commit()
                flash("New movie item added!")
                return redirect(url_for('showCatalog'))
            else: # user did not fill all fields
                flash("All fields are required!")
                return render_template('newItem.html')
        else:
            return render_template('newItem.html')
    else: # user not login yet
        flash("Please login first to add new movie item.")
        return redirect('/login')
    #return "This is new movie page."

# Edit the detail of one movie
@app.route('/catalog/<string:category>/<int:movieID>/edit/', methods=['GET', 'POST'])
def editMovieDetail(category, movieID):
    return "This is to edit the detail of %s movie " % category + str(movieID)

# Delete the movie
@app.route('/catalog/<string:category>/<int:movieID>/delete/', methods=['GET', 'POST'])
def deleteMovie(category, movieID):
    return "This is to delete the %s movie " % category + str(movieID)

#JSON endpoint
@app.route('/catalog.json/')
def catalogJSON():
     movies = session.query(Movie).all()
     return jsonify(Movies=[movie.serialize for movie in movies])
     #return "This is the JSON for movie catalog."

@app.route('/catalog/<string:category>.json/')
def queryCategoryJSON(category):
    movies = session.query(Movie).filter_by(category=category).all()
    return jsonify(Movies=[movie.serialize for movie in movies])
    #return "This is the JSON to query all %s movie items in catalog." % category

@app.route('/catalog/<string:category>/<int:movieID>.json/')
def movieDetailJSON(category, movieID):
    movie = session.query(Movie).filter_by(category=category, movieID=movieID).first()
    return jsonify(Movie=movie.serialize)
    #return "This is the JSON to show the detail of %s movie item "% category + str(movieID)

# **********************************
# Login to modify the movie catalog
# **********************************
# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(userId):
    user = session.query(User).filter_by(id=userId).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Login route, create anit-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    print "login_session state %s " % state
    return render_template('login.html', STATE=state)
    #return "This is to login to movie catalog."


# facebook signin
@app.route('/fbConnect', methods=['POST'])
def fbConnect():
    # print "Entering fbConnect method"
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v3.2/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    #************************************
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v3.2/me?access_token=%s&fields=name,id,email' % token
    #************************************
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    #************************************
    # Get user picture
    url = 'https://graph.facebook.com/v3.2/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]
    #************************************

    # see if user exists
    userId = getUserID(login_session['email'])
    if not userId:
        userId = createUser(login_session)
    login_session['userId'] = userId

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    #*************************
    flash("Now logged in as %s" % login_session['username'])
    #*************************
    return output
    #return "Signin to movie catalog with facebook account."

# Signout of movie catalog
@app.route('/fbDisconnect')
def fbDisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out"
    #return "Signout of movie catalog."


# Logout of movie catalog based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbDisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['userId']
        del login_session['provider']
        flash("You have successfully been logged out.")
        #return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
    return redirect(url_for('showCatalog'))
    #return "This is to logout of movie catalog."

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
