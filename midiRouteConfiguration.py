#! /usr/bin/env python3

################################################################################
##########                                                            ##########
###                          midiRoute.py                                    ###
#                             by DrewZeus                                      #
#                                                                              #
#                                                                              #
# This is designed as a basic framework around Python, Linux, JACK midi, and   #
# the Python-Jack module.  Its purpose is to create a way to transform, copy,  #
# filter, pass-through, etc. based on status byte, control/note byte, or value #
# byte.  Multiple input and output ports can be created and routes between the #
# two are created with dictionary entries of strings separated by periods.     #
# Multiple entries may be defined by defining them in a list.                  #
#                                                                              #
###                                                                          ###
#######                                                                  #######
#############                                                      #############
################################################################################
##########                                                            ##########
###                                                                          ###
#     -configuration file for midiRoute.py                                     #
#                                                                              #
###                                                                          ###
#                                                                              #
# configure input ports by creating classes with the following:                #
#                                                                              #
#     in "__init__" functions:                                                 #
#                                                                              #
#         define "self.name" as a string                                       #
#         define "self.routes" as a dictionary containing:                     #
#                                                                              #
#                  -input routes-                                              #
#            "diciontary":{dictionary_name:{status:{control:{value:"command"}}}#
#                                      or  {status:{control:"command"}}        #
#                                      or  {status:"command"}                  #
#                                  and use {"else":"command"} to catch         #
#                                  ..remaining events                          #
#            note: "default" must be a defined dictionary name                 #
#                                                                              #
###                                                                          ###
#                                                                              #
# configure output ports by creating classes with the following:               #
#                                                                              #
#     in "__init__" functions:                                                 #
#                                                                              #
#         define "self.name" as a string                                       #
#         define "self.routes" as a dictionary containing:                     #
#                                                                              #
#                  -output groups-                                             #
#            "matrix":{matrix_name:[midi_values]                               #
#                                                                              #
#            "sysex":{dictionary_name:{entry_name:[sysex_list]}}               #
#                                                                              #
###                                                                          ###
#                                                                              #
# Lastly,                                                                      #
#                                                                              #
# define all input ports by placing their classes in list "input_ports"        #
#                                                                              #
# define all output ports by placing their classes in list "output_ports"      #
#                                                                              #
# define all connections by placing a tuple of input and output strings..      #
#                                                  in list "connections"       #
#                                                                              #
# -note: both input and ouput ports can be set in these lists multiple times   #
#    example: ouput_ports = [outPort, outPort, outPort]                        #
#    this will cause the ports to appear as outPort, outPort2, and outPort3    #
#    all three of these ports will have the same "routes" defintions           #
#                                                                              #
###                                                                          ###
#######                                                                  #######
#############                                                      #############
################################################################################
##########                                                            ##########
###                                                                          ###
#                                                                              #
#                   --command definitions--                                    #
#                                                                              #
###                                                                          ###
#                                                                              #
#     variables                                                                #
#                                                                              #
#              -replaced at the start of processing                            #
#                                                                              #
#         #0 - all event bytes                                                 #
#         #1 - first event byte    status                                      #
#         #2 - second event byte   control/note                                #
#         #3 - third event byte    value                                       #
#                                                                              #
#              -replaced during processing of specific commands                #
#                                                                              #
# value-> $V - replaced by value in "get" command                              #
#       > $v - replaced by $V after first $V is replaced during first launch   #
# bind->  $B - replaced by new input during a triggered binded command         #
# math--> $M - replaced by value in "mathematics" command                      #
#     --> $m - replaced by $M after first $M is replaced during first launch   #
#     -->  _ - replaced by "." during "mathematics.multiply"                   #
#                                                                              #
######                                                                    ######
###########                                                          ###########
####                                                                        ####
#                                                                              #
#     arguments                                                                #
#                                                                              #
#              -must follow a command based on required arguments              #
#                                                                              #
######                                                                    ######
###########                                                          ###########
####                                                                        ####
#                                                                              #
#     commands                                                                 #
#                                                                              #
#              -can be used in conjuction with one another                     #
#              -must be at the beginning of an action                          #
#                                                                              #
###                                                                          ###
#                                                                              #
#   -send midi messages                                                        #
#         to.destinationPortName.midi.status.control/note.value                #
#     or  to.destinationPortName.midi.#0                                       #
#     or  to.destinationPortName.midi.#1.#2.#3                                 #
#                                                                              #
#   -send a group of midi messages                                             #
#         to.destinationPortName.chord.status.matrixEntry.value                #
#     or  to.destinationPortName.chord.matrixEntry.control/note.value          #
#     or  to.destinationPortName.chord.status.control/note.matrixEntry         #
#                                                                              #
#   -send a midi message from a matrix position                                #
#         to.destinationPortName.position.status.matrixEntry.value.index       #
#     or  to.destinationPortName.position.matrixEntry.control/note.value.index #
#     or  to.destinationPortName.position.status.control/note.matrixEntry.index#
#                                                                              #
#   send a sequence of midi messages                                           #
#         to.destinationPortName.sequence.status.matrixEntry.value             #
#     or  to.destinationPortName.sequence.matrixEntry.MatrixEntry.value        #
#     or  to.destinationPortName.sequence.status.matrixEntry.MatrixEntry       #
#     or  to.destinationPortName.sequence.matrixEntry.matrixEntry.MatrixEntry  #
#                                                                              #
#        -note: matrixEntries must have the same amount of entries..           #
#             ..to be used in the same command string                          #
#                                                                              #
#        -note: static values will not change throughout the sequence          #
#                                                                              #
#   -send sysex messages                                                       #
#         to.destinationPortName.sysex.sysexDeviceEntry.sysexCommandEntry      #
#                                                                              #
#                                                                              #
#   -set variable value                                                        #
#         set.variableInteger.value                                            #
#     or  set.variableInteger.#2                                               #
#                                                                              #
#        -note: this command works with the get command                        #
#                                                                              #
#                                                                              #
#   -get variable value                                                        #
#         get.variableInteger.$V                                               #
#                                                                              #
#        -note: $V can be anywhere in the command string                       #
#         get.variableInteger.to.outPort.midi.#1.#2.$V                         #
#                                                                              #
#        -note: $v can be used to get a second variable                        #
#         get.variableInteger.get.variableInteger.to.outPort.midi.$v.#2.$V     #
#                                                                              #
#                                                                              #
#   -set command string                                                        #
#         put.variableInteger.to.outPort.midi.144                              #
#     or  put.variableInteger.to.outPort.midi.176.0                            #
#                                                                              #
#        -note: this command works with the launch command                     #
#                                                                              #
#                                                                              #
#   -launch command string                                                     #
#         launch.variableInteger.#2.#3                                         #
#     or  launch.variableInteger.#3                                            #
#                                                                              #
#        -note: remaining arguments are added behind the recalled command      #
#                                                                              #
#        -note: variables from the set/get and put/launch command groups..     #
#             ..range between 0-1023 and the groups do not interact            #
#                                                                              #
#                                                                              #
#   -trigger actions on future variable change                                 #
#         bind.variableInteger.to.outPort.midi.144.$B.64                       #
#                                                                              #
#        -note: this only contains one entry and is overwritten upon a second  #
#                                                                              #
#                                                                              #
#   -one shot trigger                                                          #
#         bind.variableInteger.actions.action2.etc.bind.sameVariableInteger    #
#        -note: this sets the binded actions to be triggered next time to none #
#                                                                              #
#        -note: binded commands only trigger on "set" commands                 #
#                                                                              #
#        -note: all triggered commands launch before the remaining current..   #
#             ..commands continue to luanch and will effect remaining commands #
#                                                                              #
#                                                                              #
#   -compare two values                                                        #
#         comparison.value1.control.value2.next.command.and.args               #
#                                                                              #
#            controls include:                                                 #
#               greater                                                        #
#               lesser                                                         #
#               equal                                                          #
#               notEqual                                                       #
#               bitwise                                                        #
#               notBitwise                                                     #
#                                                                              #
#        -note: equal and notEqual are the only controls to compare values..   #
#             ..as strings and the remaining controls require integer values   #
#                                                                              #
#        -note: false means the next command will not launch                   #
#                                                                              #
#                                                                              #
#   -do nothing                                                                #
#         silence                                                              #
#                                                                              #
#                                                                              #
#   -echo all arguments                                                        #
#         print.remaining.arguments.and.commands                               #
#                                                                              #
#                                                                              #
#   -change dictionary volume                                                  #
#         load.inputPortName.volumeName                                        #
#                                                                              #
#                                                                              #
#   -perform mathmatical functions                                             #
#         mathematics.target.command.value.to.destinationPortName.#1.#2.$M     #
#                                                                              #
#        -note: $m can be used for a second mathematical equation              #
#                                                                              #
#            commands include:                                                 #
#               divide                                                         #
#               multiply                                                       #
#               add                                                            #
#               subtract                                                       #
#               modulus                                                        #
#               range                                                          #
#                                                                              #
###                                                                          ###
#######                                                                  #######
###                                                                          ###
#                                                                              #
#   -commandStrings can be linked together                                     #
#                                                                              #
#        -example:  "to.outPort1.midi.#0.to.outPort2.midi.#0"                  #
#                                                                              #
#   -commandStrings can be grouped together                                    #
#                                                                              #
#        -example:  ["to.outPort1.midi.#0", "to.outPort2.midi.#0"]             #
#                                                                              #
###                                                                          ###
#######                                                                  #######
#############                                                      #############
################################################################################

