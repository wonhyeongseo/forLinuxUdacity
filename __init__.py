##########################################
# Project 5: Item Catalog Application
# Date Started: 12/15/2017
# Date Completed: 12/15/2017
# Submitted by: Wonhyeong Seo
##########################################
import os
import random
import string
import json
import httplib2
import requests
from flask import Flask, render_template, redirect, flash
from flask import make_response, abort, request, jsonify, url_for
from flask import session as login_session
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User
from oauth2client import client

app = Flask(__name__)

path = os.path.dirname(__file__)

CLIENT_ID = json.loads(open(path+'client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"


# Connect to Database and create database session
engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Preventing request forgery.
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits
        ) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['GET', 'POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # (Receive auth_code by HTTPS POST)
    auth_code = request.data

    # If request does not have `X-Requested-With` header, could be a CSRF
    if not request.headers.get('X-Requested-With'):
        abort(403)

    CLIENT_SECRET_FILE = 'client_secrets.json'

    # Exchange auth code for access token, refresh token, and ID token
    credentials = client.credentials_from_clientsecrets_and_code(
        CLIENT_SECRET_FILE,
        ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
        auth_code)

    # Call Google API
    email = credentials.id_token['email']

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={}'
           .format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user.
    userid = credentials.id_token['sub']
    if result['sub'] != userid:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.header['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['aud'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_userid = login_session.get('userid')
    if stored_access_token is not None and userid == stored_userid:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['userid'] = userid

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # See if user exists, if not make new.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    flash("you are now logged in as {}".format(login_session['username']))
    response = make_response(json.dumps('Successfully connected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


# User Helper Functions
def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route("/gdisconnect")
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        flash("Please log in before logging out.")
        return redirect(url_for('index'))
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(
        access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['userid']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        response = make_response(
            json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("You are now logged out.")
        return redirect(url_for('index'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        flash("Logout unsuccessful. Please try again.")
        return redirect(url_for('index'))


# JSON API Endpoint
@app.route('/catalog.json')
def catalogJSON():
    # Bring relevant data from database.
    categories = session.query(Category).all()
    categories = [c.serialize for c in categories]
    for c in categories:
        items = session.query(Item).filter_by(cat_name=c['name']).all()
        c['Item'] = [i.serialize for i in items]
    return jsonify(Category=categories)


# Error handling
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


@app.route('/')
@app.route('/catalog')
def index():
    categories = session.query(Category).all()
    recents = session.query(Item).order_by(desc(Item.id)).limit(10)
    return render_template(
        'catalog.html',
        categories=categories,
        recents=recents)


@app.route('/catalog/<path:category>/items')
def showItems(category):
    try:
        categories = session.query(Category).all()
        filteredItems = session.query(Item).filter_by(cat_name=category).all()
        count = len(filteredItems)
        return render_template('category.html',
                               category=category,
                               categories=categories,
                               items=filteredItems,
                               count=count)
    except:
        abort(404)


@app.route('/catalog/<path:category>/<path:item>')
def showItem(category, item):
    try:
        item = session.query(Item).filter_by(title=item).one()
        creator = getUserInfo(item.user_id)
        return render_template('item.html', item=item, creator=creator)
    except:
        abort(404)


@app.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        newItem = Item(
            title=request.form['title'],
            description=request.form['description'],
            cat_name=request.form['cat_name'],
            user_id=login_session['user_id']
        )
        if session.query(Item).filter_by(title=newItem.title).all():
            flash(
                "Item {} already exists. Please try editing.".format(
                    newItem.title))
            return redirect(url_for('index'))
        else:
            session.add(newItem)
            session.commit()
            flash("New item {} created.".format(newItem.title))
            return redirect(url_for('index'))
    else:
        categories = session.query(Category).all()
        return render_template('addItem.html', categories=categories)


@app.route('/catalog/<path:category>/<path:item>/edit',
           methods=['GET', 'POST'])
def editItem(category, item):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    try:
        itemToEdit = session.query(Item).filter_by(title=item).one()
        if itemToEdit.user_id != login_session['user_id']:
            flash("You are not authorized to edit item {}.".format(item.title))
            return redirect(url_for('index'))
        if request.method == 'POST':
            editedItem = itemToEdit
            if request.form['title']:
                itemToEdit.title = request.form['title']
            if request.form['description']:
                itemToEdit.description = request.form['description']
            if request.form['cat_name']:
                itemToEdit.cat_name = request.form['cat_name']
            session.add(itemToEdit)
            session.commit()
            editedItem = itemToEdit
            flash("Item {} successfully edited.".format(editedItem.title))
            return redirect(url_for('index'))
        else:
            categories = session.query(Category).all()
            return render_template(
                'editItem.html',
                item=itemToEdit,
                categories=categories)
    except:
        abort(404)


@app.route('/catalog/<path:category>/<path:item>/delete',
           methods=['GET', 'POST'])
def deleteItem(category, item):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    try:
        itemToDelete = session.query(Item).filter_by(title=item).one()
        if itemToDelete.user_id != login_session['user_id']:
            flash(
                "You are not authorized to delete item {}."
                .format(item.title))
            return redirect(url_for('index'))
        if request.method == 'POST':
            session.delete(itemToDelete)
            session.commit()
            deletedItem = itemToDelete
            flash("Item {} successfully deleted.".format(deletedItem.title))
            return redirect(url_for('index'))
        else:
            return render_template('deleteItem.html', item=itemToDelete)
    except:
        abort(404)

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run()
