# udacity-linux-server-configuration

This is the final project for "Full Stack Web Developer Nanodegree" on Udacity. 

In this project, a Linux virtual machine needs to be configurated to support the Item Catalog website.

You can visit http://54.238.238.153/ for the website deployed.

## You may refer this Udacity course

1. https://www.udacity.com/course/configuring-linux-web-servers--ud299

## Instructions for SSH access to the instance
(If you're on Windows, use Git bash)
1. Download Private Key from the __SSH keys__ section in the __Account__ section on Amazon Lightsail.
2. Move the private key file into the folder `~/.ssh` (where ~ is your environment's home directory). So if you downloaded the file to the Downloads folder, just execute the following command in your terminal.
	```mv ~/Downloads/LightsailKey.pem ~/.ssh/```
3. Open your terminal and type in
	```chmod 400 ~/.ssh/LightsailKey.pem```
4. In your terminal, type in
	```ssh -i ~/.ssh/Lightsail-key.pem ubuntu@54.238.238.153```

## Create a new user named grader

1. `sudo adduser grader`
2. `sudo touch /etc/sudoers.d/grader`
3. `sudo nano /etc/sudoers.d/grader`, type in `grader ALL=(ALL:ALL) NOPASSWD:ALL`, save(`ctrl + o`) and quit(`ctrl + x`)

## Set ssh login using keys
(You may want to use 2 bash consoles. One for local, another for virtual ubuntu)

1. Generate keys on local machine using`ssh-keygen` ; then save the private key in `~/.ssh` on local machine as `graderKey`.
   (Type in what's given in the parenthesis as default, just replacing the `id_rsa` at the end with `graderKey`.)
2. Deploy public key on developement enviroment
    On your local machine:
    ```
    $ cat ~/.ssh/graderKey.pub
    ```
    Copy the public key(output) to your clipboard or temporary note.
    
	On your virtual machine:
	```
	$ su - grader
	$ mkdir .ssh
	$ touch .ssh/authorized_keys
	$ nano .ssh/authorized_keys
	```
	Paste the public key to the `.ssh/authorized_keys` file and save.
  
	```
	$ chmod 700 .ssh
	$ chmod 644 .ssh/authorized_keys
	```
	
3. reload SSH using `service ssh restart`
(Open another bash console, for virtual grader)
4. now you can use ssh to login with the new user you created

	`ssh -i ~/.ssh/graderKey grader@54.238.238.153`

## Update all currently installed packages
__Note__:This is on your virtual ubuntu

	sudo apt-get update
	sudo apt-get upgrade

You may get popups about the versions conflicting eachother. Choose to use the project manager's (Top option).

## Change the SSH port from 22 to 2200

1. Use `sudo nano /etc/ssh/sshd_config` and then change Port 22 to Port 2200 , save & quit.
2. Reload SSH using `sudo service ssh restart`

__Note:__ Remember to add and save port 2200 with _Application __as__ Custom and Protocol __as__ TCP_ in the Networking section of your instance on Amazon Lightsail. 

## Configure the Uncomplicated Firewall (UFW)

Configure the Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123)

	sudo ufw allow ssh
  	sudo ufw allow www
  	sudo ufw allow ntp
  	sudo ufw allow 2200/tcp
	sudo ufw allow 80/tcp
	sudo ufw allow 123/udp
    sudo ufw deny 22
	sudo ufw enable 
  	sudo ufw status
 
## Configure the local timezone to UTC

1. Configure the time zone `sudo dpkg-reconfigure tzdata`
2. Check with `date` command.

## Install and configure Apache to serve a Python mod_wsgi application

1. Install Apache `sudo apt-get install apache2`
2. Install mod_wsgi `sudo apt-get install python-setuptools libapache2-mod-wsgi`
3. Restart Apache `sudo service apache2 restart`

## Install and configure PostgreSQL

1. Install PostgreSQL `sudo apt-get install postgresql`
2. Check if no remote connections are allowed `sudo vi /etc/postgresql/9.3/main/pg_hba.conf`
    At the end of file, it should look like this with additional comments. (Removed comments for simplicity in this README)
    ```
    local   all             postgres                                peer
    local   all             all                                     peer
    host    all             all             127.0.0.1/32            md5
    host    all             all             ::1/128                 md5
    ```
3. Login as user "postgres" `sudo su - postgres`
4. Get into postgreSQL shell `psql`
5. Create a new database named catalog  and create a new user named catalog in postgreSQL shell
	
	```
	postgres=# CREATE DATABASE catalog;
	postgres=# CREATE USER catalog;
	```
5. Set a password for user catalog
	
	```
	postgres=# ALTER ROLE catalog WITH PASSWORD 'password';
	```
6. Give user "catalog" permission to "catalog" application database
	
	```
	postgres=# GRANT ALL PRIVILEGES ON DATABASE catalog TO catalog;
	```
7. Quit postgreSQL `postgres=# \q`
8. Exit from user "postgres" 
	
	```
	exit
	```
## Set up your Catalog App project in Github.
1. Create a new repository called `forLinuxUdacity`
2. Clone your existing catalogUdacity project into the new repository.
3. Rename `application.py` to `__init__.py`, and edit the following lines.
`engine = create_engine('sqlite:///catalog.db')` to `engine = create_engine('postgresql://catalog:password@localhost/catalog')`
`app.run(host='0.0.0.0', port=8000)` to `app.run()`
`'client_secrets.json'` to `'/var/www/FlaskApp/FlaskApp/client_secrets.json'`
4. Edit `database_setup.py` and `fill_catalog.py` the same way as the first line above.

## Install git, clone and setup your Catalog App project in the virtual machine.
1. Install Git using `sudo apt-get install git`
2. Use `cd /var/www` to move to the /var/www directory 
3. Create the application directory `sudo mkdir FlaskApp`
4. Move inside this directory using `cd FlaskApp`
5. Clone the Catalog App to the virtual machine `git clone https://github.com/wonhyeongseo/forLinuxUdacity.git`
6. Rename the project's name `sudo mv ./forLinuxUdacity ./FlaskApp`
7. Move to the inner FlaskApp directory using `cd FlaskApp`
8. Install pip `sudo apt-get install python-pip`
9. Use pip to install dependencies -
	* `sudo pip install sqlalchemy flask-sqlalchemy psycopg2 bleach requests`
	* `sudo pip install flask packaging oauth2client redis passlib flask-httpauth`
10. Install psycopg2 `sudo apt-get -qqy install postgresql python-psycopg2`
11. Create database schema `sudo python database_setup.py`
12. Fill database `sudo pip install fill_catalog.py`


## Configure and Enable a New Virtual Host
1. Create FlaskApp.conf to edit: `sudo vi /etc/apache2/sites-available/FlaskApp.conf`
2. Add the following lines of code to the file to configure the virtual host. 
	
	```
	<VirtualHost *:80>
		ServerName fill_catalog.py
		ServerAdmin pesfy101@gmail.com
		WSGIScriptAlias / /var/www/FlaskApp/flaskapp.wsgi
		<Directory /var/www/FlaskApp/FlaskApp/>
			Order allow,deny
			Allow from all
		</Directory>
		Alias /static /var/www/FlaskApp/FlaskApp/static
		<Directory /var/www/FlaskApp/FlaskApp/static/>
			Order allow,deny
			Allow from all
		</Directory>
		ErrorLog ${APACHE_LOG_DIR}/error.log
		LogLevel warn
		CustomLog ${APACHE_LOG_DIR}/access.log combined
	</VirtualHost>
	```
3. Enable the virtual host with the following command: `sudo a2ensite FlaskApp`

## Create the .wsgi File
1. Create the .wsgi File under /var/www/FlaskApp: 
	
	```
	cd /var/www/FlaskApp
	sudo vi flaskapp.wsgi 
	```
2. Add the following lines of code to the flaskapp.wsgi file:
	
	```
	#!/usr/bin/python
	import sys
	import logging
	logging.basicConfig(stream=sys.stderr)
	sys.path.insert(0,"/var/www/FlaskApp/")

	from FlaskApp import app as application
	application.secret_key = 'super_secret_key'
	```

## Restart Apache
1. Restart Apache `sudo service apache2 restart `

## References:
1. Udacity's FSND Forum
2. https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
3. https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps
