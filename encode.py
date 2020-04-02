#maddie test
from tkinter import *
import base64 
import os

root = Tk()
root.title('SoFi')

encoding = { 
        "ASCII"  : '0', 
        "Base64" : '1'
        }

# number of data bits per packet
DATA_LEN = 10

# redundant bits for error checking 
R = 4

# open file descriptor for fifo 
path = './' + sys.argv[1]
try: 
	os.mkfifo(path)
except: 
	None

fifo = os.open(path, os.O_RDWR|os.O_NONBLOCK)


def posRedundantBits(data, r): 
  # put a 0 at any bit pos that's a power of 2 
  j = 0
  k = 1
  m = len(data) 
  res = '' 

  # if bit pos == 2**j, append 0
  for i in range(1, m+r+1): 
    if i == 2**j: 
      res = res+'0'
      j+=1
    else: 
      res = res + data[-1*k] 
      k+=1

  # return reverse of result
  return res[::-1]

def calcParityBits(arr, r):
  n = len(arr)

  for i in range(r): 
    val = 0
    for j in range(1, n + 1): 
      if(j & (2**i) == (2**i)): 
        val = val ^ int(arr[-1 * j]) 
      arr = arr[:n-(2**i)] + str(val) + arr[n-(2**i)+1:] 
  return arr


'''
takes a string and an encoding scheme and returns a stream of 
packets 
'''
def makePackets(s,e): 
  # create binary message 
    message = "".join(["{:08b}".format(x) for x in e])
    padLen = DATA_LEN - (len(message)%DATA_LEN)
    for i in range(0,padLen): 
      message += '0' 

    # create a list of packets, each 16 bits long 
    # 2 bit header + 10 bit message + 3 bit crc check
    packetList = []
    for i in range(0, len(message), DATA_LEN): 
      # create header for first packets 
        header = encoding[s] + '0' 
        dataSeg = message[i:i+DATA_LEN]
        data = posRedundantBits(dataSeg,R)
        data = calcParityBits(data, R)

        packetList.append(header + data) 

    # append tail packet, w/ tail bit set 
    # treat data segment of tail packet as decimal number of pad bits
    header = encoding[s] + '1'
    binPad = bin(padLen).replace('0b','')
    while len(binPad) < DATA_LEN: 
      binPad = '0' + binPad 
    binPad = posRedundantBits(binPad,R)
    binPad = calcParityBits(binPad,R)
    tail = header + binPad
    packetList.append(tail)

    # join packets and return
    packetStream = ''.join(packetList)
    return packetStream


def getInput(): 
    s = variable.get() 
    t = inputbox.get()
    try: 
        tmp = t.encode('ascii') 
    except UnicodeEncodeError: 
        print("Error: unauthorized input detected")  
        return 

    if not t or t.isspace(): 
        print("Error: no input string detected") 
        return

    if s == 'ASCII': 
        e = tmp 
    elif s == 'Base64' :
        e = base64.b64encode(tmp) 

    # write makePackets to fifo
    stream = makePackets(s,e)
    os.write(fifo, stream.encode())


#make title frame 
topframe = Frame(root) 
topframe.pack(side=TOP)

l = Label(topframe, text='Welcome to SoFi')
l.pack(side = TOP)

#make encoding frame 
encodingframe = Frame(root, padx=10, pady=5)
encodingframe.pack(side = TOP)

label1 = Label(encodingframe, text="1. Choose an encoding scheme: ")
label1.pack(side = LEFT)

OPTIONS = ['ASCII', 'Base64']

variable = StringVar(root)
variable.set('ASCII') #default value

encodingmenu = OptionMenu(encodingframe, variable, *OPTIONS)
encodingmenu.configure(width=7)
encodingmenu.pack(side = TOP)

#take user input 
inputframe = Frame(root, padx=10, pady=5) 
inputframe.pack(side = TOP)

label2 = Label(inputframe, text='2. Enter text: ')
label2.pack(side = LEFT)

inputbox = Entry(inputframe, width=20)
inputbox.pack(side = LEFT)

go = Button(inputframe, text='Go', padx=5, command=lambda: getInput())

go.pack(side = LEFT)

root.mainloop()
