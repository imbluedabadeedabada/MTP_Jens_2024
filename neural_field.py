
from definitions import *
import math     
import numpy as np
import matplotlib.pyplot as plt
from cosivina.numba import *
from getkey import getkey, keys

buffer = ''

def check_key(sim):
    key = getkey(blocking=False)

    if key == keys.UP:
        pass  # Handle the UP key
    elif key == keys.DOWN:
        pass  # Handle the DOWN key
    elif key.isdigit():
        ampl = sim.getElement('oml '+ key).amplitude
        if ampl > 4:
            print('object ' + key + ' removed.')
            set_inputs(sim, 'field OML', [int(key)], 0.0) #remove memory of object <key>
        else:
            print('object ' + key + ' added.')
            set_inputs(sim, 'field OML', [int(key)], 8.0) #restore memory of object <key>   
    else:  # Handle text characters
        pass
        #buffer += key
        #print(buffer)
    
    return key

# from cosivina import *
# from cosivina import Simulator
# #from cosivina.GaussKernel1D import *
# from cosivina.LateralInteractions1D import *
# from cosivina.GaussStimulus1D import *
# from cosivina.SumInputs import *
# # from cosivina.ScaleInput import *
# from cosivina.NeuralField import *
# # from cosivina.SumDimension import *
# from cosivina.NormalNoise import *

import sys
import time

hand_pos = [0,0]
num_objects = 10

def create_simulator():
 #neural field simulator############
    sim = Simulator()
    fieldSize = (1, 360)
    
    #########Neural field parameters
    sigma_exc = 6.0
    sigma_inh = 10.0
    ampl_exc = 5.0
    tau = 20.0
    h = -5.0
    beta = 4.0
    noise_level = 1.0
    noise_kernel_sigma = 0.0 # this just means a direct copy, so I removed the noise kernels and connected the noise elements directly
    noise_kernel_ampl = 1.0


    # create neural field IL
    IL_sigma_exc = sigma_exc
    IL_ampl_exc = 5.0
    IL_sigma_inh = 15
    IL_ampl_inh = 0.0
    IL_h = h*IL_ampl_exc/fieldSize[1] # makes sure only one bump exists at the same time
    sim.addElement(NeuralField('field IL', fieldSize, tau, h, beta))
    #sim.addElement(GaussKernel1D('IL -> IL', fieldSize[1], sigma_exc, ampl_exc, True, True), 'field IL', 'output', 'field IL')
    sim.addElement(LateralInteractions1D('IL -> IL', fieldSize, IL_sigma_exc, IL_ampl_exc, IL_sigma_inh, IL_ampl_inh, IL_h, True, True), 'field IL', 'output', 'field IL')
    sim.addElement(NormalNoise('noise IL', fieldSize, noise_level),[],[],'field IL')
    #sim.addElement(GaussKernel1D('noise kernel IL', fieldSize, noise_kernel_sigma, noise_kernel_ampl, True, True), 'noise IL', 'output', 'field IL') # smooths and spatially correlates noise
    
    # create neural field AOL (action observation)
    AOL_global_inhibition = -2.0 # make more sensitive to input
    AOL_IL_amplitude = 3.5 # 4.1
    AOL_kernel_sigma = 5.0
    AOL_kernel_ampl = 1.0
    sim.addElement(GaussStimulus1D('hand', fieldSize, sigma_exc, 0, round(0*fieldSize[1]), True, False))
    sim.addElement(NeuralField('field AOL', fieldSize, tau, AOL_global_inhibition, beta), 'hand','output')
    #sim.addElement(GaussKernel1D('hand position', fieldSize, 5, 1, True, True),'hand', 'output', 'field AOL')
    sim.addElement(GaussKernel1D('AOL -> IL', fieldSize, sigma_exc, AOL_IL_amplitude, True, True), 'field AOL', 'output', 'field IL')
    sim.addElement(NormalNoise('noise AOL', fieldSize, noise_level),[],[],'field AOL')
    #sim.addElement(GaussKernel1D('noise kernel AOL', fieldSize, noise_kernel_sigma, noise_kernel_ampl, True, True), 'noise AOL', 'output', 'field AOL')

    # create CSGL common shared goal layer
    csgl_il_ampl = 3.0
    sim.addElement(NeuralField('field CSGL', fieldSize, tau, h, beta))
    # create inputs
    obj_list=[]
    for obj in range(1,num_objects+1):
        lbl = 'obj ' + str(obj)
        sim.addElement(GaussStimulus1D( lbl, fieldSize, sigma_exc, 0, round((obj/10)*fieldSize[1]), True, False),[],[],'field CSGL')
        obj_list.append(lbl)
    # create DNF
    sim.addElement(SumInputs('summed inputs CSGL', fieldSize), obj_list)
    #sim.addElement(NeuralField('field CSGL', fieldSize, tau, h, beta), 'summed inputs CSGL')
    sim.addElement(GaussKernel1D('CSGL -> IL', fieldSize, sigma_exc, csgl_il_ampl, True, True), 'field CSGL', 'output', 'field IL')
    sim.addElement(NormalNoise('noise CSGL', fieldSize, noise_level),[],[],'field CSGL')
    #sim.addElement(GaussKernel1D('noise kernel CSGL', fieldSize, noise_kernel_sigma, noise_kernel_ampl, True, True), 'noise CSGL', 'output', 'field CSGL')


    # create OML - object memory layer
    # create inputs
    oml_il_ampl = 3.0
    oml_list=[]
    for obj in range(1,num_objects+1):
        lbl = 'oml ' + str(obj)
        sim.addElement(GaussStimulus1D( lbl, fieldSize, sigma_exc, 0, round((obj/10)*fieldSize[1]), True, False))
        oml_list.append(lbl)
    # create DNF
    sim.addElement(SumInputs('summed inputs OML', fieldSize), oml_list)
    sim.addElement(NeuralField('field OML', fieldSize, tau, h, beta), 'summed inputs OML')
    sim.addElement(GaussKernel1D('OML -> IL', fieldSize, sigma_exc, oml_il_ampl, True, True), 'field OML', 'output', 'field IL')
    sim.addElement(NormalNoise('noise objects', fieldSize, noise_level),[],[],'field OML')
    #sim.addElement(GaussKernel1D('noise kernel OML', fieldSize, noise_kernel_sigma, noise_kernel_ampl, True, True), 'noise OML', 'output', 'field OML')


    ####################################################
    ################## action execution Layer#####################
    AEL_sigma_exc = sigma_exc
    AEL_ampl_exc = 5.0 #make it input driven
    AEL_sigma_inh = 15.0
    AEL_ampl_inh =0.0
    AEL_h = h*AEL_ampl_exc/fieldSize[1]; # kills the competition
    IL_AEL_ampl = 10.0 #strong input needed to overcome global inhibition adn to react fast
   
    ################Summing objects
    #sim.addElement(GaussKernel1D('noise kernel AEL', fieldSize,noise_kernel_sigma, noise_kernel_ampl, True, True), 'noise AEL', 'output', 'field AEL')

    sim.addElement(NeuralField('field AEL', fieldSize, tau, h, beta))
    sim.addElement(GaussKernel1D('IL -> AEL', fieldSize, sigma_exc, IL_AEL_ampl, True, True), 'field IL', 'output', 'field AEL')
    #sim.addElement(GaussKernel1D('u -> action', fieldSize, sigma_exc, 5, true, true), 'field IL', 'activation', 'action layer')
    sim.addElement(LateralInteractions1D('AEL -> AEL', fieldSize, AEL_sigma_exc, AEL_ampl_exc, AEL_sigma_inh, AEL_ampl_inh, AEL_h, True, True), 'field AEL', 'output', 'field AEL')
    sim.addElement(NormalNoise('noise AEL', fieldSize, noise_level), [], [], 'field AEL')
    #% noise_kernel_sigma = 1 here -> noise gets spatial correlation, don't know why
    #sim.addElement(GaussKernel1D('noise kernel AEL', fieldSize, 1, noise_kernel_ampl, True, True), 'noise AEL', 'output', 'field AEL')


    return sim

