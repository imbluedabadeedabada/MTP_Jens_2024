import naoqi
from naoqi import ALProxy
import time

IP = "192.168.0.119"
tts = ALProxy("ALTextToSpeech", IP, 9559)

tts.say("Which shape or color would you like to move?")
