import socket, random
from config import params

TCP_IP = params["TCP_IP"]#'127.0.0.1'  # localhost
TCP_PORT = params["TCP_PORT"]#8091

packet_size = params["packet_size"] #60000
proba_err =params["proba_err"]  # error probability

a = ['sent', 'lost'] #
b = [1-proba_err, proba_err ] # packet 'sent' has weight 1-p_err, packet 'lost' has weight p_err

buffer = b'' # buffer that will contain received data
# Initialize the socket class
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Associate the STREAM socket with the specific IP and port number
s.bind((TCP_IP, TCP_PORT))
# Listen for incoming connections
s.listen()
# start connection
conn, addr = s.accept()
print('Connected to', addr)
while True :
    packet = conn.recv(packet_size)
    # print(packet)
    if not packet :
        break
    else : # a packet is received
        # choose randomly whether the ack will be sent or lost
        sent_or_lost = (random.choices(a,b))[0]
        if sent_or_lost == 'sent' :  # simulation of packet sent
            # send the ack
            conn.sendall("ack".encode())
            print("ack sent")
            # Add the acknowledged to the buffer
            buffer += packet
        else : # simulation of packet lost
            print("ack is lost")


# write a new file, when all the data is received
f = open("Receivedfile.txt", "wb")
f.write(buffer)
print("File saved")
# close file and socket
f.close()
s.close()
print("Connection is closed")