# def create_field_inputs(sim, label, objects, target_field):
#     #create input driehoek
#     sim.addElement(GaussStimulus1D(label, fieldSize, sigma_exc, 5.5, round(1/7*fieldSize[1]), True, False))
    
#     obj_list=[]
#     for obj in objects:
#         lbl = 'obj ' + str(obj)
#         sim.addElement(GaussStimulus1D( lbl, fieldSize, sigma_exc, 2, round((obj/10)*fieldSize[1]), True, False))
#         ojb_list.append(lbl)
    
# #create neural field driehoek (t)
#     sim.addElement(SumInputs('summed obj ' + label, fieldSize), obj_list)
#     sim.addElement(NeuralField('object layer', fieldSize, 20, -5, 4), 'summed obj ' + label)
#     sim.addElement(NeuralField('field ' + target_field, fieldSize, 20, -5, 4), 'summed obj ' + label)
#     sim.addElement(GaussKernel1D(target_field + ' -> u', fieldSize, sigma_exc, 5, True, True), 'summed obj ' + label, 'output', 'field u')

# def check_and_do_action(sim, i, hand_range, message):
#     for i in hand_range:
#         if sim.getComponent('field AEL', 'activation')[0,i] > 1 and sim.getElementParameter('hand', 'position') >hand_range[0] and sim.getElementParameter('hand', 'position')< hand_range[1]:

#             pepper =  open("pepperzegt.txt", "w")
#             pepper.write(message)
#             pepper.close()
#             break

def set_inputs(sim, fieldname, obj_list, value):

    if fieldname=='field CSGL':
        prefix = 'obj '
    elif fieldname=='field OML':
        prefix = 'oml '

    for obj in obj_list:
        lbl = prefix + str(obj)
        sim.setElementParameters(lbl, 'amplitude', value)

def make_choice():
    keuze = input("Please make a choice between shape: triangles (t), squares (s) and circles (c).\n and colors: Pink (p), Orange (o), Green (g): ")
    #print(keuze)
    return keuze

