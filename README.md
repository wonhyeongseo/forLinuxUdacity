# catalog_udacity
## About
This is source code for a simple item catalog powered by [Flask](http://flask.pocoo.org/docs/0.12/quickstart/).
It implements a basic JSON endpoint, which can be seen by clicking the "JSON" button next to the header.
In addition, it uses sqlalchemy to read and write from a minimal database- containing tables called 
User, Category, and Item. Forms are used to add, edit and delete items from the catalog. 
It also utilizes a third-party signin via [Google Signin](https://developers.google.com/identity/sign-in/web/devconsole-project).

## Requirements
[Git](https://git-scm.com/)
Vagrant (Most recent)
VirtualBox (Most recent) **Be sure to set [Intel Virtual Technology](http://bce.berkeley.edu/enabling-virtualization-in-your-pc-bios.html) to enabled in the BIOS. **

The packages below are all available when you set up a Virtual Machine with the Vagrantfile in this
repository.

Flask 0.12.2
Python 2.7.12
Sqlalchemy 1.1.15

## Project Contents
static(blank_user.gif, styles.css, top-banner.jpg)
templates(
    addItem.html
    catalog.html
    category.html
    deleteItem.html
    editItem.html
    header.html
    item.html
    login.html
    main.html
    page_not_found.html
)
application.py
database_setup.py
lotsofitems.py
README.md

## Installation Instructions
1. Clone this repository to your computer.
2. Open Git CMD, and move to your cloned directory.
3. Type "vagrant up", and after installation is complete, "vagrant ssh", and after logged in, "cd /vagrant".
4. Please go through the instructions in this [website](https://developers.google.com/identity/sign-in/web/devconsole-project), but at step 5, set the authorized javascript origins field as "http://localhost:5000" and authorized redirect uris as "http://localhost:5000/login" and "http://localhost:5000/catalog"; then continue.
5. Click the download button below the trash can button, rename the file as "client_secrets.json", and put it your directory.
6. Copy the Client ID, and replace two "<YOUR-CLIENT-ID>" with it in the login.html in the templates folder.
<meta name="google-signin-client_id" content="<YOUR-CLIENT-ID>">
client_id: '<YOUR-CLIENT-ID>'

## Operating Instructions
1. Type in to your Git CMD, "python database_setup.py" to run the database setup.
2. Type in to your Git CMD, "python lotsofitems.py" to populate the database.
3. Finally, run the application by typing in "python application.py" into your logged in Git CMD.
4. The app will be running at "http://localhost:5000". Thank you for using this app. 

This will be used as boilerplate code for a future project of mine.
