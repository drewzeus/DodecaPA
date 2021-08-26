#! /usr/bin/env python3

#includes
import jack
import queue
import struct
from sys import argv
from time import sleep
from inspect import getframeinfo, stack

try:
    print("<----%s---->" % argv[1])
except IndexError:
    print("client name missing")
    exit()

debug = 0
#redefined print function for debugging
#importance value of 0 = always print
#importance value of 1 = print when debug is 0 or 1
#importance value of 2 = print when debug is 0, 1 or 2
_print = print
def print(msg, importance=-1):
    global debug
    if importance == -1:
        caller = getframeinfo(stack()[1][0])
        _print("%d - %s" % (caller.lineno, msg))
    if importance == 0:
        _print(msg)
    elif importance == 1:
        if debug >= 1:
            _print(msg)
    elif importance == 2:
        if debug == 2:
            _print(msg)


#set configuration variables
inPorts = {}
outPorts = {}
variables = {}
argsList = {}
cntrList = {}
latches = {}
for x in range(1024): variables.update({x:[0,None]})#value,bindedCommands
for x in range(1024): argsList.update({x:[]})#launchable commands
for x in range(1024): cntrList.update({x:[0,0,1,0,[]]})#value,bottom,top,exec,bindedCommands
for x in range(1024): latches.update({x:False})#latches
startup_commands = []
shutdown_commands = []

#gather user configuration
from midiRouteConfiguration import *

clientFound = False
for package in dir():
    if str(package) == argv[1]:
        clientFound = True

if clientFound == False:
    print("client: '%s' not found in configuration" % argv[1], 0)
    exit()


#start client
for clientObject in clientList:
    #instantiate
    co = clientObject()
    if co.clientName != argv[1]:
        del co
        continue
    #prep work
    client = jack.Client(co.clientName)
    print("/----client created : %s" % co.clientName, 0)
    print("|                   :", 0)

    #create input ports
    for inputPortObject in co.input_ports:
        inputObject = inputPortObject()
        setattr(inputObject, "dictionary", "default")
        
        addative, x = "", 1
        while True:
            if inputObject.name + addative in inPorts.keys():
                x += 1
                addative = str(x)
            else:
                inputObject.name += addative
                break
        
        inPorts.update({inputObject.name:[client.midi_inports.register(inputObject.name), inputObject]})
        print("|---input connected : %s" % inputObject.name, 0)
    print("|=-                 :", 0)

    #create output ports
    for outputPortObject in co.output_ports:
        outputObject = outputPortObject()
        outPorts.update({outputObject.name:[client.midi_outports.register(outputObject.name), outputObject, queue.Queue()]})
        print("|--output connected : %s" % outputObject.name, 0)

    print("\___________________:", 0)
    print("", 0)
    for command in co.startup_commands:
        if command != "":
            args = command.split(".")
            startup_commands.append([args])
    for command in co.shutdown_commands:
        if command != "":
            args = command.split(".")
            shutdown_commands.append([args])
    debug = co.debugLevel
    print("", 0)


#define callbacks
@client.set_process_callback
def process(frames):
    global inPorts
    global outPorts
    global debug
    
    #catch incoming events
    
    for name, portData in inPorts.items():
        
        inPort = portData[0]
        routes = portData[1].routes
        dictionary = portData[1].dictionary
        incoming = []
        commands = []
        
        for offset, data in inPort.incoming_midi_events():
            
            msg = struct.unpack('%iB' % len(data), data)
            incoming.append(msg)
            
            print("message in: %s - %s" % (name, str(msg)), 1)
        
        commands = processIncoming(incoming.copy(), routes["dictionary"][dictionary].copy())
        if commands: processCommands(commands.copy())
    
    #send outgoing messages
    
    for name, portData in outPorts.items():
        
        outPort = portData[0]
        outgoing = portData[2]
        outPort.clear_buffer()
        
        while not outgoing.empty():
            msg = outgoing.get(block=False)
            outPort.write_midi_event(0, msg)
            print("message out: %s - %s" % (name, str(msg)), 1)


