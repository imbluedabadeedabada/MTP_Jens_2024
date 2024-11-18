import os

file_header = "experiment\terror\tmemory\n"

class stimulus():
    def __init__(self, initstring):
        fh=file_header.strip().split('\t')
        b=initstring.strip().split('\t')
        if len(b)==len(fh):
            self.experiment=int(b[0])
            self.error=int(b[1])
            self.memory=int(b[2])
        else :
            print("Could not initialize stimulus.")

    def __str__(self):
        return str(self.experiment) + "\t" + \
               str(self.error) + "\t" + \
               str(self.memory) + "\n"
        
    def experiment(self):
        return self.experiment
    def memory(self):
        return self.memory
    def error(self):
        return self.error
##    def pitch(self):
##        return self.pitch
##    def distance(self):
##        return self.distance
    
class measurement():
    def __init__(self, stim, handposx, handposy, handposz, RT):
        self.stim=stim
        self.RT=RT
        self.handposx=handposx
        self.handposy=handposy
        self.handposz=handposz
        
    def __str__(self):
        return str(self.stim).rstrip("\n") + "\t" + \
               str(self.handposx)   + "\t" + \
               str(self.handposy)  + "\t" + \
               str(self.handposz)+ "\t" + \
               str(self.RT) + "\n"

def save_measurement(f, m):
    f.write(str(m))
    
def save_experiment(output_file, exp):
    try:
        f=open(output_file, 'w')
        f.write(file_header)
        for m in exp:
           f.write(str(m))
        f.close()

    except IOError as e:
        print(e)

def open_outputfile(output_file):
    try:
        f=open(output_file, 'a')
        f.write(file_header)
        return f

    except IOError as e:
        print(e)
    
def close_outputfile(f):
    try:
        f.close()

    except IOError as e:
        print(e)
        
def read_stimuli(file_name):
    if os.path.exists(file_name):
        print('Reading: ' + file_name , end="")
        theFile=open(file_name)
        header=theFile.readline()
        theContent=theFile.readlines()
        stim=[]
        for theLine in theContent: 
            stim.append(stimulus(theLine))

        print( "... done.")
        return stim
    else:
        print("file not found.")
        return None

    

if __name__ == '__main__':
    stim=read_stimuli("stimuli.txt")
    m1=measurement(stim[1], 100, 23, -10, 22.5)
    m2=measurement(stim[2], 110, 3, 15, 10.1 )
    print(m1,end="")
    print(m2)
    save_experiment('test.txt',[m1, m2])
    f=open_outputfile('test2.txt')
    save_measurement(f,m1)
    save_measurement(f,m2)
    close_outputfile(f)
