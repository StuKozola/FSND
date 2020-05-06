export PROJ_DIR=`pwd`
# install flask
cd ~
sudo pip3 install Flask

# install postgresql
echo 'deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main' > /etc/apt/sources.list.d/pgdg.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# start the service under root
service postgresql start

# setup database
sudo -u postgres psql -c "SELECT version();"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
sudo -u postgres createdb trivia
sudo -u postgres psql trivia < trivia.psql

# create virtual envinroment
cd $PROJ_DIR
echo $PROJ_DIR
sudo apt-get install python3-venv    # If needed
python3 -m venv env
source env/bin/activate

# install dependencies for project
pip3 install --upgrade pip
pip3 install wheel
pip3 install -r requirements.txt --upgrade
pip3 install pep8
pip3 install pylint

# run development server
#sudo su - postgres
export FLASK_APP=flaskr
export FLASK_ENV=development # enables debug mode
flask run