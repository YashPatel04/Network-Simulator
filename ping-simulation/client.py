import socket
import time
import sys
import argparse
import array

def ping(host='localhost', port=3000, count=4, timeout=2):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = (host, port)

    client.settimeout(timeout)
    sent, recieved, lost = 0, 0, 0
    rtt = array.array('f')
    try:
        print('Pinging server : '+ server[0]+" "+ str(server[1]))
        # Ping the server count times.
        for i in range(count):
            start = time.time()
            message = "Ping #"+ str(i+1) + " time: " + time.ctime(start)
            try:
                send = client.sendto(message.encode(), server)
                sent+=1
                data, addr = client.recvfrom(4096)
                recieved+=1
                end = time.time()
                print("#"+(str(i+1))+" Reply from "+ str(addr)+": bytes = "+ str(len(data))+", RTT = "+(str(end-start))+"secs")
                rtt.append((end-start))
            except socket.timeout:
                lost+=1
                print("#" + str(i+1) + " Requested Timed out!!")
    except:
        print("An Error Occured")

    finally:
        print("Ping statistics for "+ str(server)+":")
        print("\t Sent = {sent}, Recieved = {recv}, Lost={Lost}({loss}% loss)".format(sent=sent, recv=recieved, Lost=lost, loss = (lost/sent)*100))
        print("Approximate round trip times in milli-seconds:")
        if rtt:  # Only calculate stats if we have RTT values
            print("\tMinimum = {mi:.2f}ms, Maximum = {ma:.2f}ms, Average = {av:.2f}ms".format(mi=min(rtt), ma=max(rtt), av=(sum(rtt)/len(rtt))))
        else:
            print("\tNo RTT data available - all packets were lost")
        client.close()

if __name__ == "__main__":
    # Create simple argument parser
    parser = argparse.ArgumentParser(description="UDP Ping Client")
    parser.add_argument("host", nargs="?", default="localhost", help="Host to ping")
    parser.add_argument("-r", "--count", type=int, default=4, help="Number of packets to send")
    parser.add_argument("-w", "--timeout", type=float, default=2.0, help="Timeout in seconds")
    
    args = parser.parse_args()
    
    try:
        # Run ping with provided arguments
        ping(args.host, 3000, args.count, args.timeout)
    except KeyboardInterrupt:
        print("\nPing terminated by user")
        sys.exit(0)