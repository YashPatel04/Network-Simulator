import random
import time
from socket import *
# Create a UDP socet
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', 3000))
while True:
    rand = random.randint(0, 10)
    rand2 = random.randint(40,100)
    message, address = serverSocket.recvfrom(1024)
    message = message.upper()
    if rand < 4:
        continue
    time.sleep(rand2/1000)
    serverSocket.sendto(message, address)

