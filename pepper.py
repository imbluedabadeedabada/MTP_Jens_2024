#python 2.7
import time
from definitions import *

# SIMULATED = True
# if not SIMULATED:
import naoqi
from naoqi import ALProxy

# overrided definitions
IP='192.168.7.76'
PORT=9559
tts = ALProxy("ALTextToSpeech", IP, PORT)
# else:
    # import pyttsx3
    # tts = pyttsx3.init()





def say(text):
    # if SIMULATED:
    #     tts.say(text) 
    #     tts.runAndWait() 
    #     tts.stop()
    # else:
    print(text)
    tts.say(text)

def make_text(object_key):
    (color, shape) = dict_objects[object_key.strip()]
    (row, col) = dict_map[object_key.strip()]
    text = "Could you please place the " + color + " " + shape + " in " + row + ". " + col + "?"
    return text

def create_file(file_name):
    try:
        f = open(file_name,'w')
        f.write('0')
        f.close()
    except IOError:
        print("Cannot open file \""+file_name+"\" for writing.")
    

if __name__=="__main__":
    #say(make_text("2"))

    try:
        pepper = open(pepper_file_name, "r")
    except IOError:
        create_file(pepper_file_name)
        pepper = open(pepper_file_name,'r')
    print(pepper.read())
    pepper.close()
    
    is_looping = True
    while is_looping:
        try:
            pepper= open(pepper_file_name, "r")
            peppersays = pepper.read().strip()
            if peppersays=="0":
                pepper.close()
                time.sleep(0.1)
                
                pass
            else:
                
                if peppersays == "intro":
                    # say("Hi, I am Eve. We are going to do an experiment. You will need to pick-up the objects in front of you and place them on the other table in the right location. " + \
                    # "I will tell you where to put it. " + \
                    # "You can give me a hint by telling which color or shape of object you will grasp. Are your ready?")
                    say("Hello My name is Eve. Thank you for helping me out today. Since i cannot lift objects i want your help in placing the objects in front of you in the right place in the grid. In a moment I will ask you which shape or color item you want to move, i will ask you this seperately for every item. I ask you to wait untill i say. \\pau=50\\ Go.\\pau=50\\ afterward i expect you to move your gloved hand towards the object. If i see which one you chose i will tell you where to place it in the grid.")
                    say("When you have placed the item in the grid please put your hand on the cross on the table. ")
                    say("If something happens or you do not want to continue just tell me and i will let the researcher in the room next to us know.")
                    say("Are you ready to start?")
                    #time.sleep(5)
                elif peppersays == "misleading":
                    say("This was the first experiment. Now we are going to do the second experiment. This time you need to lie about the shape or color of the object you are going to choose. So try to mislead me.")
                    #time.sleep(3)
                elif peppersays == "shape_color":
                    say("Which shape or color would you like to move?")
                    #time.sleep(2)
                elif peppersays == "go_to_start":
                    say("Please put your hand on the starting position.")
                    #time.sleep(2)
                elif peppersays=="go":
                    say("Go.")
                    #time.sleep(1)
                elif peppersays.isdigit():
                    say(make_text(peppersays))
                    time.sleep(2)
                else:
                    say(peppersays)
                    time.sleep(1)


                pepper.close()
                pepper = open(pepper_file_name, "w")
                pepper.write("0")
                pepper.close()
                time.sleep(0.1)
        finally:
            pass
