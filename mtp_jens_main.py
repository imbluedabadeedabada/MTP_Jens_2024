#python 2.7
import time
from definitions import *
import sys
import numpy as np
import pygame
from pygame.locals import *
import csv
import Queue

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

# Initialize Pygame and the joystick to record button presses
pygame.init()
pygame.joystick.init() 
num_joysticks = pygame.joystick.get_count()
if num_joysticks < 2:
    print("Please connect 2 joysticks")
    sys.exit(0)

joystick1 = pygame.joystick.Joystick(0)
joystick1.init()
joystick2 = pygame.joystick.Joystick(1)
joystick2.init()
print("Joysticks initialized")

# Initialise global variables for further use
live_data = {}
ws = None
formation = None
p1_id = 5
p2_id = 6
trial_state = {"p1": False, "p2": False}
button_queue = Queue.Queue()

# Create output file for recording stopping distances (or a test file)
# output_file = "C:/Users/20183464/OneDrive - TU Eindhoven/School/Master Thesis/Scripts/Experiment Robot assisted cleanup 2_scripts_14-07-2023/scripts/mtp_jens_output.csv"
output_file = "C:/Users/20183464/OneDrive - TU Eindhoven/School/Master Thesis/Scripts/Experiment Robot assisted cleanup 2_scripts_14-07-2023/scripts/mtp_jens_testing.csv"

try:
    with open(output_file, 'r') as f:
        # File exists, set participant IDs to the next available numbers
        reader = csv.reader(f)
        rows = list(reader)
        if len(rows) > 1:
            ids_present = []
            for row in rows[1:]:
                if row[0] != "" and int(row[0]) not in ids_present:
                    ids_present.append(int(row[0]))
            p1_id = np.max(ids_present) + 1
            p2_id = p1_id + 1
        
except IOError:
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Participant", "Target", "Formation", "Distance", "Side", "Comfort", "Trial"]) # Create file with headers

