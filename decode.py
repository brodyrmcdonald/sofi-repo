#maddie test
from tkinter import *
import base64
import binascii

decoding = { 
        "ASCII"  : '0', 
        "Base64" : '1'
        }

poly = '1011' 

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

def closePipe(): 
    print('pipe closed') 
    exit(0)

def extractPackets(e,infile):
    chunk_size = 16
    iter = 0
    fullStr=""
    byte = []
    fullMsg = bytes()
    
    #READ IN AS A STRING
    scheme = ''
    fullStr = ''
    errors=0
    numPackets = 0
    while True:
        chunk = infile.read(chunk_size)
        if chunk == '':
            closePipe()
        header = chunk[0:2]
        scheme = header[0]
        data = chunk[2:13]
        crcRem = chunk[13:16]
        numPackets += 1

        # if tail bit is set, break and treat last packet as decimal number 
        if header[1] == '1': 
            break 

        # basic error checking on header+data segments 
        if not crc_check((header+data),poly,crcRem): 
            print("Error detected")
            errors += 1 

        if not chunk: break
        #print(chunk[2:])
        fullStr = fullStr + data

    # convert data segment from last packet to decimal number 
    padLen = int(data,2)
    fullStr = fullStr[:(-1)*padLen] 

    # calculate bit error rate 
    bitErrRate = 0.0 
    if errors > 0: 
        bitErrRate = float(errors)/(numPackets*16)
    print('Bit error rate: ', bitErrRate)


    #INITIALIZE SIZE OF THE ARRAY
    byteFlip = [0]* ((int)(len(fullStr)/8)+1)
    bitCounter = 0
    num = 0
    for bit in fullStr:
        if(bitCounter == 8):
            num += 1
            bitCounter = 0
        if(bit == '0'):
            byteFlip[num] = byteFlip[num]<<1
        else:
            byteFlip[num] = (byteFlip[num]<<1)|1
        bitCounter += 1

    j = 0
    final = ""
    
    for i in byteFlip:
        final += chr(byteFlip[j])
        j+= 1
    if(scheme == '0'):
        print(final)
    elif (scheme == '1'):
        b64bytes = final.encode('ascii')
        msgbytes = base64.b64decode(b64bytes)
        b64final = msgbytes.decode('ascii')
        print(b64final)
        #https://stackabuse.com/encoding-and-decoding-base64-strings-in-python/
    
    return final

with open(sys.argv[1], 'r') as fin:
    x = ""
    while True:
        extractPackets(x,fin)
