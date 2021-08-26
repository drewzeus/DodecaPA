#! /usr/bin/bash
pushd ~/

echo installing dependecies
sudo apt-get install bison flex automake libasound2-dev
sudo apt-get install libjack-jackd2-dev libtool libbluetooth-dev libgl1-mesa-dev
sudo apt-get install libglu1-mesa-dev libglew-dev libmagick++-dev libftgl-dev
sudo apt-get install libgmerlin-dev libgmerlin-avdec-dev libavifile-0.7-dev
sudo apt-get install libmpeg3-dev libquicktime-dev libv4l-dev libraw1394-dev
sudo apt-get install libdc1394-22-dev libfftw3-dev libvorbis-dev ladspa-sdk
sudo apt-get install dssi-dev tap-plugins invada-studio-plugins-ladspa blepvco
sudo apt-get install swh-plugins mcp-plugins cmt blop slv2-jack omins rev-plugins
sudo apt-get install libslv2-dev dssi-utils vco-plugins wah-plugins fil-plugins
sudo apt-get install mda-lv2 libmp3lame-dev libspeex-dev libgsl0-dev
sudo apt-get install portaudio19-dev liblua5.3-dev python-dev libsmpeg0 libjpeg62-turbo
sudo apt-get install flite1-dev libgsm1-dev libgtk2.0-dev git libstk0-dev
sudo apt-get install libfluidsynth-dev fluid-soundfont-gm byacc

echo downloading package
pushd Downloads
git clone https://git.purrdata.net/jwilkes/purr-data.git
pushd purr-data

./configure --enable-jack
make all
sudo make install