def record_stopping_distance(participant, target, distance, side, trial):
    global output_file, formation

    with open(output_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([participant, target, formation, distance, side, None, trial])

def process_button_presses():
    global button_queue, p1_id, p2_id, trial_state

    # Process button presses from the queue
    while not button_queue.empty():
        participant, side = button_queue.get()
        if participant == p1_id and not trial_state["p1"]:
            # Mark Participant 1 as having logged for this trial
            trial_state["p1"] = True  
            return participant, side
        elif participant == p2_id and not trial_state["p2"]:
            # Mark Participant 2 as having logged for this trial
            trial_state["p2"] = True  
            return participant, side
    return None, None

def button_pressed():
    # Check if button[0] (A button) is pressed on either controller
    global joystick1, joystick2, p1_id, p2_id

    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if event.joy == 0 and event.button == 0:
                button_queue.put((p1_id, "Left"))  # Add Participant 1's press to the queue
            elif event.joy == 1 and event.button == 0:
                button_queue.put((p2_id, "Right"))  # Add Participant 2's press to the queue

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
    ws = websocket.WebSocketApp("ws://192.168.0.101:8000",on_message=on_message,on_error=on_error,on_close=on_close)
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
    target_angle = target_angle - yaw

    # Normalise to -pi<x<pi interval
    target_angle = (target_angle + math.pi) % (2 * math.pi) - math.pi
    return target_angle/(math.pi) # Nao.Move() needs a value between -1 and 1
        
def check_target_distance(pepper, target):
    distance = math.sqrt((pepper[u'position'][0] - target[0])**2 + (pepper[u'position'][2] - target[2])**2)
    return np.abs(distance)
    
def pepper_to_target(target, condition, trial_nr):
    global live_data, trial_state

    sleep_time = 0.1

    print("Moving to target")
    moving = True

    # Reset trial state at the start of each trial
    trial_state["p1"] = False
    trial_state["p2"] = False

    # Define conditions where button presses are logged
    logged_conditions = ['mid', 'fl', 'ml', 'mr', 'fr']

    while moving:
        if live_data[u'Pepper']:
            pepper_data = live_data[u'Pepper']
            
            # Check target orientation and distance
            turn_speed = check_target_orientation(pepper_data, target)
            dist = check_target_distance(pepper_data, target)

            # If relevant, check for button presses
            if condition in logged_conditions:
                # Add button presses to the queue, then process them
                button_pressed()  
                pressed_by, participant_side = process_button_presses()

                if pressed_by != None:
                    record_stopping_distance(pressed_by, condition, dist, participant_side, trial_nr)
            
            # Adjust forward velocity based on distance
            if dist > 0.5:  # Minimum distance threshold
                velocity = 1
            elif 0.5 > dist > 0.1:
                velocity = clip(0.7 * dist)
            else:
                velocity = 0
            
            # Check if both distance and angle are within thresholds
            if dist <= 0.1:
                moving = False
                velocity = 0
                turn_speed = 0
                print("Target reached!")

            # Debugging information
            else:
                # print("Distance:"+str(dist)+", Turn rate: "+str(turn_speed)+", Velocity: "+str(velocity))
                pass

            # Send combined movement commands
            Nao.Move(velocity, 0, turn_speed)
            
            # Take some time to allow processing of new data
            time.sleep(sleep_time)

    # At the end of the trial, log missing data for participants who did not press
    if condition in logged_conditions:
        if not trial_state["p1"]:
            record_stopping_distance(p1_id, condition, None, "Left", trial_nr)

        if not trial_state["p2"]:
            record_stopping_distance(p2_id, condition, None, "Right", trial_nr)

def set_pepper_heading(target):
    global live_data
    
    heading_correct = False
    target_angle = check_target_orientation(live_data[u'Pepper'], target)

    while not heading_correct:
        if np.abs(target_angle) > 0.3:
            Nao.Move(0,0,np.sign(target_angle))
        elif np.abs(target_angle) > 0.005:
            Nao.Move(0,0,2*target_angle)
        else:
            Nao.Move(0,0,0)
            print( target_angle, live_data[u'Pepper'][u'orientation'])
            print("Heading correct.")
            heading_correct = True
        time.sleep(0.1)
        target_angle = check_target_orientation(live_data[u'Pepper'], target)


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
    heading_dir = [0,0,1]

    # QoL/control implementation for experimenter
    trials_done = []
    formations = ['H', 'I', 'L']
    full_reps = 0
    max_reps = 9
    trials = 0
    formation = raw_input("Enter formation "+str(formations)+": ")

    # Main
    try:
        robot.say("Thank you for participating in my experiment. I hope we can have lots of fun!")

        # Take sleeptime to make sure everything is setup
        time.sleep(1)

        # Ask for commands to give to Pepper until the script can be quit
        cmd = raw_input("Command: ")
        while cmd != 'q':

            # Link all commands to a target location    
            if cmd == 's':
                pepper_to_target(targets['start'], cmd, trials)
                # set_pepper_heading(heading_dir)

            elif cmd == 'mid':
                pepper_to_target(targets['mid'], cmd, trials)
                time.sleep(0.2)
                
                set_pepper_heading(heading_dir)
                trials_done.append(cmd)
                trials += 1
                robot.say("Hello there, I am Eve.")

            elif cmd == 'fl':
                pepper_to_target(targets['far_left'], cmd, trials)
                time.sleep(0.2)
                
                set_pepper_heading(heading_dir)
                trials_done.append(cmd)
                trials += 1
                robot.say("Hi, it's nice to meet you!")

            elif cmd == 'ml':
                pepper_to_target(targets['mid_left'], cmd, trials)
                time.sleep(0.2)
                
                set_pepper_heading(heading_dir)
                trials_done.append(cmd)
                trials += 1
                robot.say("I am having a lot of fun today.")

            elif cmd == 'mr':
                pepper_to_target(targets['mid_right'], cmd, trials)
                time.sleep(0.2)
                
                set_pepper_heading(heading_dir)
                trials_done.append(cmd)
                trials += 1
                robot.say("This a great day for an experiment.")

            elif cmd == 'fr':
                pepper_to_target(targets['far_right'], cmd, trials)
                time.sleep(0.2)
                
                set_pepper_heading(heading_dir)
                trials_done.append(cmd)
                trials += 1
                robot.say("It's very nice to see you")

            elif cmd == 'prints':
                qx, qy, qz, qw = live_data[u'Pepper'][u'orientation']
                yaw = math.atan2(2*(qw*qy + qx*qz), 1 - 2*(qy**2 + qz**2))
                yaw = yaw/(2*math.pi)*360
                print("Pepper orientation: "+str(yaw))
                print("Pepper position: "+str(live_data[u'Pepper'][u'position']))

            elif cmd == 'heading':
                set_pepper_heading(heading_dir)
                print("Heading set.")    

            else:
                print("Command not recognised.")
                print("Options are: s, fl, ml, mid, mr, fr, heading, prints, q")

            # When all targets have been visited, show experimenter
            if len(trials_done) > 4:
                trials_done = []
                full_reps += 1
                trials = 0
                print("All 5 trials done. That makes "+str(full_reps)+" repetitions of the experiment.")
                if (full_reps % 3) == 0:
                    formation = raw_input("Enter formation "+str(formations)+": ")
                    # formations.remove(formation)

            else:
                print("The following trials have been completed so far in this rep: "+str(trials_done))

            # Turn off autonomous life features 
            # amp=Nao.naoqi.ALProxy('ALAutonomousMoves',IP,PORT)
            # alp=Nao.naoqi.ALProxy('ALAutonomousLife',IP,PORT)
            alp.setAutonomousAbilityEnabled('BasicAwareness', False)
            amp.setExpressiveListeningEnabled(False)
            Nao.motionProxy.setBreathEnabled("Body",False)
            Nao.motionProxy.setIdlePostureEnabled("Body",False)  
            cmd = raw_input("Command: ")

                
    except KeyboardInterrupt:
        pass
    finally:
        # End the experiment, then close all connections and terminate the script
        robot.say("That was all for today. Thank you very much! I really enjoyed our time.")
        time.sleep(5)
        pepper_to_target(targets['start'], cmd, trials)
        print("Exiting script.")
        ws.close()
        pygame.quit()
        Nao.Crouch()
        
