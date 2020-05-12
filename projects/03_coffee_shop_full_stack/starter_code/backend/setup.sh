export PROJ_DIR=`pwd`
# install flask
cd ~
sudo pip3 install Flask

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
export FLASK_APP=api.py
export FLASK_ENV=development # enables debug mode
flask run --reload