#define helper functions

def processIncoming(incomingEvents, routes):
    returnable = []
    
    for eventTuple in incomingEvents:
        
        try:
            entry = routes[eventTuple[0]]
            if entry.__class__ == dict:
                
                try:
                    entry = entry[eventTuple[1]]
                    if entry.__class__ == dict:
                        
                        try: entry = entry[eventTuple[2]]
                        
                        except KeyError:
                            try: entry = entry["else"]
                            except KeyError:
                                print("FAIL: %i is not a defined value" % eventTuple[2], 2)
                                continue
                    
                except KeyError:
                    try: entry = entry["else"]
                    except KeyError:
                        print("FAIL: %i is not a defined value" % eventTuple[1], 2)
                        continue
        
        except KeyError:
            try: entry = routes["else"]
            except KeyError:
                print("FAIL: %i is not a defined value" % eventTuple[0], 2)
                continue
        
        if entry.__class__ == list:
            for entr in entry:
                ent = replaceVariables(entr, eventTuple)
                if ent: returnable.append(ent.split('.'))
        
        if entry.__class__ == str:
            ent = replaceVariables(entry, eventTuple)
            if ent: returnable.append(ent.split('.'))
        
    return returnable


def replaceVariables(entry, incomingEvents):
    while "#" in entry:
        x = 2
        
        try:
            if "#0" in entry: entry = entry.replace("#0", "%i.%i.%i" % (incomingEvents[0], incomingEvents[1], incomingEvents[2]))
        
        except IndexError:
            l = len(incomingEvents)
            if l == 0: return
            elif l == 1: replacement = "%i.%i.%i" % (incomingEvents[0], 0, 0)
            elif l == 2: replacement = "%i.%i.%i" % (incomingEvents[0], incomingEvents[1], 0)
            entry = entry.replace("#0", replacement)
        
        if "#1" in entry: entry = entry.replace("#1", "%i" % (incomingEvents[0]))
        if "#2" in entry: entry = entry.replace("#2", "%i" % (incomingEvents[1]))
        if "#3" in entry: entry = entry.replace("#3", "%i" % (incomingEvents[2]))
        x -= 1
        if x == 0:
            print("FAIL: '#' in dictionary entry contains no variable", 2)
            return
    
    return entry


def processCommands(commandsList):
    for commands in commandsList:
        print("commands: %s" % str(commands), 1)
        command = commands.pop(0)
        
        #try:
        ret = eval("_cmd_%s" % command)(commands)
        #except NameError:
        #    print("FAIL: %s is not a defined function" % command)
        #    return


#define command functions

