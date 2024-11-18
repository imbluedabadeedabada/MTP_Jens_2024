import naoqi
from naoqi import ALProxy


IP = "192.168.0.119"
tts = ALProxy("ALTextToSpeech", IP, 9559)
postureProxy = ALProxy("ALRobotPosture", IP, 9559)
#postureProxy.goToPosture("Stand", 1.0)

#al = ALProxy("ALAutonomousLife", IP, 9559)
#al.setState("disabled")
postureProxy.goToPosture("StandInit", 1.0)

tts.say("Hello My name is Eve. Thank you for helping me out today. Since i cannot lift objects i want your help in placing the objects in front of you in the right place in the matrix. In a moment i will ask you which shape or color item you want to move, i will ask you this seperately for every item. I ask you to wait untill i say. \\pau=50\\ Go.\\pau=50\\ afterward i expect you to move your gloved hand towards the object. If i see which one you chose i will tell you where to place it in the matrix.")
tts.say("When you have placed the item in the matrix please put your hand on the cross on the table. ")
tts.say("If something happens or you do not want to continue just tell me and i will let the researcher in the room next to us know")
tts.say("Are you ready to start?")
