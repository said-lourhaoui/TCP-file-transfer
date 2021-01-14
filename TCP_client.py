#!/usr/bin/env python

import socket, random, time
from datetime import datetime
import xlwings as xw
from config import params
from timeit import default_timer as timer


TCP_IP = params["TCP_IP"]#'127.0.0.1'  # localhost
TCP_PORT = params["TCP_PORT"]#8091

packet_size = params["packet_size"] #60000
proba_err =params["proba_err"]  # error probability

T_p = params["T_p"]  # Propagation time

# Initialise the socket class
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
print("Begin")
# Open the file to send
f = open("myfile.txt", "rb")
#read the data
data = f.read()
data_size = len(data)
print("Data length : {} bytes".format(data_size))


total_packets = int(data_size/packet_size) + data_size%packet_size  # total packets to send

a = ['sent', 'lost'] #
b = [1-proba_err, proba_err ] # packet 'sent' has weight 1-p_err, packet 'lost' has weight p_err

try:
    #msg = input("Input your msg : ")
    i = 0
    sendt = timer() #datetime.now()
    while i*packet_size <= data_size :
        # select the packet to send
        if (i+1)*packet_size <= data_size :
            packet = data[i*packet_size : (i+1)*packet_size]
        else :
            packet = data[i*packet_size : ]

        # choose randomly whether the packet will be sent or lost
        sent_or_lost = (random.choices(a,b))[0]
        if sent_or_lost == 'sent' :  # simulation of packet sent
            # send the packet for the first try
            s.send(packet)
            # set acknoweledgment timeout
            s.settimeout(2*T_p)
            # set the acknowledgment boolean to false at the start
            ack = False
        else : # simulation of packet lost
            print("Packet is lost")
            # set acknoweledgment timeout
            s.settimeout(2*T_p)
            # set the acknowledgment boolean to false at the start
            ack = False

        # ARQ loop
        while True :
            # listen for acknoweledgment
            try:
                msg_received = s.recv(1024).decode()
                print("msg_received : ", msg_received)
                if msg_received == "ack":  #True
                    print("acknowledgment received")
                    # set ack flag to True
                    ack = True
                    # break this while loop and go back to the main loop
                    # to send another packet
                    break
            # if communication is timedout
            except socket.timeout :
                print("timeout")
                # choose randomly whether the packet will be resent or lost again
                sent_or_lost = (random.choices(a,b))[0]
                if sent_or_lost == 'sent' :  # simulation of packet resent
                    # send the packet again
                    s.send(packet)
                    print("Packet is resent")

                else : # simulation of packet lost
                    print("Packet is lost again")

        # Increment i to send the next packet
        i+=1
    recvt = timer() #datetime.now()

except Exception as ex:
    print("Exception : ",ex)

print("File transmitted")

#transfer_time = (recvt - sendt).seconds*1000+(recvt - sendt).microseconds/1000
transfer_time = (recvt - sendt)*1000

throughput    = data_size/(transfer_time) # message_size/transfer_time in Kbytes/s
print("Transfer time(ms) : {}, Throughput (Kbytes/s) : {}".format(transfer_time, throughput))
# closing socket and file
s.close()
f.close()

# # saving results in a file
# f_2 = open("results.txt", "a")
# f_2.write(str(throughput))
# f_2.close()
if input("Do you want to update the results in the excel file ? (y/n) : ") == 'y':
    app = xw.App(visible=False)
    excel_file = xw.Book("results.xlsx")
    currentSheet = excel_file.sheets["time_throughput_dataunit_p0"]
    max_row = currentSheet.range('A' + str(currentSheet.cells.last_cell.row)).end('up').row
    current_row = max_row + 1
    currentSheet["A{}".format(current_row)].value = transfer_time  # first column = transfer time
    currentSheet["B{}".format(current_row)].value = throughput  #second column = throughput
    currentSheet["C{}".format(current_row)].value = proba_err  #second column = error proba
    currentSheet["D{}".format(current_row)].value = packet_size  #second column = error proba

    excel_file.save()
    excel_file.close()
