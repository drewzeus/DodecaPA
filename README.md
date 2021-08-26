# DodecaPA
This project contains a set of tools for creating and playing 12-channel audio using Linux with BASH, JACK, Python and PureData.

The BASH scripts can help along the arduous installation.  These require root privilages to run.

midiRoute and it's accompanied configuration file allows the user to create JACK MIDI clients to manipulate the incomming messages to send any number of commands to any number of outputs.  If you happen to have a woefully esoteric SoundSculptue SwitchBlade 16GL, there is also an example configuration file to help demonstate rotating the entire room with the help of a Novation LaunchKey 25.  midiRoute only looks for a file in the same directory name "midiRouteConfiguration.py" so you will need to rename the example file before use.

volumeMatrix.pd is PureData patch that is designed to accept MIDI CC values (channel 1, CCs 0-9) that in turn selects the output position of the corrisponding input.  Currently, there is only 1 spread option (see Arrays).  Given this, a value of 127 results in a volume of 1 on chnanel 12, 4.5 on channels 11 & 1, and 0.8 on channels 10 and 2.  Note: Too distant of a motion, like going from 0 to 64 can currently result in unpleasent behavior.

Relevant Equipment in use for playing 12-channel music:
Logitech Z313   x6
Behringer U-phoria UMC1820
SoundSculpture SwitchBlade 16GL
Novation LaunchKey 25
Zaquencer (Behringer BCR2000)
System76 Serval

Equipment in use for 12-channel music creation:
a handful of synths
a few guitars
too many pedals
a couple of mics
Ardour
3000 lines of code in my configuartion page

please do attempt to contact me about this project if you have any interest.  I will continue to post updates about as I perfect each element.
drewzeus (AT) gmail