def _cmd_to(args):
    global outPorts
    destination = args.pop(0)
    messageType = args.pop(0)
    
    try:
        outputObject = outPorts[destination]
    except KeyError:
        print("FAIL: %s is not a defined destination" % destination, 2)
        return
    
    if messageType == "midi":
        outputObject[2].put((int(args[0]), int(args[1]), int(args[2])))
        for x in range(3): args.pop(0)
    
    elif messageType == "chord":
        status = args.pop(0)
        control = args.pop(0)
        value = args.pop(0)
        
        try:
            if not status.isdigit(): status = outputObject[1].routes["matrix"][status]
        except KeyError:
            print("FAIL: %s is not a defined matrix entry" % status, 2)
            return
        
        try:
            if not control.isdigit(): control = outputObject[1].routes["matrix"][control]
        except KeyError:
            print("FAIL: %s is not a defined matrix entry" % control, 2)
            return
        
        try:
            if not value.isdigit(): value = outputObject[1].routes["matrix"][value]
        except KeyError:
            print("FAIL: %s is not a defined matrix entry" % value, 2)
            return
        
        if status.__class__ != list: status = [status]
        if control.__class__ != list: control = [control]
        if value.__class__ != list: value = [value]
        
        for statusByte in status:
            for controlByte in control:
                for valueByte in value:
                    outputObject[2].put((int(statusByte), int(controlByte), int(valueByte)))
    
    elif messageType == "sequence":
        status = args.pop(0)
        control = args.pop(0)
        value = args.pop(0)
        statusLength = 1
        controlLength = 1
        valueLength = 1
        fullLength = -1
        
        try:
            if not status.isdigit():
                status = outputObject[1].routes["matrix"][status]
                statusLength = len(status)
                fullLength = statusLength
        except KeyError:
            print("FAIL: %s is not a defined matrix entry" % status, 2)
            return
        
        try:
            if not control.isdigit():
                control = outputObject[1].routes["matrix"][control]
                controlLength = len(control)
                if fullLength == -1:
                    fullLength = controlLength
                else:
                    if fullLength != controlLength:
                        print("FAIL: sequence lengths vary")
                        return
        except KeyError:
            print("FAIL: %s is not a defined matrix entry" % control, 2)
            return
        
        try:
            if not value.isdigit():
                value = outputObject[1].routes["matrix"][value]
                valueLength = len(value)
                if fullLength == -1:
                    fullLength = valueLength
                else:
                    if fullLength != valueLength:
                        print("FAIL: sequence lengths vary")
                        return
        except KeyError:
            print("FAIL: %s is not a defined matrix entry" % value, 2)
            return
        
        if status.__class__ != list:
            digit = status
            status = []
            for x in range(fullLength):
                status.append(digit)
        
        if control.__class__ != list:
            digit = control
            control = []
            for x in range(fullLength):
                control.append(digit)
        
        if value.__class__ != list:
            digit = value
            control = []
            for x in range(fullLength):
                value.append(digit)
        
        for x in range(fullLength):
            outputObject[2].put((int(status[x]), int(control[x]), int(value[x])))
    
    elif messageType == "position":
        status = args.pop(0)
        control = args.pop(0)
        value = args.pop(0)
        index = int(args.pop(0))
        
        try:
            if not status.isdigit(): status = outputObject[1].routes["matrix"][status]
        except KeyError:
            print("FAIL: %s is not a defined matrix entry" % status, 2)
            return
        
        try:
            if not control.isdigit(): control = outputObject[1].routes["matrix"][control]
        except KeyError:
            print("FAIL: %s is not a defined matrix entry" % control, 2)
            return
        
        try:
            if not value.isdigit(): value = outputObject[1].routes["matrix"][value]
        except KeyError:
            print("FAIL: %s is not a defined matrix entry" % value, 2)
            return
        
        if status.__class__ == list: status = status[index]
        if control.__class__ == list: control = control[index]
        if value.__class__ == list: value = value[index]
        
        outputObject[2].put((int(status), int(control), int(value)))
    
    elif messageType == "sysex":
        deviceEntry = args.pop(0)
        commandEntry = args.pop(0)
        
        try:
            sysexValueList = outputObject[1].routes["sysex"][deviceEntry][commandEntry]
        except KeyError:
            print("FAIL: %s.%s is not a defined sysex entry" % (deviceEntry, commandEntry), 2)
            return
        
        outputObject[2].put((sysexValueList))
    
    else:
        print("FAIL: no message type: %s" % str(args), 2)
        return
    
    if args:
        processCommands([args])


def _cmd_put(args):
    global argsList
    argsInt = int(args.pop(0))
    
    try: argsList[argsInt]
    except KeyError:
        print("FAIL: %s is not a defined variable" % argsInt, 2)
        return
    
    argsList[argsInt] = args
    return


def _cmd_launch(args):
    global argsList
    argsInt = int(args.pop(0))
    
    try: newArgs = argsList[argsInt].copy()
    except KeyError:
        print("FAIL: %s is not a defined variable" % argsInt, 2)
        return
    
    if newArgs:
        processCommands([newArgs+args])


