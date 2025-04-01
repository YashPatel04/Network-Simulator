import socket
import time
import sys


def traceroute(dest ,host='localhost', port=3000, max_hops=30):
    dest_ip = socket.gethostbyname(dest)
    dest_addr = (dest_ip, port)

    print("Tracing route to {d}  over a maximum of {m} hops:\n".format(d=dest_addr, m=max_hops))
    tries = 2
    # UDP socket
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # set timeout to 2 secs
    client.settimeout(2.0)
    print("------------------------------------------------")
    print("RESP    HOSTNAME        #1    #2")
    for i in range(0, max_hops, 1):
        rtts = ["*   "] * tries
        timeout = False
        for j in range(tries):
                try:
                    message = "TTL: {}".format(i)
                    client.sendto(message.encode(), dest_addr)
                    t = time.time()
                    data, _ = client.recvfrom(4096)
                    rtt = time.time() - t
                    message = data.decode()
                    ttl = int(message.split(':')[1])
                    if ttl == i:
                        rtts[j] = f"{int(rtt*1000)}ms"
                except socket.timeout:
                    timeout = True
        if timeout and all(rtt == "*   " for rtt in rtts):
            print(f"{i+1}   Request Timed Out    *   *")
        else:
            print(f"{i+1}    {dest_ip}:{port}    {rtts[0]}   {rtts[1]}")

    client.close()
if __name__ == "__main__":
    try:
        dest = 'localhost'
        traceroute(dest)
    except KeyboardInterrupt:
        print("Terminating Operation!")
        sys.exit(0)