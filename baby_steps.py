import socket
import numpy as np
import pymicropulse as mp

HOST = "10.1.1.2"
PORT = 1067
TIMEOUT = 1
#%% Status
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.settimeout(TIMEOUT)
    s.sendall(b"STA\r")
    data = s.recv(1024)

print("Received", repr(data))
arr = np.frombuffer(data, np.uint8)
assert data[0] == 0x15
assert arr[0] == 0x15

#%% Temperature
# see p 145

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.settimeout(TIMEOUT)
    s.sendall(b"STS 20\r")
    data = s.recv(1024)

assert data[0] == 0x15
assert data[1] == 0xF4

temperatures = np.frombuffer(data[2:9:2], dtype=np.uint8)

print(f"System {temperatures[0]}°C")
print(f"Processor {temperatures[1]}°C")


#%% System information
# p 24

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.settimeout(TIMEOUT)
    s.sendall(b"STS -1\r")
    data = s.recv(1024)

assert data[0] == 0x23
print(f"Default sample freq {data[8]} MHz")
print(f"Actual sample freq {data[9]} MHz")

print(mp.parse_rst(data))

#%%
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.settimeout(0)
    try:
        data = s.recv(1024)
    except BlockingIOError:
        print("No available data")

#%%

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.settimeout(TIMEOUT)
    s.sendall(b"ABC\r")
    data = s.recv(1024)

assert data[0] == 0x06


print(mp.parse_error(data))