def _cmd_set(args):
    global variables
    argsInt = args.pop(0)
    
    try: variableList = variables[int(argsInt)]
    except KeyError:
        print("FAIL: %s is not a defined variable" % argsInt, 2)
        return
    
    value = args.pop(0)
    variableList[0] = int(value)
    
    if variableList[1] != None:
        if variableList[1] == []:
            variableList[1] = None
        else:
            newArgs = variableList[1].copy()
            for x in range(len(newArgs)):
                if newArgs[x] == "$B":
                    newArgs[x] = value
            processCommands([newArgs])
    
    if args:
        processCommands([args])


def _cmd_get(args):
    global variables
    variable = args.pop(0)
    
    try: variableList = variables[int(variable)]
    except KeyError:
        print("FAIL: %s is not a defined variable" % variable, 2)
        return
    
    if "$V" in args:
        for x in range(len(args)):
            if args[x] == "$V":
                args[x] = str(variableList[0])
        
        if "$v" in args:
            for x in range(len(args)):
                if args[x] == "$v":
                    args[x] = "$V"
    
    if args:
        processCommands([args])


def _cmd_bind(args):
    global variables
    variable = args.pop(0)
    
    try: variableList = variables[int(variable)]
    except KeyError:
        print("FAIL: %s is not a defined variable" % variable, 2)
        return
    
    variableList[1] = args
    return


#count.240.create.0.0.1.0
#count.240.incriment
#count.240.decriment
#count.240.bind.to.midiClockOut.midi.224.0.0
#count.240.get.print.$C


def _cmd_count(args):
    global cntrList
    counterInt = int(args.pop(0))
    command = args.pop(0)

    newArgs = []

    if command == "create":
        value = int(args.pop(0))
        bottomValue = int(args.pop(0))
        topValue = int(args.pop(0))
        execValue = int(args.pop(0))

        cntrList[counterInt][0] = value
        cntrList[counterInt][1] = bottomValue
        cntrList[counterInt][2] = topValue
        cntrList[counterInt][3] = execValue
    
    elif command == "bind":
        cntrList[counterInt][4] = args.copy()
    
    elif command == "incriment":
        cntrList[counterInt][0] += 1
        if cntrList[counterInt][0] > cntrList[counterInt][2]:
            cntrList[counterInt][0] = cntrList[counterInt][1]
        if cntrList[counterInt][0] == cntrList[counterInt][3]:
            newArgs = cntrList[counterInt][4].copy()
    
    elif command == "decriment":
        cntrList[counterInt][0] -= 1
        if cntrList[counterInt][0] < cntrList[counterInt][1]:
            cntrList[counterInt][0] = cntrList[counterInt][2]
        if cntrList[counterInt][0] == cntrList[counterInt][3]:
            newArgs = cntrList[counterInt][4].copy()
    
    elif command == "get":
        for arg in args:
            if "$C" in arg:
                arg.replace("$C",cntrList[counterInt[0]])
        for arg in args:
            if "$c" in arg:
                arg.replace("$c, $C")
    
    else:
        print("FAIL: %s is not a command" % command, 2)
        return
    
    if newArgs:
        processCommands([newArgs])



def _cmd_require(args):
    global latches
    testValue = args.pop(0)
    if testValue == "true":
        testValue = True
    elif testValue == "false":
        testValue = False
    else:
        print("FAIL: %s is incorrect: value must be true or false" % str(testValue), 2)
        return
    latchInt = int(args.pop(0))
    
    try: storedValue = latches[latchInt]
    except KeyError:
        print("FAIL: %i is not a defined latch number" % latchInt, 2)
        return
    
    if storedValue == testValue:
        processCommands([args])
    else: return


