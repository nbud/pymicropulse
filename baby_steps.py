import socket
import numpy as np

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

import pymicropulse as mp

print(mp.parse_error(data))
