This system consists of three main files. 

encode.py 
    This script starts a GUI for encoding user input and writes the 
    result to a named pipe. 

decode.py 
    This script reads from the named pipe that the encode module writes 
    to, and performs a CRC check on the data it reads. It reconstructs 
    the original message encoded by the encode module and displays it 
    in the terminal. 

simulator.py
    This runs a simulator window for the system designed as a placeholder
    for testing. The window allows the user to peek at and modify bits
    while they are in transmission. The upper text box displays the 
    current bits in transmission and the lower text box allows the user 
    to edit the next packet to be transmitted. 

----------------------------------------------------------------------------

System setup: 

    This system is based on a series of pipes that communicate between 
    programs. The encoding module will write encoded message to a named pipe. 
    The decoding module will subsequently read from a named pipe the encoded 
    messages, decode them, and display them on the terminal. The simulator
    steps in between the encoding and decoding modules, allowing the user 
    to modify bits as they are in transmission. This is meant to simulate 
    noise and error in transmission. Reference the below diagram: 

     encody.py --> input pipe --> simulator.py --> output pipe --> decode.py

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

To run the simulator: 
    Open three separate terminal windows.
    In the first run the following command:  

        $> python3 encode.py in 

    As above, "in" is the name of the named pipe that the encoding module 
    will write encoded messages to. 

    In the second terminal run the following command: 

        $> python3 simulator.py in out

    The first argument to the simulator is the input pipe to the system. 
    This must match the name of the pipe used to the encoding module above. 
    The second argument is the name of the output pipe for the system, if 
    it does not exist already, the script will make one for you. 

    In the third terminal run the following command: 

        $> python3 decode.py out 

    As before, "out" is the name of the pipe that the decoding module 
    will read from. This is being written to by the simulator to represent 
    transmission across a medium. 

    At this point there will be two GUI windows. Choose an encoding scheme, 
    Type a message into the input box for the encoding module and press go. 
    The encoded message will now appear in the simulator window as a sequence 
    of bits. Press the "Send All" button in the window to empty the buffer 
    and write the whole message, or the "Send Packet" button to send just 
    the contents of the lower text box. Edits can be made to the lower text 
    box to simulate errors in transmission. Alternatively, there is a "Drop 
    Packet" button that drops the next packet entirely from the system. The 
    decoder does not handle this type of error very well, as it has no 
    visibility on the number of packets that are sent in a transmission. 

----------------------------------------------------------------------------

More on the simulator: 
    The upper text box of the simulator should be considered a queued buffer 
    of packets. Edits may not be made here by the user. The lower text box is
    open to user edits, and is automatically updated with the next packet in 
    the queue. The contents of the lower text box should always match the 
    first 16 bits of the upper text box, because these bits represent the 
    next packet in the queue. The decoding module features single bit error 
    correction per packet, so one bit flip per packet is correctable by the
    decoder. Multiple bit flips in a packet are not easily handled and 
    cannot be corrected by the decoder. 