def init_csgl_inputs(sim, keuze):

    if keuze=="t":
        obj_list = triangles
    elif keuze =="s":
        obj_list = squares
    elif keuze == "c":
        obj_list = circles
    elif keuze =="p":
        obj_list = purples
    elif keuze =="g":
        obj_list = greens
    elif keuze =="o":
        obj_list = oranges
    
    # init CSGL
    csgl_ampl_exc =8.0
    set_inputs(sim, 'field CSGL', range(1,10+1), 0.0)
    set_inputs(sim, 'field CSGL', obj_list, csgl_ampl_exc)

def init_oml_inputs(sim, objects_present):
    # init OML
    oml_ampl_exc=8.0
    set_inputs(sim, 'field OML', objects_present, oml_ampl_exc)

def plot_field(axis, sim, field_name, input_name):
    fieldSize = sim.getElement(field_name).size
    x = np.arange(fieldSize[1])
    the_lines = axis.plot(x, sim.getComponent(input_name, 'output')[0],'g',
            x, sim.getComponent(field_name, 'activation')[0], 'b',
            x, sim.getComponent(field_name, 'output')[0], 'r')
    axis.set_title(field_name)
    axis.set_xlim(0, fieldSize[1])
    axis.set_ylim(-10, 10)
    axis.set_ylabel('input/activation/output')

    plt.ion()
    plt.pause(1)


    return the_lines

def update_field(lines, sim, field_name, input_name):
    input      = sim.getComponent(input_name, 'output')
    activation = sim.getComponent(field_name, 'activation')
    output     = sim.getComponent(field_name, 'output')
    lines[0].set_ydata(input[0])
    lines[1].set_ydata(activation[0])
    lines[2].set_ydata(output[0])
        
def update_handpos(sim, hand_position, hand_amplitude):
    sim.setElementParameters('hand', 'position', hand_position)
    sim.setElementParameters('hand', 'amplitude', hand_amplitude)

def init_plots(sim):
     # prepare axes
    num_plots = 5
    fig, axes = plt.subplots(num_plots, 1)
    
    # plot initial state
    lns_aol = plot_field(axes[0],sim,'field AOL', 'hand')
    lns_csgl= plot_field(axes[1],sim,'field CSGL','summed inputs CSGL')
    lns_oml = plot_field(axes[2],sim,'field OML', 'summed inputs OML')
    lns_il  = plot_field(axes[3],sim,'field IL',  'AOL -> IL')
    lns_ael = plot_field(axes[4],sim,'field AEL', 'IL -> AEL')

    axes[num_plots-1].set_xlabel('feature space')

    return fig, axes
   
if __name__ == "__main__":
    sim_time = 0
    sim = create_simulator()
    sim.init()
    sim.saveSettings('test2.JSON')

     # prepare axes
    num_plots = 5
    fig, axes = plt.subplots(num_plots, 1)
    
    # plot initial state
    lns_aol = plot_field(axes[0],sim,'field AOL', 'hand')
    lns_csgl= plot_field(axes[1],sim,'field CSGL','summed inputs CSGL')
    lns_oml = plot_field(axes[2],sim,'field OML', 'summed inputs OML')
    lns_il  = plot_field(axes[3],sim,'field IL',  'AOL -> IL')
    lns_ael = plot_field(axes[4],sim,'field AEL', 'IL -> AEL')

    axes[num_plots-1].set_xlabel('feature space')
    
    keuze=make_choice()
    init_csgl_inputs(sim, keuze)
    init_oml_inputs(sim, range(1,int(num_objects/2) + 1))
    plt.ion()
    plt.pause(1)

   
    fsz=sim.getElement('field AEL').size[1]
    ael_objects = np.array([round((obj/10)*fsz) for obj in range(1,10+1)])

    is_looping = True
    plot_interval = 10
     # load parameter settings
    #sim.loadSettings('test2.JSON')
       
    while is_looping:
        key = check_key(sim)
        sim.step()
        ael=sim.getComponent('field AEL','output')[0]
        #max_value=ael.max()
        #max_index=ael.argmax()
        #print(max_value, max_index)

        ael_values = np.array([ael[pos%fsz] for pos in ael_objects])
        #print(ael_values.max(), ael_values.argmax())
        if ael_values.max()>0.95:
            #do_action()
            print("Action " + str(ael_values.argmax()+1) + " chosen.")
            is_looping = False


        hand_pos[0]+=0.02
        hand_pos[1]+=0.5
        hand_position = hand_pos[1]
        hand_amplitude = hand_pos[0] #np.sqrt(hand_pos[0]**2+hand_pos[1]**2)
        update_handpos(sim, hand_position, hand_amplitude)
        
        if sim.t%plot_interval==0:
            update_field(lns_aol, sim, 'field AOL', 'hand')
            update_field(lns_csgl, sim,'field CSGL','summed inputs CSGL')
            update_field(lns_oml, sim, 'field OML', 'summed inputs OML')
            update_field(lns_il, sim,  'field IL',  'AOL -> IL')
            update_field(lns_ael, sim, 'field AEL', 'IL -> AEL')
            
            plt.pause(0.01)
            fig.canvas.draw_idle()
            fig.canvas.flush_events()

    plt.close('all')
        
     

        
