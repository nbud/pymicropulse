import socket
import numpy as np
import pymicropulse as mp

HOST = "10.1.1.2"
PORT = 1067
#%% Status
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
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
    s.sendall(b"STS 20\r")
    data = s.recv(1024)

assert data[0] == mp.Header.UNIV
assert data[1] == 0xF4

temperatures = np.frombuffer(data[2:9:2], dtype=np.uint8)

print(f"System {temperatures[0]}°C")
print(f"Processor {temperatures[1]}°C")

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
    s.sendall(b"ABC\r")
    data = s.recv(1024)

assert data[0] == 0x06


print(mp.parse_error(data))
