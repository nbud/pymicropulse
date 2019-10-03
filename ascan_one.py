"""
Acquire one Ascan with a Peakndt Micropulse ultrasound acquisition system and
plot it

Single channel transmitting, single channel receiving (possibly different)

Known issue: CAL 1 returns a EHT supply error. CAL 0 works
"""
import socket
import numpy as np
import pymicropulse as mp
import matplotlib.pyplot as plt

HOST = "10.1.1.2"
PORT = 1067
TIMEOUT = 5

#%% Reset at desired sampling rate
# Valid: 10, 25, 40, 50, 80, 100
# See p 126

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"RST 50\r")
    data = s.recv(1024)
    sampling_rate = mp.parse_rst(data)["sampling_rate"]
    print(f"Sampling rate: {sampling_rate} MHz")

#%% Define test and acquire one Ascan
# TXN: p 154

test_idx = 1
tx_channel_idx = 1
rx_channel_idx = 1
gain = 80  # dB
_gain_param = round(gain / 4)

# in time points
gate_start = 300
gate_end = 3000

numaverages = 16
_numaverages = int(np.log2(numaverages))

# pulser width in nanosecond
# 10 to 502 ns by 2 ns
pulser_width = 100

# 25-200 V by 25 Volt
pulser_voltage = 100

# see p 121.
# 0 to 7
damping_mode = 0

# Pulse repetition rate
# 1 Hz to 20 kHz by 1 Hz
prf = 1000

waveform_mode = 1  # full waveform
amp_mode = 3  # full ascan

# 1 to 12:
filter_idx = 5
# 1 to 11:
filter_smoothing = 1

# data output mode
# Note that the ADC supports 12 bits max
dof = 1  # 8 bits
dof = 2  # 10 bits
dof = 3  # 12 bits
dof = 4  # 16 bits

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.settimeout(TIMEOUT)
    cmd = f"""
DOF {dof}
DLY {test_idx} 0
NUM 1
TXN {test_idx} {tx_channel_idx}
RXN {test_idx} {rx_channel_idx}
GAN {test_idx} {_gain_param}
GAT {test_idx} {gate_start} {gate_end}
AWF {test_idx} {waveform_mode}
AMP {test_idx} {amp_mode} {_numaverages}
PDW {tx_channel_idx} {damping_mode} {pulser_width}
PSV {tx_channel_idx} {pulser_voltage}
FRQ {test_idx}  {filter_idx} {filter_smoothing}
PRF {prf}
ETM {test_idx} 0
    """
    print(cmd)
    mp.send_str_cmd(s, cmd)
    mp.assert_no_error(s)

    # mp.send_str_cmd(s, "TXF")
    mp.assert_no_error(s)

    # Do acquisition
    # mp.send_str_cmd(s, "CAL {test_idx}") # EHT supply error?
    mp.send_str_cmd(s, "CAL 0")
    header_length = 8
    data_header = s.recv(header_length)
    if data_header[0] != mp.Header.ASCAN:
        raise mp.MicropulseError(mp.parse_error(data))
    # Length of data in bytes (remove 8 bytes for already read header):
    datacount = (
        data_header[1]
        + data_header[2] * 2 ** 8
        + data_header[3] * 2 ** 16
        - header_length
    )
    data_plus_suffix = b""
    while len(data_plus_suffix) < (datacount + 2):
        data_plus_suffix += s.recv(4096)
    data = data_plus_suffix[:datacount]
    # A CAL 0 ends with 0x01 0x01 (see p 45)
    suffix = data_plus_suffix[datacount:]
    assert suffix[0] == suffix[1] == mp.Header.CAL_ZERO_END
    if len(suffix) > 2:
        print(f"Unexpected trailing data: {suffix}")
    print("Ascan received")


#%% Parse Ascan
dof = data_header[6]
if dof == 1:
    dtype = np.uint8
    bits_per_sample = 8
elif dof in (2, 3, 4):
    # 10, 12 or 16 bit output, padded with zeros on LSB if necessary
    dtype = np.uint16
    bits_per_sample = 16
else:
    raise ValueError("unsupported dof")

timetrace = np.frombuffer(data, dtype)
# convert to ]-1, 1] float
timetrace2 = timetrace.astype(np.float_) * 2 / 2 ** bits_per_sample - 1

#%% Plot Ascan
t = np.arange(gate_start, gate_end) / sampling_rate
plt.figure()
plt.step(t, timetrace2)
plt.xlabel("time (µs)")
# plt.ylim([-1, 1])
