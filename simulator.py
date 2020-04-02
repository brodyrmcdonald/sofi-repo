from tkinter import *
import os 

root = Tk()
root.title('Simulator')

if len(sys.argv) != 3: 
  print('Usage: ')
  print('python3 simulator.py [input_pipe] [output_pipe]')
  exit(1)

# function to update bits to send box
def updateBitBufferBox(textBox,text,line): 
  lineNo = str(line) 

  textBox.configure(state='normal') 
  textBox.delete(lineNo+'.0', lineNo+'.end')
  textBox.insert(END, text)
  textBox.configure(state='disabled')

# gui stuff 
# make title frame
topframe = Frame(root)
topframe.pack(side=TOP)

l = Label(topframe, text='SoFi Simulator')
l.pack(side=TOP)

# make current buffer frame
currentBuffer = Frame(root,padx=10,pady=5)
currentBuffer.pack(side=TOP)

# label for current buffer box
label1 = Label(currentBuffer, text='Bits to send')
label1.pack(side=LEFT)

# actual test box of cureent buffer
currentText = Text(currentBuffer, height=1, width=50)
currentText.pack()
currentText.configure(state='disabled')
updateBitBufferBox(currentText, 'Hello',1)

root.mainloop()



# set up input and output pipes
inPath = './' + sys.argv[1]
outPath = './' + sys.argv[2]

# make the fifos if they don't already exist
try: 
  os.mkfifo(inPath)
  os.mkfifo(outPath)
except FileExistsError: 
  None

# open a file object on the fifos 
inPipe = os.open(inPath, os.O_RDWR|os.O_NONBLOCK)
outPipe = os.open(inPath, os.O_RDWR|os.O_NONBLOCK)

while True: 
  text = inPipe.read()
  updateBitBufferBox(currentText, text, 1)

