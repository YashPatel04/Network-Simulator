import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading
import time
import random
import sys

class NetworkingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Simulator")
        self.root.geometry("700x500")
        
        # Server variables
        self.server_running = False
        self.server_socket = None
        self.drop_rate = 30
        
        # Create tabs
        self.tab_control = ttk.Notebook(self.root)
        self.server_tab = ttk.Frame(self.tab_control)
        self.ping_tab = ttk.Frame(self.tab_control)
        self.tracert_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.server_tab, text="Server")
        self.tab_control.add(self.ping_tab, text="Ping")
        self.tab_control.add(self.tracert_tab, text="Traceroute")
        self.tab_control.pack(expand=1, fill="both")
        
        self.setup_server_tab()
        self.setup_ping_tab()
        self.setup_tracert_tab()
    
    def setup_server_tab(self):
        # Simple server controls
        frame = ttk.LabelFrame(self.server_tab, text="Server Controls")
        frame.pack(pady=10, padx=10, fill="both")
        
        ttk.Label(frame, text="Port:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.port_var = tk.StringVar(value="3000")
        ttk.Entry(frame, textvariable=self.port_var, width=10).grid(row=0, column=1, sticky="w")
        
        ttk.Label(frame, text="Drop %:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.drop_rate_var = tk.StringVar(value="30")
        ttk.Entry(frame, textvariable=self.drop_rate_var, width=10).grid(row=1, column=1, sticky="w")
        
        self.server_button = ttk.Button(frame, text="Start Server", command=self.toggle_server)
        self.server_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Log:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.server_log = scrolledtext.ScrolledText(frame, width=60, height=15)
        self.server_log.grid(row=4, column=0, columnspan=2)
        self.server_log.config(state=tk.DISABLED)
    
    def setup_ping_tab(self):
        frame = ttk.LabelFrame(self.ping_tab, text="Ping Tool")
        frame.pack(pady=10, padx=10, fill="both")
        
        ttk.Label(frame, text="Host:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ping_host_var = tk.StringVar(value="localhost")
        ttk.Entry(frame, textvariable=self.ping_host_var, width=20).grid(row=0, column=1, sticky="w")
        
        ttk.Label(frame, text="Port:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ping_port_var = tk.StringVar(value="3000")
        ttk.Entry(frame, textvariable=self.ping_port_var, width=10).grid(row=1, column=1, sticky="w")
        
        ttk.Label(frame, text="Count:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.ping_count_var = tk.StringVar(value="4")
        ttk.Entry(frame, textvariable=self.ping_count_var, width=10).grid(row=2, column=1, sticky="w")
        
        ttk.Button(frame, text="Start Ping", command=self.start_ping).grid(row=3, column=0, columnspan=2, pady=10)
        
        self.ping_output = scrolledtext.ScrolledText(frame, width=60, height=12)
        self.ping_output.grid(row=4, column=0, columnspan=2)
        self.ping_output.config(state=tk.DISABLED)
    
    def setup_tracert_tab(self):
        frame = ttk.LabelFrame(self.tracert_tab, text="Traceroute Tool")
        frame.pack(pady=10, padx=10, fill="both")
        
        ttk.Label(frame, text="Host:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.tracert_host_var = tk.StringVar(value="localhost")
        ttk.Entry(frame, textvariable=self.tracert_host_var, width=20).grid(row=0, column=1, sticky="w")
        
        ttk.Label(frame, text="Port:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.tracert_port_var = tk.StringVar(value="3000")
        ttk.Entry(frame, textvariable=self.tracert_port_var, width=10).grid(row=1, column=1, sticky="w")
        
        ttk.Label(frame, text="Max Hops:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.tracert_hops_var = tk.StringVar(value="10")
        ttk.Entry(frame, textvariable=self.tracert_hops_var, width=10).grid(row=2, column=1, sticky="w")
        
        ttk.Button(frame, text="Start Traceroute", command=self.start_tracert).grid(row=3, column=0, columnspan=2, pady=10)
        
        self.tracert_output = scrolledtext.ScrolledText(frame, width=60, height=12)
        self.tracert_output.grid(row=4, column=0, columnspan=2)
        self.tracert_output.config(state=tk.DISABLED)
    
    def toggle_server(self):
        if not self.server_running:
            try:
                port = int(self.port_var.get())
                drop_rate = int(self.drop_rate_var.get())
                self.drop_rate = drop_rate
                
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.server_socket.bind(('127.0.0.1', port))
                self.server_socket.settimeout(0.5)
                
                self.server_button.config(text="Stop Server")
                self.log_to_server(f"Server started on port {port} with {drop_rate}% packet loss")
                
                self.server_running = True
                threading.Thread(target=self.run_server, daemon=True).start()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            self.server_running = False
            if self.server_socket:
                self.server_socket.close()
            self.server_button.config(text="Start Server")
            self.log_to_server("Server stopped")
    
    def run_server(self):
        while self.server_running:
            try:
                data, addr = self.server_socket.recvfrom(4096)
                
                # Drop packets randomly
                if random.randint(1, 100) <= self.drop_rate:
                    self.log_to_server(f"Dropped packet from {addr}")
                    continue
                
                message = data.decode()
                self.log_to_server(f"Got: {message} from {addr}")
                
                # Handle ping
                if message.startswith("PING"):
                    seq = message.split(':')[1]
                    reply = f"PONG:{seq}"
                    time.sleep(random.uniform(0.01, 0.1))  # Random delay
                    self.server_socket.sendto(reply.encode(), addr)
                
                # Handle traceroute
                elif message.startswith("TTL"):
                    ttl = int(message.split(':')[1].strip())
                    reply = f"RESPONSE: {ttl}"
                    time.sleep(random.uniform(0.01, 0.3))  # Random delay
                    self.server_socket.sendto(reply.encode(), addr)
                    
            except socket.timeout:
                pass
            except Exception as e:
                if self.server_running:
                    self.log_to_server(f"Error: {e}")
    
    def start_ping(self):
        self.ping_output.config(state=tk.NORMAL)
        self.ping_output.delete(1.0, tk.END)
        self.ping_output.config(state=tk.DISABLED)
        
        host = self.ping_host_var.get()
        port = int(self.ping_port_var.get())
        count = int(self.ping_count_var.get())
        
        threading.Thread(target=self.run_ping, args=(host, port, count), daemon=True).start()
    
    def run_ping(self, host, port, count):
        self.log_to_ping(f"Pinging {host}:{port} with {count} packets:")
        
        try:
            dest_ip = socket.gethostbyname(host)
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.settimeout(2.0)
            
            sent, received = 0, 0
            rtts = []
            
            for i in range(count):
                sent += 1
                seq = i + 1
                
                try:
                    start = time.time()
                    client.sendto(f"PING:{seq}".encode(), (dest_ip, port))
                    data, _ = client.recvfrom(4096)
                    rtt = (time.time() - start) * 1000
                    rtts.append(rtt)
                    received += 1
                    self.log_to_ping(f"Reply from {dest_ip}: seq={seq} time={rtt:.1f}ms")
                except socket.timeout:
                    self.log_to_ping(f"Request timed out for seq={seq}")
                
                if i < count - 1:
                    time.sleep(1)
            
            # Show stats
            loss = ((sent - received) / sent) * 100
            self.log_to_ping(f"\nSent={sent}, Received={received}, Lost={sent-received} ({loss:.1f}% loss)")
            
            if rtts:
                self.log_to_ping(f"Min={min(rtts):.1f}ms, Max={max(rtts):.1f}ms, Avg={sum(rtts)/len(rtts):.1f}ms")
                
            client.close()
            
        except Exception as e:
            self.log_to_ping(f"Error: {str(e)}")
    
    def start_tracert(self):
        self.tracert_output.config(state=tk.NORMAL)
        self.tracert_output.delete(1.0, tk.END)
        self.tracert_output.config(state=tk.DISABLED)
        
        host = self.tracert_host_var.get()
        port = int(self.tracert_port_var.get())
        max_hops = int(self.tracert_hops_var.get())
        
        threading.Thread(target=self.run_tracert, args=(host, port, max_hops), daemon=True).start()
    
    def run_tracert(self, host, port, max_hops):
        self.log_to_tracert(f"Tracing route to {host}:{port} (max {max_hops} hops):")
        self.log_to_tracert("-" * 40)
        self.log_to_tracert("HOP    HOST           RTT1    RTT2")
        
        try:
            dest_ip = socket.gethostbyname(host)
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.settimeout(2.0)
            
            for i in range(max_hops):
                rtts = ["*", "*"]
                timeout = False
                
                for j in range(2):  # Two tries per hop
                    try:
                        msg = f"TTL:{i}"
                        client.sendto(msg.encode(), (dest_ip, port))
                        
                        start = time.time()
                        data, _ = client.recvfrom(4096)
                        rtt = (time.time() - start) * 1000
                        
                        response = data.decode()
                        ttl = int(response.split(':')[1].strip())
                        if ttl == i:
                            rtts[j] = f"{rtt:.1f}ms"
                            
                    except socket.timeout:
                        timeout = True
                
                hop = i + 1
                if timeout and all(r == "*" for r in rtts):
                    self.log_to_tracert(f"{hop:<5} Timed Out      *       *")
                else:
                    self.log_to_tracert(f"{hop:<5} {dest_ip}  {rtts[0]}    {rtts[1]}")
            
            client.close()
            
        except Exception as e:
            self.log_to_tracert(f"Error: {str(e)}")
    
    def log_to_server(self, msg):
        self.server_log.config(state=tk.NORMAL)
        self.server_log.insert(tk.END, f"{msg}\n")
        self.server_log.see(tk.END)
        self.server_log.config(state=tk.DISABLED)
    
    def log_to_ping(self, msg):
        self.ping_output.config(state=tk.NORMAL)
        self.ping_output.insert(tk.END, f"{msg}\n")
        self.ping_output.see(tk.END)
        self.ping_output.config(state=tk.DISABLED)
    
    def log_to_tracert(self, msg):
        self.tracert_output.config(state=tk.NORMAL)
        self.tracert_output.insert(tk.END, f"{msg}\n")
        self.tracert_output.see(tk.END)
        self.tracert_output.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkingTool(root)
    root.mainloop()