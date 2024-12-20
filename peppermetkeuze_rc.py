﻿#Copyright © 2018 Naturalpoint
#
#Licensed under the Apache License, Version 2.0 (the "License")
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


# OptiTrack NatNet direct depacketization sample for Python 3.x
#
# Uses the Python NatNetClient.py library to establish a connection (by creating a NatNetClient),
# and receive data via a NatNet connection and decode it using the NatNetClient library.

import math     
import numpy as np
import matplotlib.pyplot as plt
from cosivina.nonumba import *
from cosivina import*
from cosivina import Simulator
from cosivina.GaussKernel1D import *
from cosivina.GaussStimulus1D import *
from cosivina.SumInputs import *
from cosivina.ScaleInput import *
from cosivina.NeuralField import *
from cosivina.SumDimension import *
from cosivina.NormalNoise import *
import sys
import time
from NatNetClient import NatNetClient
import DataDescriptions
import MoCapData
import struct
import keuze
# This is a callback function that gets connected to the NatNet client
# and called once per mocap frame.
def receive_new_frame(data_dict):
    order_list=[ "frameNumber", "markerSetCount", "unlabeledMarkersCount", "rigidBodyCount", "skeletonCount",
                "labeledMarkerCount", "timecode", "timecodeSub", "timestamp", "isRecording", "trackedModelsChanged" ]
    dump_args = False
    if dump_args == True:
        out_string = "    "
        for key in data_dict:
            out_string += key + "="
            if key in data_dict :
                out_string += data_dict[key] + " "
            out_string+="/"
        #print(out_string)

# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receive_rigid_body_frame( new_id, position, rotation ):
        
    position_x = position[0]
    position_x = 360*((position_x+0.0110)/(1.012+0.0110))#Deze werkt
    position_z = position[2]
    sim.setElementParameters('hand', 'amplitude', position_z*1.15)
    sim.setElementParameters('hand', 'position', position_x)

    
    pass
def add_lists(totals, totals_tmp):
    totals[0]+=totals_tmp[0]
    totals[1]+=totals_tmp[1]
    totals[2]+=totals_tmp[2]
    return totals

def print_configuration(natnet_client):
    #print("Connection Configuration:")
    #print("  Client:          %s"% natnet_client.local_ip_address)
    #print("  Server:          %s"% natnet_client.server_ip_address)
    #print("  Command Port:    %d"% natnet_client.command_port)
    #print("  Data Port:       %d"% natnet_client.data_port)

    if natnet_client.use_multicast:
        #print("  Using Multicast")
        #print("  Multicast Group: %s"% natnet_client.multicast_address)
        pass
    else:
        #print("  Using Unicast")
        pass

    #NatNet Server Info
    application_name = natnet_client.get_application_name()
    nat_net_requested_version = natnet_client.get_nat_net_requested_version()
    nat_net_version_server = natnet_client.get_nat_net_version_server()
    server_version = natnet_client.get_server_version()

##    print("  NatNet Server Info")
##    print("    Application Name %s" %(application_name))
##    print("    NatNetVersion  %d %d %d %d"% (nat_net_version_server[0], nat_net_version_server[1], nat_net_version_server[2], nat_net_version_server[3]))
##    print("    ServerVersion  %d %d %d %d"% (server_version[0], server_version[1], server_version[2], server_version[3]))
##    print("  NatNet Bitstream Requested")
##    print("    NatNetVersion  %d %d %d %d"% (nat_net_requested_version[0], nat_net_requested_version[1],\
##       nat_net_requested_version[2], nat_net_requested_version[3]))
    #print("command_socket = %s"%(str(natnet_client.command_socket)))
    #print("data_socket    = %s"%(str(natnet_client.data_socket)))


def print_commands(can_change_bitstream):
    outstring = "Commands:\n"
    outstring += "Return Data from Motive\n"
    outstring += "  s  send data descriptions\n"
    outstring += "  r  resume/start frame playback\n"
    outstring += "  p  pause frame playback\n"
    outstring += "     pause may require several seconds\n"
    outstring += "     depending on the frame data size\n"
    outstring += "Change Working Range\n"
    outstring += "  o  reset Working Range to: start/current/end frame = 0/0/end of take\n"
    outstring += "  w  set Working Range to: start/current/end frame = 1/100/1500\n"
    outstring += "Return Data Display Modes\n"
    outstring += "  j  print_level = 0 supress data description and mocap frame data\n"
    outstring += "  k  print_level = 1 show data description and mocap frame data\n"
    outstring += "  l  print_level = 20 show data description and every 20th mocap frame data\n"
    outstring += "Change NatNet data stream version (Unicast only)\n"
    outstring += "  3  Request 3.1 data stream (Unicast only)\n"
    outstring += "  4  Request 4.0 data stream (Unicast only)\n"
    outstring += "t  data structures self test (no motive/server interaction)\n"
    outstring += "c  show configuration\n"
    outstring += "h  print commands\n"
    outstring += "q  quit\n"
    outstring += "\n"
    outstring += "NOTE: Motive frame playback will respond differently in\n"
    outstring += "       Endpoint, Loop, and Bounce playback modes.\n"
    outstring += "\n"
    outstring += "EXAMPLE: PacketClient [serverIP [ clientIP [ Multicast/Unicast]]]\n"
    outstring += "         PacketClient \"192.168.10.14\" \"192.168.10.14\" Multicast\n"
    outstring += "         PacketClient \"127.0.0.1\" \"127.0.0.1\" u\n"
    outstring += "\n"
    #print(outstring)

