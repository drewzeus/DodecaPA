#! /usr/bin/bash

echo installing JACK and JACK tools
pushd ~

sudo apt-get -y install jackd2
sudo apt-get -y install jack-keyboard
sudo apt-get -y install python-pip3
sudo apt-get -y install xdotool

sudo apt -y install jack-midi-clock

pip3 install dbus-python
pip3 install JACK-client


#cadence
echo installing cadence
sudo adduser $(whoami) audio
sudo apt-get -y install libjack-jackd2-dev qtbase5-dev qtbase5-dev-tools
sudo apt-get -y install python3-pyqt5 python3-pyqt5.qtsvg pyqt5-dev-tools

sudo apt-get -y install python3-dbus
sudo apt -y install python3-dbus.mainloop.pyqt5

sudo apt -y install a2jmidid
sudo apt -y install jack-capture
sudo apt -y install pulseaudio
sudo apt -y install pulseaudio-module-jack
sudo apt-get -y install libboost-all-dev

wget https://github.com/falkTX/Cadence/archive/master.zip
unzip master.zip
pushd Cadence-master
make
sudo make install
pushd ~

pushd Downloads
wget https://github.com/falkTX/Carla/archive/v2.2.0.tar.gz
tar -xf v2.2.0.tar.gz
pushd Carla-2.2.0
make
sudo make install
pushd ~
echo cadence installed


#patchage
echo installing patchage
sudo apt -y install build-essential libdbus-glib-1-dev libgirepository1.0-dev
sudo apt-get -y install glibmm-2.4
sudo apt-get -y install gtkmm-2.4
pushd /home/$(whoami)
wget http://download.drobilla.net/ganv-1.8.0.tar.bz2
tar -xf ganv-1.8.0.tar.bz2
pushd ganv-1.8.0
sudo ./waf configure
sudo ./waf
sudo ./waf install
pushd /home/$(whoami)
wget http://download.drobilla.net/patchage-1.0.4.tar.bz2
tar -xf patchage-1.0.4.tar.bz2
pushd patchage-1.0.4
sudo ./waf --no-alsa configure
sudo ./waf
sudo ./waf install
pushd /home/$(whoami)
sudo rm -R patchage-1.0.4
sudo rm patchage-1.0.4.tar.bz2
sudo rm -R ganv-1.8.0
sudo rm ganv-1.8.0.tar.bz2
echo patchage installed


