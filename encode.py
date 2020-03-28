from tkinter import *
import base64 
import os

root = Tk()
root.title('SoFi')

encoding = { 
        "ASCII"  : '0', 
        "Base64" : '1'
        }

DATA_LEN = 11

# open file descriptor for fifo 
path = './' + sys.argv[1]
try: 
	os.mkfifo(path)
except: 
	None

fifo = os.open(path, os.O_RDWR|os.O_NONBLOCK)

'''
calculates the crc remainder given an input bit string with a three bit '0' pad and 
a modulo polynomial
'''
def crc_remainder(input_bitstring, polynomial_bitstring):
    polynomial_bitstring = polynomial_bitstring.lstrip('0')
    len_input = len(input_bitstring)-3
    input_padded_array = list(input_bitstring)
    while '1' in input_padded_array[:len_input]:
        cur_shift = input_padded_array.index('1')
        for i in range(len(polynomial_bitstring)):
            input_padded_array[cur_shift + i] = str(int(polynomial_bitstring[i] != input_padded_array[cur_shift + i]))
    return ''.join(input_padded_array)[len_input:]

'''
returns True there were no errors in the data, False if at least 1 error was detected
'''
def crc_check(input_bitstring, polynomial_bitstring, check_value):
    polynomial_bitstring = polynomial_bitstring.lstrip('0')
    len_input = len(input_bitstring)
    initial_padding = check_value
    input_padded_array = list(input_bitstring + initial_padding)
    while '1' in input_padded_array[:len_input]:
        cur_shift = input_padded_array.index('1')
        for i in range(len(polynomial_bitstring)):
            input_padded_array[cur_shift + i] = str(int(polynomial_bitstring[i] != input_padded_array[cur_shift + i]))
    return ('1' not in ''.join(input_padded_array)[len_input:])

''' 
takes a string and an encoding scheme and returns a stream of 
packets 
'''
def makePackets(s,e): 
    poly = '1011' 
    tmpPad = '000'

    # create binary message 
    message = "".join(["{:08b}".format(x) for x in e])
    padLen = DATA_LEN - (len(message)%DATA_LEN)
    for i in range(0,padLen): 
        message += '0' 

    '''
    print('message : ' + message)
    print('pad     : ' + str(padLen))
    '''

    # create a list of packets, each 16 bits long 
    # 2 bit header + 10 bit message + 3 bit crc check
    packetList = []
    for i in range(0, len(message), DATA_LEN): 
        # create header for first packets 
        header = encoding[s] + '0' 
        data = message[i:i+DATA_LEN]
        crcRem = crc_remainder((header + data + tmpPad), poly)

        packetList.append(header + data + crcRem) 

    # append tail packet, w/ tail bit set 
    # treat data segment of tail packet as decimal number of pad bits
    header = encoding[s] + '1'
    binPad = bin(padLen).replace('0b','')
    while len(binPad) < DATA_LEN: 
        binPad = '0' + binPad 
    # print('binary pad: ' + binPad)
    crcRem = crc_remainder((binPad + tmpPad), poly)
    tail = header + binPad + crcRem
    packetList.append(tail)

    # print(packetList)
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

    '''
    print('scheme  : ' + s)
    print('text    : ' + t)
    print('encoding: ' + e.decode())
    print('stream  : ' + makePackets(s,e))
    print()
    ''' 

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
