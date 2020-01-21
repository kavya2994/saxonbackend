sudo yum -y install git
sudo adduser backend
sudo mkdir -p ~backend/.ssh
touch $HOME/.ssh/authorized_keys
sudo sh -c "cat $HOME/.ssh/authorized_keys >> ~backend/.ssh/authorized_keys"
sudo chown -R backend: ~backend/.ssh
sudo chmod 700 ~backend/.ssh
sudo sh -c "chmod 600 ~backend/.ssh/*"
sudo mkdir -p /var/www
sudo chown backend: /var/www
sudo -u backend -H git clone --branch=master git@github.com:mousavian/backend-0.git /var/www
