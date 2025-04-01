import socket
import os
import time
import struct
import select

ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2

def checksum(data):
    csum = 0
    countTo = (len(data) // 2) * 2
    count = 0
    
    # This loop processes data in 2-byte chunks
    # converts each chunk to a 16 bit integer
    # then adds each 16-bit val to running checksum
    while count < countTo:
        thisVal = data[count+1] * 256 + data[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(data):
        csum = csum + data[len(data) - 1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def build_packet():
    # checksum
    cs = 0
    # 12-bit identifier from the process ID to uniquely identify this process's packets
    ID = os.getpid() & 0xFFF
    # make a dummy header with 0 checksum
    # 
    header = struct.pack("bbHHh", ECHO_REQUEST, 0, cs, ID, 1)
    # Includes current timestamp as payload data (8 bytes)
    data = struct.pack("d", time.time())
    cs = checksum(header+data)
    # Convert checksum value from host byte order to network byte order
    cs = socket.htons(cs)
    header = struct.pack("bbHHh", ECHO_REQUEST, 0, cs, ID, 1)
    packet = header + data
    return packet

def get_route(hostname):
    timeLeft = TIMEOUT
    destAddr = socket.gethostbyname(hostname)
    print("Reaching out to "+destAddr)
    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):
            
            # Make a raw socket named mySocket
            icmp = socket.getprotobyname("icmp")
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
            
            # modifying the time to live TTL 
            # SOCK_RAW: Allows direct packet manipulation.
            mySocket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
            # set the timeout to 2 secs
            mySocket.settimeout(TIMEOUT)
            try:
                # construct an ICMP Echo request like a ping and send it to the hostname
                packet = build_packet()
                mySocket.sendto(packet, (hostname, 0))
                t = time.time()
                # Starts a timer and waits for a response using select.select(), which monitors the socket for incoming data.
                # If no response is recieved within timeLeft a timeout occurs.
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                
                # IN CASE: no ICMP response was recieved from the server
                if whatReady[0] == []: 
                    print (" *    *    * Request timed out.")
                
                recvPacket, addr = mySocket.recvfrom(1024)
                print (addr)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                #TIMEOUT: if select operation takes too long.
                if timeLeft <= 0:
                    print (" *    *    * Request timed out.")

            except socket.timeout:
                print (" *    *    * Request timed out.")
                continue

            else:
                icmpHeader = recvPacket[20:28]
                # unpacking icmp header
                request_type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)

                if request_type == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print (" %d try:%d  rtt=%.0fms %s" % (ttl,tries,(timeReceived -t)*1000, addr[0]))
                elif request_type == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print (" %d try:%d  rtt=%.0fms %s" % (ttl,tries,(timeReceived -t)*1000, addr[0]))
                elif request_type == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print (" %d try:%d  rtt=%.0fms %s" % (ttl,tries,(timeReceived -t)*1000, addr[0]))
                    return
                else:
                    print ("error")
                    break
            finally:
                mySocket.close()

get_route('www.dal.ca')