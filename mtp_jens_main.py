#python 2.7
import time
from definitions import *
import sys
import numpy as np

# SIMULATED = True
# if not SIMULATED:
import naoqi
from naoqi import ALProxy
import nao_nocv_2_1 as Nao
import json
import math
import websocket
import threading

# overrided definitions
IP='192.168.0.116'      # Eve
PORT=9559
robot = ALProxy("ALTextToSpeech", IP, PORT)
Nao.InitProxy(IP)
# else:
    # import pyttsx3
    # tts = pyttsx3.init()

live_data = {}
ws = None

def on_message(ws, message):
    global live_data
    # Parse the incoming JSON message and update live_data dictionary
    try:
        data = json.loads(message)
        live_data.update(data)
##        print("Updated data:", live_data)
    except json.JSONDecodeError as e:
        print("Failed to decode JSON message:", e)

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws):
    print("WebSocket connection closed")

def on_open(ws):
    print("WebSocket connection opened")
    
def start_websocket_client():
    global ws
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8000",on_message=on_message,on_error=on_error,on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

def read_rigid_body_data(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except (IOError, ValueError) as e:
        print("Error reading file:", e)
        return None

    # Convert the data into a dictionary of dictionaries format
    # Displaying the content
##    for object_id, attributes in data.items():
##        print("Object ID:", object_id)
##        print("Position (x,y,z):", attributes.get("position")[0])
##        print("Orientation (x,y,z):", attributes.get("orientation")[1])
##        print()
    return data

def normalise(vector):
    mag = math.sqrt(sum(i**2 for i in vector))
    return [i/mag for i in vector]

def clip(velocity):
    if velocity>1:
        velocity = 1.0
    elif velocity<-1:
        velocity = -1.0
    return velocity


def check_target_orientation(pepper, target):
    # Calculate position vector and target angle
    direction_to_target = [target[0] - pepper[u'position'][0], 0, target[2] - pepper[u'position'][2]]
    target_angle = math.atan2(direction_to_target[2], direction_to_target[0])

    turn_rate = target_angle - pepper[u'orientation'][1]
##    print("dtt: ", direction_to_target, ", angle: ", target_angle)
    # Normalise to -2pi<x<2pi range
    while turn_rate > math.pi:
        turn_rate -= 2 * math.pi
    while turn_rate < -math.pi:
        turn_rate += 2 * math.pi
    return turn_rate/(math.pi)
        
def check_target_distance(pepper, target):
    return math.sqrt( (pepper[u'position'][0] - target[0])**2 + (pepper[u'position'][2] - target[2])**2 )
    

def pepper_to_target(target):
    global live_data

    sleep_time = 0.3
    velocity = 0
    turn_rate = 0

    print('turning')
    done_turning = False
    while not done_turning:
        #print(live_data)
        if live_data!={}:
            pepper_data = live_data[u'Pepper']
            target_data = [0,0,0]
            turn_rate = check_target_orientation(pepper_data, target_data)
            if np.abs(turn_rate) > 0.1:
                time.sleep(sleep_time)
            else:
                done_turning = True
                turn_rate = 0
                
##        print("Turn rate: " + str(turn_rate))
        Nao.Move(velocity,0,turn_rate)
    
    print('driving')
    done_moving = False
    dist = 0
    while not done_moving:
        if live_data!={}:
            pepper_data = live_data[u'Pepper']
            target_data = [0, 0, 0]
            dist = check_target_distance(pepper_data, target_data)
            if check_target_distance(pepper_data, target_data) > 0:
                print("Distance: " +  str(dist))
                velocity = 0.3 * dist
                if velocity < 0.5:
                    velocity = 0.5
                time.sleep(sleep_time)
            else:
                done_moving = True
                velocity = 0
        Nao.Move(velocity,0,turn_rate)
        
##            bodies = read_rigid_body_data(file_path)
##            pepper = bodies[u'Pepper']
##            target = bodies[u'Glove']
##            time.sleep(0.5)

##    else:
##        if velocity > 0:
##            velocity -= 0.1
##        else:
##            velocity = 0



if __name__ == "__main__":
    # Run the WebSocket client in a separate thread to keep receiving updates
    client_thread = threading.Thread(target=start_websocket_client)
    client_thread.start()
    
    Nao.InitPose()
##    file_path = "C:/Users/20183464/OneDrive - TU Eindhoven/School/Master Thesis/Scripts/Experiment Robot assisted cleanup 2_scripts_14-07-2023/scripts/objects_data.json"

    # Turn off autonomous life features 
    amp=Nao.naoqi.ALProxy('ALAutonomousMoves',IP,PORT)
    alp=Nao.naoqi.ALProxy('ALAutonomousLife',IP,PORT)
    alp.setAutonomousAbilityEnabled('BasicAwareness', False)
    amp.setExpressiveListeningEnabled(False)
    Nao.motionProxy.setBreathEnabled("Body",False)
    Nao.motionProxy.setIdlePostureEnabled("Body",False)

    is_looping = True
    loop_count = 0
    loop_max = 10

##    robot.say("Thank you for participating in my experiment. I hope we can have lots of fun!")
##    pepper_to_target(file_path)
##    while is_looping:
##        bodies = read_rigid_body_data(file_path)
##        pepper = bodies[u'Pepper']
##        target = bodies[u'Target_1']
##        loop_count += 1
##        if loop_count == loop_max:
##            is_looping = False
##        
# Main loop to access live data as it updates
    try:
        while True:
            pepper_to_target(u'Glove')
                # Add more processing or logic as needed with the live data
##            time.sleep(0.01)  # Adjust frequency as needed
    except KeyboardInterrupt:
        print("Exiting script.")
    finally:
        ws.close()
        Nao.Crouch()
        
