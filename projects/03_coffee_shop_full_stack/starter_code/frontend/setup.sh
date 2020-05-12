export PROJ_DIR=`pwd`

# install node.js on Unbuntu
curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt-get install -y nodejs

# use `sudo` on Ubuntu or run this as root on debian
sudo apt-get install -y build-essential

# install from packag.js
cd $PROJ_DIR
npm install

# Install ionic
npm uninstall -g ionic
npm install -g @ionic/cli

# run development server
npm start