def variables(voorwerp):

    voorwerp = voorwerp
    return voorwerp

def request_data_descriptions(s_client):
    # Request the model definitions
    s_client.send_request(s_client.command_socket, s_client.NAT_REQUEST_MODELDEF,    "",  (s_client.server_ip_address, s_client.command_port) )

def test_classes():
    totals = [0,0,0]
    print("Test Data Description Classes")
    totals_tmp = DataDescriptions.test_all()
    totals=add_lists(totals, totals_tmp)
    print("")
    print("Test MoCap Frame Classes")
    totals_tmp = MoCapData.test_all()
    totals=add_lists(totals, totals_tmp)
    print("")
    print("All Tests totals")
    print("--------------------")
    print("[PASS] Count = %3.1d"%totals[0])
    print("[FAIL] Count = %3.1d"%totals[1])
    print("[SKIP] Count = %3.1d"%totals[2])

def my_parse_args(arg_list, args_dict):
    # set up base values
    arg_list_len=len(arg_list)
    if arg_list_len>1:
        args_dict["serverAddress"] = arg_list[1]
        if arg_list_len>2:
            args_dict["clientAddress"] = arg_list[2]
        if arg_list_len>3:
            if len(arg_list[3]):
                args_dict["use_multicast"] = True
                if arg_list[3][0].upper() == "U":
                    args_dict["use_multicast"] = False

    return args_dict

def create_simulator():
 #neural field simulator############
    sim = Simulator.Simulator()
    fieldSize = (1, 360)
    sigma_exc = 6
    sigma_inh = 10
    #########Neural field parameters


    # create inputs (and sum for visualization)
    sim.addElement(GaussStimulus1D('stimulus 1', fieldSize, sigma_exc, 0, round(1/4*fieldSize[1]), True, False))
    sim.addElement(GaussStimulus1D('stimulus 2', fieldSize, sigma_exc, 0, round(1/2*fieldSize[1]), True, False))
    sim.addElement(GaussStimulus1D('stimulus 3', fieldSize, sigma_exc, 0, round(3/4*fieldSize[1]), True, False))
    sim.addElement(GaussStimulus1D('stimulus 4', fieldSize, sigma_exc, 0, round(fieldSize[1]), True, False))
    sim.addElement(SumInputs('stimulus sum', fieldSize), ['stimulus 1', 'stimulus 2', 'stimulus 3', 'stimulus 4'])
    sim.addElement(ScaleInput('stimulus scale w', fieldSize, 0.25), 'stimulus sum')

    # create neural field
    sim.addElement(NeuralField('field u', fieldSize, 20, -5, 4), 'stimulus sum')
    #sim.addElement(NeuralField('field v', fieldSize, 5, -5, 4))
    #sim.addElement(NeuralField('field w', fieldSize, 20, -5, 4), 'stimulus scale w')
    
    # create interactions
    #interactions from field u
    sim.addElement(GaussKernel1D('u -> u', fieldSize, sigma_exc, 5, True, True), 'field u', 'output', 'field u')
    

    # create noise stimulus and noise kernel
    sim.addElement(NormalNoise('noise u', fieldSize, 1));
    sim.addElement(GaussKernel1D('noise kernel u', fieldSize, 0, 0.5, True, True), 'noise u', 'output', 'field u')
    
        #actief = NeuralField()
    #################### beweging hand
    sim.addElement(GaussStimulus1D('hand', fieldSize, sigma_exc, 1.5, round(0*fieldSize[1]), True, False))
    sim.addElement(NeuralField('reaching behavior', fieldSize, 20, -2, 4), 'hand')
    sim.addElement(GaussKernel1D('hand position', fieldSize, 5, 1, True, True),'hand', 'output', 'reaching behavior')
    sim.addElement(GaussKernel1D('h -> u', fieldSize, sigma_exc, 4.1, True, True), 'hand', 'output', 'field u')
    #sim.addElement(GaussKernel1D('t -> u', fieldSize, sigma_exc, 5, True, True), 'summed obj driehoek', 'output', 'field u')
    #######adding noise
    sim.addElement(NormalNoise('noise reaching', fieldSize, 1))
    sim.addElement(GaussKernel1D('noise kernel reaching', fieldSize, 0, 1, True, True), 'noise reaching', 'output', 'reaching behavior')

    
    ####################################################
    ################## Object Layer#####################

    keuze = input("please make a choice between shape: triangles (t), squares (s) and circles (c).\n and colors: Pink (p), Orange (o), Green (g)")
    print(keuze)
    if keuze == 't':
        create_field_inputs(sim, 'driehoek', [2,5,8], 't') #create input driehoek

    if keuze == 's':
        create_field_inputs(sim, 'vierkant', [1,4,7], 'v') #create input driehoek
        
    if keuze == 'c':
        create_field_inputs(sim, 'cirkel', [3,6,9], 'c') #create input cirkel

    if keuze == 'p':
        create_field_inputs(sim, 'pink', [5,7,9], 'p') #create input pink

    if keuze == 'o':
        create_field_inputs(sim, 'orange', [2,4,6], 'o') #create input oranje
        
    if keuze == 'g':
        create_field_inputs(sim, 'green', [1,3,8], 'g') #create input green

    sim.addElement(NormalNoise('noise objects', fieldSize, 1))

    sim.addElement(GaussKernel1D('noise kernel objects', fieldSize, 0, 1, True, True), 'noise objects', 'output', 'object layer')



    
    ####################################################
    ################## action Layer#####################
    
    ################Summing objects
    sim.addElement(NeuralField('action layer', fieldSize, 20, -5, 4))
    sim.addElement(GaussKernel1D('u -> action', fieldSize, sigma_exc, 5, True, True), 'field u', 'activation', 'action layer')
    sim.addElement(NormalNoise('noise objects2', fieldSize, 1))
    sim.addElement(GaussKernel1D('noise kernel action', fieldSize, 0, 1, True, True), 'noise objects2', 'output', 'action layer')

    return sim

