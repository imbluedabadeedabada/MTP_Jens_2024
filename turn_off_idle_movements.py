import nao_nocv_2_1 as nao

nao_ip = "192.168.0.116" #Bender
#nao_ip = "192.168.0.115" #Marvin
port = 9559

nao.InitProxy(nao_ip)
#nao.ConnectProxy('ALAutonomousMoves')
amp=nao.naoqi.ALProxy('ALAutonomousMoves',nao_ip,port)

print("Expressive listening enabled is", amp.getExpressiveListeningEnabled())
# The chain name ["Body", "Legs", "Arms", "LArm", "RArm", "Head"].
chain_names =["Body", "Legs", "Arms", "LArm", "RArm", "Head"]
for n in chain_names:
    print ("Breath enabled for", n , nao.motionProxy.getBreathEnabled(n) )
    print ("IdlePosture enabled for", n , nao.motionProxy.getIdlePostureEnabled(n))


amp.setExpressiveListeningEnabled(False)
nao.motionProxy.setBreathEnabled("Body",False)
nao.motionProxy.setIdlePostureEnabled("Body",False)
nao.Say("I'm done.")