def _cmd_latch(args):
    global latches
    command = args.pop(0)
    latchInt = int(args.pop(0))
    value = None
    
    try: value = latches[latchInt]
    except KeyError:
        print("FAIL: %i is not a defined latch" % latchInt, 2)
        return
    
    if command == "flip":
        if value == True: value = False
        else: value = True
    elif command == "set":
        value = True
    elif command == "unset":
        value = False
    else:
        print("FAIL: %s is not a command" % command, 2)
        return
    
    latches[latchInt] = value
    
    if args:
        processCommands([args])


def _cmd_within(args):
    distance = int(args.pop(0))
    value1 = int(args.pop(0))
    value2 = int(args.pop(0))
    doCommand = False

    if value1 == value2:
        doCommand = True
    
    elif value1 > value2:
        if (value2 + distance) >= value1:
            doCommand = True
    
    elif value2 > value1:
        if (value1 + distance) >= value2:
            doCommand = True
    
    if doCommand:
        if args:
            processCommands([args])


def _cmd_comparison(args):
    value1 = args.pop(0)
    control = args.pop(0)
    value2 = args.pop(0)
    doCommand = False
    
    if control == "greater":
        if int(value1) > int(value2):
            doCommand = True
    
    elif control == "lesser":
        if int(value1) < int(value2):
            doCommand = True
        
    elif control == "equal":
        if value1 == value2:
            doCommand = True
        
    elif control == "notEqual":
        if value1 != value2:
            doCommand = True
    
    elif control == "bitwise":
        if int(value1) & int(value2) != 0:
            doCommand = True
    
    elif control == "notBitwise":
        if int(value1) & int(value2) == 0:
            doCommand = True
    
    if doCommand:
        if args:
            processCommands([args])


def _cmd_silence(args):
    pass


def _cmd_print(args):
    print(args, 0)


def _cmd_load(args):
    global inPorts
    name = args.pop(0)
    volume = args.pop(0)
    
    try:
        portData = inPorts[name][1]
    except KeyError:
        print("FAIL: %s is not a defined input port" % name, 2)
        return
    
    try:
        portData.routes["dictionary"][volume]
        portData.dictionary = volume
        print("Dictionary volume loaded: %s - %s" % (name, volume), 2)
    except KeyError:
        print("FAIL: %s is not a defined dictionary volume" % volume, 2)
    
    if args:
        processCommands([args])


def _cmd_mathematics(args):
    target = args.pop(0)
    command = args.pop(0)
    value = args.pop(0)
    
    if "$M" in args:
        if command == "divide":
            answer = int(target) / int(value)
        
        elif command == "multiply":
            if "_" in value:
                answer = int(target * value.replace("_","."))
            
            else:
                answer = int(target) * int(value)
        
        elif command == "add":
            answer = int(target) + int(value)
        
        elif command == "subtract":
            answer = int(target) - int(value)
        
        elif command == "modulus":
            answer = int(target) % int(value)
        
        elif command == "range":
            ratio = 127 / int(value)
            answer = int(target) * ratio
        
        else:
            print("FAIL: %s is not a defined command" % command, 2)
            return
        
        for x in range(len(args)):
            if args[x] == "$M":
                args[x] = int(answer)
        
        if "$m" in args:
            for x in range(len(args)):
                if args[x] == "$m":
                    args[x] = "$M"
    
    if args:
        processCommands([args])


#accept input forever

def main():
    active = True
    with client:
        ans = ""
        
        #connect defined connections
        for connection in connections:
            try:
                print(connection, 0)
                client.connect(connection[0],connection[1])
            except: print("FAIL: error connecting %s and %s" % (connection[0], connection[1]), 2)
        
        print('\ntype "q" to quit\n', 0)
        while active:
            ans = input()
            if ans == 'q':
                for args in shutdown_commands.copy():
                    if args:
                        processCommands(args)
                    sleep(0.05)
                break
            elif ans == "startup":
                for args in startup_commands.copy():
                    if args:
                        processCommands(args)
                    sleep(0.05)
            else:
                commandsList = ans.split('.')
                processCommands([commandsList])
        
        client.deactivate()
    client.close()


if __name__ == '__main__':
    main()

