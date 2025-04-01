import socket
import time
import random
import sys

# Init UDP server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.settimeout(1.0)
def runserver():
    while True:
        try:
            rand = random.randint(1,10)
            data, addr = server.recvfrom(4096)
            if(rand<4):
                continue
            # if not data:
            #     print(rand)
            # decode the data and send the ttl
            message = data.decode('utf-8')
            ttl = int(message.split(':')[1])

            # introduce artificaital delay to make it seem real
            time.sleep(random.uniform(10,20)/1000)

            reply = "RESPONSE: {ttl}".format(ttl=ttl)
            server.sendto(reply.encode('utf-8'), addr)
        except socket.timeout:

            continue

if __name__=="__main__":
    # server bound to local host 3000
    server.bind(('127.0.0.1', 3000))
    print("Traceroute Simulator listening on localhost 3000...")
    try:
        runserver()
    except KeyboardInterrupt:
        server.close()
        sys.exit(0)

    
