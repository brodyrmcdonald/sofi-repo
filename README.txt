Welcome to SoFi! 

This system consists of two main files. 

encode.py 
  This script starts a GUI for encoding user input and writes the 
  result to a named pipe. 

decode.py 
  This script reads from the named pipe that the encode module writes 
  to, and performs a CRC check on the data it reads. It reconstructs 
  the original message encoded by the encode module and displays it 
  in the terminal. 

To run: 
  Open two separate terminal windows
  In the first, run the following command: 

    $> python3 encode.py pipe 

  "pipe" is the named pipe that the encoding module will write to. If 
  it does not already exist, it will create one for you.

  In the other terminal, run the following command: 
  
    $> python3 decode.py pipe 
  
  Here, "pipe" must match the same name used in running the encode module. 

  At this point there should be a GUI window that accepts user input. 

  Select an encoding scheme, type your message in the input box, and press 
  "Go". Your input will be encoded, sent through the pipe, and will appear 
  as decoded text in the other terminal window along with a bit error rate. 