def create_field_inputs(sim, label, objects, target_field):
    #create input driehoek
    sim.addElement(GaussStimulus1D(label, fieldSize, sigma_exc, 5.5, round(1/7*fieldSize[1]), True, False))
    
    obj_list=[]
    for obj in objects:
        lbl = 'obj ' + str(obj)
        sim.addElement(GaussStimulus1D( lbl, fieldSize, sigma_exc, 2, round((obj/10)*fieldSize[1]), True, False))
        ojb_list.append(lbl)
    
#create neural field driehoek (t)
    sim.addElement(SumInputs('summed obj ' + label, fieldSize), obj_list)
    sim.addElement(NeuralField('object layer', fieldSize, 20, -5, 4), 'summed obj ' + label)
    sim.addElement(NeuralField('field ' + target_field, fieldSize, 20, -5, 4), 'summed obj ' + label)
    sim.addElement(GaussKernel1D(target_field + ' -> u', fieldSize, sigma_exc, 5, True, True), 'summed obj ' + label, 'output', 'field u')

def check_and_do_action(sim, i, hand_range, message):
    for i in hand_range:
        if sim.getComponent('action layer', 'activation')[0,i] > 1 and sim.getElementParameter('hand', 'position') >hand_range[0] and sim.getElementParameter('hand', 'position')< hand_range[1]:

            pepper =  open("pepperzegt.txt", "w")
            pepper.write(message)
            pepper.close()
            break

def init_natnet_client():
        #NatNetCliet shizzle

    optionsDict = {}
    optionsDict["clientAddress"] = "127.0.0.1"
    optionsDict["serverAddress"] = "127.0.0.1"
    optionsDict["use_multicast"] = True

    # This will create a new NatNet client
    optionsDict = my_parse_args(sys.argv, optionsDict)

    streaming_client = NatNetClient()
    streaming_client.set_client_address(optionsDict["clientAddress"])
    streaming_client.set_server_address(optionsDict["serverAddress"])
    streaming_client.set_use_multicast(optionsDict["use_multicast"])

    # Configure the streaming client to call our rigid body handler on the emulator to send data out.
    streaming_client.new_frame_listener = receive_new_frame
    streaming_client.rigid_body_listener = receive_rigid_body_frame
    
    # Start up the streaming client now that the callbacks are set up.
    # This will run perpetually, and operate on a separate thread.
    streaming_client.set_print_level(0)
    is_running = streaming_client.run()
    if not is_running:
        print("ERROR: Could not start streaming client.")
        try:
            sys.exit(1)
        except SystemExit:
            print("...")
        finally:
            print("exiting")
    
    #time.sleep(1)
    if streaming_client.connected() is False:
        #print("ERROR: Could not connect properly.  Check that Motive streaming is on.")
        try:
            sys.exit(2)
        except SystemExit:
            print("...")
        finally:
            pass
            #print("exiting")

    print_configuration(streaming_client)
    print("\n")
    print_commands(streaming_client.can_change_bitstream_version())
      
    return streaming_client

