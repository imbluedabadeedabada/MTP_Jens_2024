# import pepper #will not work directly as it needs python 2.7 while natnetclient needs python 3
import tracker
import neural_field
import read_stimuli
import time
import numpy as np
import sys
from definitions import pepper_file_name
from definitions import default_start_position
from definitions import dict_obj_position

start_position = (0.09444347769021988, 0.038085825741291046, 0.07298186421394348)
stop_position = None
timestr = ""

# def init_robot():
#         ######opening write file
#     ######
#     pepper.create_file("peppersays.txt")
#     pass

def init_tracker():
    print("Initialising tracker ... ",end="")
    tracker.init_tracker()
    print("done.")
    pass

def init_neural_field():
    print("Initialising neural field simulator ... ",end="")
    sim = neural_field.create_simulator()
    neural_field.set_inputs(sim, 'field OML', range(1,10), 8.0)
    sim.init()
    sim.saveSettings('dnf_config.JSON')
    print("done.")
    return sim

def read_file(ID):
    file_name = "stimuli_"+ID+".txt"
    stim = read_stimuli.read_stimuli(file_name)
    return stim

def write_data(ID, trial, data, start_pos, stop_pos):
    global timestr

    file_name = "result_"+str(ID)+'_'+timestr+".txt"
    f = open(file_name,'a')
    f.write(str(trial.experiment) + '\t' + str(trial.memory) + '\t' + str(trial.error) + '\t')
    f.write(str(data[0]) + '\t' + str(data[1]) + '\t' + str(data[2])+'\t'+ str(data[3])+'\t'+str(data[4])+'\t')
    f.write(str(start_pos[0])+'\t'+str(start_pos[1])+'\t'+str(start_pos[2])+'\t')
    f.write(str(stop_pos[0])+'\t'+str(stop_pos[1])+'\t'+str(stop_pos[2])+'\n')
    f.close()

def signal_pepper(key):
    file_name = pepper_file_name
    try:
        f = open(file_name,'w')
        f.write(key)
        f.close()
        return True
    except IOError:
        print("Cannot open file "+file_name+" for writing")
        return False
        

def do_trial(ID, trial, object_num, sim):
    state = "wait"
    while state!="done":
        if state == "wait":
            state = wait_for_hand()
            if state == "trial":
                input("Wait until hand is in start position.")
                start_position = np.array(default_start_position)
                # done = False
                # while not done:
                #     print('Detected start position: ',end='')
                #     print(tracker.current_position)
                #     s= input("Is this correct? [Enter if ok / n if not]")
                #     if s!="n":
                #         start_position = np.array(tracker.current_position)
                #         done = True
        elif state =="trial":
            timestr = time.strftime("-%Y%m%d-%H%M%S") # make this once for every recording    
            fname = 'optitrack_'+str(ID)+'_'+str(trial.experiment)+'_'+str(trial.memory)+'_'+str(trial.error)+'_'+str(object_num) + timestr + '.txt'
            
            signal_pepper('shape_color')
            keuze=neural_field.make_choice()
            neural_field.init_csgl_inputs(sim, keuze)
    
            #tracker.start_recording(fname)
            
            choice, RT, hand_position = run_trial(sim, fname)
            #stop_position = tracker.current_position
            signal_pepper(str(choice))
            
            s=input("Select which object was taken (1 - 9, 0 is 10): ")
            if s.isdigit():
                actual_object = int(s)
                if trial.memory ==1:
                    neural_field.set_inputs(sim, 'field OML', [actual_object], 0.0 )
            else:
                actual_object = -1
            if trial.error == 1:
                if actual_object >= 0 and actual_object != choice:
                    signal_pepper('Sorry, I made a mistake.')
                    print(str(actual_object))
                    input('press enter')
                    signal_pepper(str(actual_object))
                    input('press enter')
                    error_message = 1
                else:
                    error_message = 0
            else:
                error_message = -1
            write_data(ID, trial, [object_num, choice, RT, actual_object, error_message], start_position, hand_position )
            tracker.stop_recording()
            state ="done"

def wait_for_hand():
    try:
        signal_pepper('go_to_start')
        return "trial"
    except:
        time.sleep(3)
        return "wait"
    pass

def run_trial(sim, fname):
    fsz=sim.getElement('field AEL').size[1]
    ael_object_pos = np.array([round((obj/10)*fsz) for obj in range(1,10+1)])
    left_object = np.array(dict_obj_position["9"])
    right_object= np.array(dict_obj_position["1"])
    max_forward_distance = right_object[2] - start_position[2] #m
    max_lateral_distance = (left_object[0] - right_object[0]) #m objects 10cm apart
    sim.run(10,True) # reset and run 10 time steps
    start_time = time.time()
    print("go")
    tracker.start_recording(fname)
    
    signal_pepper('go')
    done = False
    while not done:
        sim.step()
        position = np.array(tracker.current_position) - start_position
        if position[2]>max_forward_distance:
            hand_position = (1 + 8*(position[0]-right_object[0])/max_lateral_distance)*fsz/10 #use actual position
        elif position[2]>0.01:
            predicted_position = start_position + position*max_forward_distance/position[2] # checked
            hand_position = (1 + 8*(predicted_position[0]-right_object[0])/max_lateral_distance)*fsz/10 #checked
        else:
            predicted_position = start_position + position*max_forward_distance/0.1 # do not extend more than ten times
            hand_position = (1 + 8*(predicted_position[0]-right_object[0])/max_lateral_distance)*fsz/10 #checked
             
        hand_amplitude = 5*position[2]/max_forward_distance
        if sim.t%10 == 0: # print every 10th time step
            print(position, hand_amplitude, hand_position)
        neural_field.update_handpos(sim, hand_position, hand_amplitude)
        ael=sim.getComponent('field AEL','output')[0]
        ael_values = np.array([ael[pos%fsz] for pos in ael_object_pos])
        #print(ael_values.max(), ael_values.argmax())
        if ael_values.max()>0.95:
            #do_action()
            choice = ael_values.argmax()+1
            reaction_time = time.time() - start_time
            print("Object " + str(choice) + " chosen.")
            done = True
    
    return choice, reaction_time, position

def do_questionnaire():
    signal_pepper("Now please do the questionaire.")
    s=input("Now do the questionnaire now and press enter when done.")
    return s

def main():
    global timestr
    #init_robot()
    s_client = init_tracker()
    sim=init_neural_field()
            

    subject_ID=input("Please enter the subject ID (including 0-s): ")
    exp = read_file('01')     # always read the same file otherwise use subject_ID
    timestr = time.strftime("%Y%m%d-%H%M%S") # make this once for every condition
    signal_pepper('intro')
    time.sleep(3)
    #tracker.do_command('LiveMode') # make sure Motive is sending something
    
    
    for trial in exp:
        print('Starting condition: experiment='+str(trial.experiment)+' memory='+str(trial.memory)+' error='+str(trial.error))
        if trial.experiment ==2:
            signal_pepper('misleading')
        input('Press enter when ready to start condition.')
        for object in range(1,10):
            print('-> object '+str(object))
            do_trial(subject_ID, trial, object, sim)
        do_questionnaire()
        

if __name__=="__main__":
    main()