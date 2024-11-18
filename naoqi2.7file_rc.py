import naoqi
from naoqi import ALProxy
import time

IP = "192.168.0.119"
tts = ALProxy("ALTextToSpeech", IP, 9559)

pepper = open("pepperzegt.txt", "r")
print(pepper.read())
pepper.close
is_looping = True
tts.say("Go.")
while is_looping:
    try:
        pepper= open("pepperzegt.txt", "r")
        peppersays = pepper.read()
        
        ######als file == 0 dan is geen item geselecteerd in het veld.
        #####green square
        if  peppersays == "1":
            tts.say("could you please place The green square in B. 1?")

        ############orange triangle
        if peppersays == "2":          
            tts.say("The orange triangle should go in C. 2")

        ########green circle
        if peppersays == "3":           
            tts.say("The green circle should go in A. 3")

        ###########Orange square
        if peppersays == "4":
            tts.say("can you place the orange square in B. 2?")
            
        ###########purple triangle
        if peppersays == "5":          
            tts.say("The purple triangle should go in A. 1")

        #########orange circle
        if peppersays == "6":            
            tts.say("The orange circle should go in B. 3")
            
        ########purple square
        if peppersays == "7":
            tts.say("Could you please place the purple square in C. 3?")
        
        #############green triangle
        if peppersays == "8":          
            tts.say("can you place the green triangle in A. 2?")

        ############Purple circle
        if peppersays == "9":   
            tts.say("can you place the purple circle in C. 1?")
            
        pepper.close
        pepper = open("pepperzegt.txt", "w")
        pepper.write("0")
        pepper.close
        time.sleep(2)
    finally:
        pass