if __name__ == "__main__":

    t=0
    sim = create_simulator()

    plt.ion()

        # re-initialize
    sim.init()
    streaming_client = init_natnet_client()



    # prepare axes
    fig, axes = plt.subplots(2, 1)
    for i in range(1):
        axes[i].set_xlim(0, fieldSize[1])
        axes[i].set_ylim(-5, 5)
        axes[i].set_ylabel('activation')
    #axes[3].set_xlabel('feature space')
    #axes[3].set_ylabel('hand movement')
    
    #axes[2].set_ylim(-7,5)
    # plot initial state
    x = np.arange(fieldSize[1])
    plot_stim, plot_u = axes[0].plot(x, sim.getComponent('stimulus sum', 'output')[0],
            x, sim.getComponent('field u', 'activation')[0], color='r')
    plot_stim.set_color('g')
    #plot_objects, = axes[2].plot(x, sim.getComponent('object layer', 'activation')[0], color='b')
    #plot_action, = axes[3].plot(x, sim.getComponent('action layer', 'activation')[0], color='r')
    
    #plot_c, = axes[3].plot(x, sim.getComponent('field c', 'activation')[0], color='r')
    #plot_n, = axes[3].plot(x, sim.getComponent('field n', 'activation')[0], color='r')
    # run simulation
    #plot_reach, = axes[1].plot(x, sim.getComponent('reaching behavior', 'activation')[0], color='r')
    #plot_hand, = axes[1].plot(x, sim.getComponent('hand', 'output')[0])

    ######opening write file
    ######
    pepper =  open("pepperzegt.txt", "w")
    pepper.write("0")
    pepper.close()

    ######



    is_looping = True
    while is_looping:
            
        sim.saveSettings('test2.JSON')
    # load parameter settings
        sim.loadSettings('test2.JSON')
        sim.run(12,True,False)
    #sim.run(tMax, True, False)
    
    
        for i in range(360):
            ####################### check for activation above 1 if above 1 then its the object number in the pepper file.
            ####################### Naoqi file reads this and tells participant where it should go
            if keuze == 't':
                check_and_do_action(sim, i, [60,80],"2")
                check_and_do_action(sim, i, [170,190],"5")
                check_and_do_action(sim, i, [275,295],"8")
                break

            if keuze == 's':
                check_and_do_action(sim, i, [25,45],"1")
                check_and_do_action(sim, i, [130,150],"4")
                check_and_do_action(sim, i, [245,260],"7")
                break

            if keuze == 'c':
                check_and_do_action(sim, i, [100,120],"3")
                check_and_do_action(sim, i, [210,230],"6")
                check_and_do_action(sim, i, [315,335],"9")
                break


            if keuze == 'g':
                check_and_do_action(sim, i, [25,45],"1")
                check_and_do_action(sim, i, [100,120],"3")
                check_and_do_action(sim, i, [275,295],"8")
                break

            if keuze == 'o':
                check_and_do_action(sim, i, [60,80],"2")
                check_and_do_action(sim, i, [130,150],"4")
                check_and_do_action(sim, i, [205,225],"6")
                break

            if keuze == 'p':
                check_and_do_action(sim, i, [170,190],"5")
                check_and_do_action(sim, i, [240,260],"7")
                check_and_do_action(sim, i, [315,335],"9")
                break
   
        #t += 0.085
        plot_u.set_ydata(sim.getComponent('field u', 'activation')[0])
        #plot_objects.set_ydata(sim.getComponent('object layer', 'activation')[0])
        #plot_action.set_ydata(sim.getComponent('action layer', 'activation')[0])
        #plot_c.set_ydata(sim.getComponent('field c', 'activation')[0])
        #plot_n.set_ydata(sim.getComponent('field n', 'activation')[0])
        plot_stim.set_ydata(sim.getComponent('stimulus sum', 'output')[0])
        
        #plot_reach.set_ydata(sim.getComponent('reaching behavior', 'activation')[0])
        
        
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        

        
