from NatNetClient import NatNetClient
import DataDescriptions
import MoCapData
import sys
import time
import json
import os
from websocket_server import WebsocketServer
import threading

file_name = ""
is_recording = False
start_time = 0
current_position = None
current_orientation = None
current_frame = None
is_running = False
streaming_client = None
ws_server = None
data = {}


# Setup a server to share rigid body data
def on_new_client(client, server):
    print("New client connected and was given id %d" % client['id'])

def start_new_server():
    global ws_server
    ws_server = WebsocketServer(port=8000, host='localhost')
    ws_server.set_fn_new_client(on_new_client)
    ws_server.serve_forever()


# This is a callback function that gets connected to the NatNet client
# and called once per mocap frame.
def receive_new_frame(data_dict):
    global current_frame, file_name 
    order_list=[ "frameNumber", "markerSetCount", "unlabeledMarkersCount", "rigidBodyCount", "skeletonCount",
                "labeledMarkerCount", "timecode", "timecodeSub", "timestamp", "isRecording", "trackedModelsChanged" ]
    current_frame = data_dict
           
# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receive_rigid_body_frame(new_id, position, rotation):
    global current_position, current_orientation, is_running, data
    current_position = position
    current_orientation = rotation

    # These IDs can be found in Motive
    if new_id == 2:
        body = 'Glove'
    elif new_id == 5:
        body = 'Pepper'
        print("Orientation Pepper: ", current_orientation)
        # print("data: ", data)
    elif new_id == 1:
        body = 'Target_1'
    else:
        body = f"Object_{new_id}"

    
    # Prepare data to be written to the file
    data.update({body: {
            "position": current_position,
            "orientation": current_orientation
    }})
    # time.sleep(0.1) ## It seems that the data is not being updated in real-time, but in chronological order

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

def init_tracker():
    global is_running, streaming_client
 #NatNetCliet shizzle

    optionsDict = {}
    optionsDict["clientAddress"] = "192.168.0.101"
    optionsDict["serverAddress"] = "192.168.0.100"
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

    
    time.sleep(1)
    if streaming_client.connected() is False:
        #print("ERROR: Could not connect properly.  Check that Motive streaming is on.")
        try:
            sys.exit(2)
        except SystemExit:
            print("...")
        finally:
            print("exiting")


    tmpCommands=["TimelinePlay",
                "TimelineStop",
                "SetPlaybackStartFrame,0",
                "SetPlaybackStopFrame,1000000",
                "SetPlaybackLooping,0",
                "SetPlaybackCurrentFrame,0",
                "TimelineStop"]
    for sz_command in tmpCommands:
        return_code = streaming_client.send_command(sz_command)
        print("Command: %s - return_code: %d"% (sz_command, return_code) )
    time.sleep(1)
    
    return streaming_client

def do_command(sz_command):
    global streaming_client

    return_code = streaming_client.send_command(sz_command)
    print("Command: %s - return_code: %d"% (sz_command, return_code) )
    return return_code



if __name__=="__main__":
    s_client = init_tracker()
    server_thread = threading.Thread(target=start_new_server)
    server_thread.start()

    time.sleep(5)
    do_command('LiveMode')
        
    try:
        # count=10000
        while True:
            ws_server.send_message_to_all(json.dumps(data))
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        is_looping = False
        is_running = False
        is_recording = False
        s_client.shutdown()
        ws_server.shutdown()