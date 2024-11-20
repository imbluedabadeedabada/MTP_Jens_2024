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

def clip(velocity):
    if velocity > 1:
        velocity = 1.0
    elif velocity < -1:
        velocity = -1.0
    return velocity


def check_target_orientation(pepper, target):
    # Calculate position vector and target angle
    direction_to_target = [target[0] - pepper[u'position'][0], 0, target[2] - pepper[u'position'][2]]
    target_angle = math.atan2(direction_to_target[0], direction_to_target[2])
    
    # Extract yaw (rotation around vertical/Y-axis) from quaternion
    qx, qy, qz, qw = pepper[u'orientation']
    yaw = math.atan2(2*(qw*qy + qx*qz), 1 - 2*(qy**2 + qz**2))
    turn_rate = target_angle - yaw

    # Normalise to -pi<x<pi interval
    turn_rate = (turn_rate + math.pi) % (2 * math.pi) - math.pi
    return turn_rate/(math.pi)
        
def check_target_distance(pepper, target):
    distance = math.sqrt((pepper[u'position'][0] - target[0])**2 + (pepper[u'position'][2] - target[2])**2)
    return np.abs(distance)
    
def pepper_to_target(target):
    global live_data

    sleep_time = 0.1

    print("Moving to target")
    moving = True
    while moving:
        if live_data[u'Pepper']:
            pepper_data = live_data[u'Pepper']
            
            # Check target orientation and distance
            turn_rate = check_target_orientation(pepper_data, target)
            dist = check_target_distance(pepper_data, target)
            
            # Adjust forward velocity based on distance
            if dist > 0.5:  # Minimum distance threshold
                velocity = 1
            elif 0.5 > dist > 0.1:
                velocity = clip(0.7 * dist)
            else:
                velocity = 0
            
            # Check if both distance and angle are within thresholds
            if dist <= 0.1 and np.abs(turn_rate) < 0.1:
                moving = False
                velocity = 0
                turn_rate = 0
                print("Target reached!")

            # Debugging information
            else:
                print("Distance:"+str(dist)+", Turn rate: "+str(turn_rate)+", Velocity: "+str(velocity))
            

            # Send combined movement commands
            Nao.Move(velocity, 0, turn_rate)
            
            # Take some time to allow processing of new data
            time.sleep(sleep_time)

def set_pepper_heading(target):
    global live_data
    
    heading_correct = False
    while not heading_correct:
        target_angle = check_target_orientation(live_data[u'Pepper'], target)
        if target_angle > 0.1:
            Nao.Move(0,0,target_angle)
        else:
            Nao.Move(0,0,0)
            print("Heading correct.")
            heading_correct = True

if __name__ == "__main__":
    # Run the WebSocket client in a separate thread to keep receiving updates
    client_thread = threading.Thread(target=start_websocket_client)
    client_thread.start()
    
    Nao.InitPose()

    # Turn off autonomous life features 
    amp=Nao.naoqi.ALProxy('ALAutonomousMoves',IP,PORT)
    alp=Nao.naoqi.ALProxy('ALAutonomousLife',IP,PORT)
    alp.setAutonomousAbilityEnabled('BasicAwareness', False)
    amp.setExpressiveListeningEnabled(False)
    Nao.motionProxy.setBreathEnabled("Body",False)
    Nao.motionProxy.setIdlePostureEnabled("Body",False)

    # Create dictionary containing all targets
        # Mind your coordinate system!
    inter_dist = 0.5
    targets = {'start': [0,0,-3], 'mid': [0,0,0], 'far_left': [2*inter_dist, 0, 0], 'mid_left': [inter_dist, 0, 0], 'mid_right': [-inter_dist, 0, 0], 'far_right': [-2*inter_dist, 0,0]}
    heading_dir = [0,0,inter_dist]

    # QoL/control implementation for experimenter
    trials_done = []
    full_reps = 0

    # Main
    try:
##        robot.say("Thank you for participating in my experiment. I hope we can have lots of fun!")

        # Take sleeptime to make sure everything is setup
        time.sleep(1)

        # Ask for commands to give to Pepper until the script can be quit
        cmd = raw_input("Command: ")
        while cmd != 'q':

            # Link all commands to a target location    
            if cmd == 'g':
                pepper_to_target(live_data[u'Glove'][u'position'])

            elif cmd == 's':
                pepper_to_target(targets['start'])
                set_pepper_heading(heading_dir)

            elif cmd == 'mid':
                pepper_to_target(targets['mid'])
                time.sleep(0.2)
                
                set_pepper_heading(heading_dir)
                trials_done.append(cmd)

            elif cmd == 'fl':
                pepper_to_target(targets['far_left'])
                time.sleep(0.2)
                
                set_pepper_heading(heading_dir)
                trials_done.append(cmd)

            elif cmd == 'ml':
                pepper_to_target(targets['mid_left'])
                time.sleep(0.2)
                
                set_pepper_heading(heading_dir)
                trials_done.append(cmd)

            elif cmd == 'mr':
                pepper_to_target(targets['mid_right'])
                time.sleep(0.2)
                
                set_pepper_heading(heading_dir)
                trials_done.append(cmd)

            elif cmd == 'fr':
                pepper_to_target(targets['far_right'])
                time.sleep(0.2)
                
                set_pepper_heading(heading_dir)
                trials_done.append(cmd)
                
            else:
                print("Command not recognised.")
                print("Options are: s, fl, ml, mid, mr, fr, q")

            # When all targets have been visited, show experimenter
            if len(trials_done) > 4:
                trials_done = []
                full_reps += 1
                print("All 5 trials done. That makes "+full_reps+" repetitions of the experiment.")
                
            cmd = raw_input("Command: ")

                
    except KeyboardInterrupt:
        pass
    finally:
        # End the experiment, then close all connections and terminate the script
##        robot.say("That was all for today. Thank you very much! I really enjoyed our time.")
##        time.sleep(5)
##        pepper_to_target(targets['start'])
        print("Exiting script.")
        ws.close()
        Nao.Crouch()
        
