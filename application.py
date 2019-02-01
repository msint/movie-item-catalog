#!/usr/bin/env python
from flask import Flask

app = Flask(__name__)


# Main page to show movies catalog
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    return "This is main movies catalog page."

# Query all movie items in one category
@app.route('/catalog/<string:category>/')
def queryCategory(category):
    return "This is to query all movie items in %s category in catalog." % category

# Show the detail of one movie
@app.route('/catalog/<string:category>/<int:movieID>/')
def movieDetail(category, movieID):
    return "This is to show the detail of movie item " + str(movieID) + " in %s ." % category


# Add a new movie in the catalog
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newMovie():
    return "This is new movie page."

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
    return "This is the JSON for movie catalog."

@app.route('/catalog/<string:category>.json/')
def queryCategoryJSON(category):
    return "This is the JSON to query all %s movie items in catalog." % category

@app.route('/catalog/<string:category>/<int:movieID>.json/')
def movieJSON(category, movieID):
    return "This is the JSON to show the detail of %s movie item "% category + str(movieID)

# Login to modify the movie catalog
@app.route('/login')
def showLogin():
    return "This is to login to movie catalog."

# Logout of movie catalog
@app.route('/logout', methods=['post'])
def logout():
    return "This is to logout of movie catalog."

# google signin
@app.route('/gconnect', methods=['POST'])
def gConnect():
    return "Signin to movie catalog with google account."

# Signout of movie catalog
@app.route('/gdisconnect')
def gdisconnect():
    return "Signout of movie catalog."

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
