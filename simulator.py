from tkinter import *
import os 
from multiprocessing import Event,Process,Pipe


if len(sys.argv) != 3: 
    print('Usage: ')
    print('python3 simulator.py [input_pipe] [output_pipe]')
    exit(1)

# reads from bash pipe and writes to python Pipe 
# from which the GUI will read 
def reader(inPipe,pipe,stop): 
    while not stop.is_set():
        txt = inPipe.read(16)
        pipe.send(txt)

# function to update bits to send box
def appendToTextBox(textBox,text): 
    textBox.configure(state='normal') 
    textBox.insert(END, text)
    textBox.configure(state='disabled')

def clearTextBox(textBox):
    textBox.configure(state='normal')
    textBox.delete('1.0','1.end')
    textBox.configure(state='disabled')

def nextPacket(editText,currentText,outPipe): 
    packet = editText.get('1.0','end-1c')
    editText.delete('1.0',END)
    currentText.configure(state='normal')
    currentText.delete('1.0','1.16')
    currentText.configure(state='disabled')
    os.write(outPipe,packet.encode())

def sendAll(editText,currentText,outPipe): 
    currentText.configure(state='normal')
    msg = currentText.get('1.0','end-1c')
    currentText.delete('1.0','end-1c')
    currentText.configure(state='disabled')
    editText.delete('1.0',END)

    os.write(outPipe,msg.encode())



class updatingGUI(Frame): 
    def __init__(self,parent,inPipe,outPipe): 
        Frame.__init__(self,parent)
        self.inPipe = inPipe
        self.outPipe = outPipe
        self.parent = parent 
        self.stop_event = Event()

        # python Pipes 
        self.parent_pipe,self.child_pipe = Pipe()

        # make title frame
        self.topframe = Frame(root)
        self.topframe.pack(side=TOP)

        self.l = Label(self.topframe, text='SoFi Simulator')
        self.l.pack(side=TOP)

        # make current buffer frame
        self.currentBuffer = Frame(self,padx=10,pady=5)
        self.currentBuffer.pack(side=TOP)

        # label for current buffer box
        self.label1 = Label(self.currentBuffer, text='Bits to send')
        self.label1.pack(side=LEFT)

        # actual text box of current buffer
        self.currentText = Text(self.currentBuffer, height=5, width=64)
        self.currentText.pack()
        # self.currentText.insert(END, 'Waiting...')
        self.currentText.configure(state='disabled')

        # make user edit frame
        self.editFrame = Frame(self,padx=10,pady=10)
        self.editFrame.pack(side=BOTTOM)

        # label for user edits
        self.label2 = Label(self.editFrame, text='Current Packet')
        self.label2.pack(side=LEFT)

        # input box for user edits
        self.editText = Text(self.editFrame, height=1, width=64)
        self.editText.pack()

        # create send all button and add to frame
        func=lambda: sendAll(self.editText,self.currentText,outPipe)
        self.sendAllButton = Button(self.editFrame, 
                                    text='Send All',
                                    padx=5, 
                                    command=func)        
        self.sendAllButton.pack(side=LEFT)

        # create next packet button and add to frame
        func = lambda: nextPacket(self.editText,self.currentText,outPipe)
        self.nextPacketButton = Button(self.editFrame,
                                    text='Next Packet',
                                    padx=5,
                                    command=func)
        self.nextPacketButton.pack(side=LEFT) 

        # process to read from pipe 
        self.reader = Process(target=reader,
                args=(inPipe,self.child_pipe,self.stop_event))
        self.reader.start()

        self.update()

    def quit(self): 
        self.stop_event.set()
        self.inPipe.close()
        os.close(self.outPipe)
        self.reader.terminate()
        self.parent.destroy()


    # update function for the GUI
    # read from the pipe and write contents to the text box 
    def update(self): 
        while self.parent_pipe.poll(): 
            # grab data from python Pipe 
            txt = self.parent_pipe.recv()

            #update bits to send box
            appendToTextBox(self.currentText,txt)

        # editText box is empty and currentText box is not, 
        # take 16 chars and put in edit text 
        editTextIsEmpty = self.editText.compare("end-1c", "==", "1.0")
        currentTextNotEmpty  = self.currentText.compare('end-1c','!=','1.0')
        if  editTextIsEmpty and currentTextNotEmpty:
            # take 16 bits from the currentText box 
            packet = self.currentText.get('1.0','1.16') 
            self.currentText.delete('1.0','1.16')

            # insert packet into edit text box
            self.editText.insert(END, packet)


        self.parent.after(200,self.update)

def delete(gui): 
    gui.quit()

# set up input and output pipes
inPath = './' + sys.argv[1]
outPath = './' + sys.argv[2]

# make the fifos if they don't already exist
try: 
    os.mkfifo(inPath)
except FileExistsError: 
    None

try: 
    os.mkfifo(outPath)
except FileExistsError: 
    None

# open a file object on the fifos 
outPipe = os.open(outPath, os.O_RDWR|os.O_NONBLOCK)
inPipe = open(inPath, 'r')

# root for gui 
root = Tk()
root.title('Simulator')

# build the gui
gui = updatingGUI(root,inPipe,outPipe)
gui.pack()

# run the gui
root.protocol("WM_DELETE_WINDOW", lambda:delete(gui))
root.mainloop()
