from tkinter import *
import base64
import binascii
import sys

decoding = { 
        "ASCII"  : '0', 
        "Base64" : '1'
        }

DATA_LEN = 10
R = 4 

def detectError(arr, nr):
    n = len(arr)
    res = 0

    for i in range(nr):
      val = 0
      for j in range(1, n + 1):
        if(j & (2**i) == (2**i)):
          val = val ^ int(arr[-1 * j])

      res = res + val*(10**i)

    return int(str(res), 2)

def removeRedundantBits(arr, r):
    tmp = arr[::-1]
    res = tmp[2] + tmp[4:7] + tmp[8:]

    return res[::-1]

def correctError(arr, error): 
  if error == 0: 
    return arr,0

  tmp = list(arr[::-1])
  if tmp[error-1] == '1': 
    tmp[error-1] = '0'
  else: 
    tmp[error-1] = '1'

  res = ''.join(tmp[::-1])
  return res,1
		

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
        dataSeg = chunk[2:]
        numPackets += 1


        # basic error checking on header+data segments 
        errorPos = detectError(dataSeg,R)
        data,numErrors = correctError(dataSeg,errorPos)
        errors += numErrors
        data = removeRedundantBits(data,R)

        # if tail bit is set, break and treat last packet as decimal number 
        if header[1] == '1': 
            break 

        fullStr = fullStr + data

    # convert data segment from last packet to decimal number 
    padLen = int(data,2)
    fullStr = fullStr[:(-1)*padLen] 

    # calculate bit error rate 
    bitErrRate = 0.0 
    if errors > 0: 
        bitErrRate = float(errors)/(numPackets*16)
    print('Bit error rate: ', bitErrRate)
    errors = 0


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
        try:
            b64bytes = final.encode('ascii', 'ignore')
            msgbytes = base64.b64decode(b64bytes)
            b64final = msgbytes.decode('ascii')
            print(b64final)
        #https://stackabuse.com/encoding-and-decoding-base64-strings-in-python/
        except:
            e = sys.exc_info()
            print( "Error! Too many incorrect bits received")
    return final

with open(sys.argv[1], 'r') as fin:
    x = ""
    while True:
        extractPackets(x,fin)