#set debug value here
#0 - only important prints
#1 - midi messages in and out
#2 - full verbose with fails
debug = 2

#main superclass
#-leave this alone-
class jackClient:
    def __init__(self):
        self.clientName = "client"
        self.debugLevel = 0
        self.active = False
        self.restart = False


#client classes inherit from main superclass


#copy classes from here-
#client
class defaultClient(jackClient):
    def __init__(self):
        self.clientName = "defaultClient"
        self.input_ports = [
                defaultInput
                ]
        self.output_ports = [
                defaultOutput
                ]
        self.debugLevel = 2
        self.startup_commands = [
                ]
        self.shutdown_commands = [
                ]

#input
class defaultInput:
    def __init__(self):
        self.name = 'defaultInput'
        self.routes = {
            "dictionary":
                {
                "default":
                    {
                    "else":"to.defaultOutput.midi.#0"
                    }
                }
            }

#output
class defaultOutput:
    def __init__(self):
        self.name = 'defaultOutput'
        self.routes = {
            "matrix":
                {
                "":[]
                },
            "sysex":
                {
                "":[]
                }
            }

#end of templates


#list clients here-








#keep this at the end and list available clients
clientList = [
            defaultClient
            ]

#for later use
connections = []

#to start midiRoute, call "./midiRoute.py defaultClient"
