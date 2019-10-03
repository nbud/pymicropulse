%% acquire in MATLAB an ascan with a peakndt micropulse acquisition system and plot it

%% clear all
clear all
clc
%%

%Micropulse connection details
ip_address = '10.1.1.2';
port_no = 1067;
timeout = 3; %seconds
sock = tcpclient(ip_address, port_no, 'Timeout', timeout);

%% Params
sampling_freq_mhz = 50;
test_idx = 1;
tx_channel_idx = 1;
rx_channel_idx = 1;

%in time points
gate_start = 300;
gate_end = 3000;

gain = 80; % in dB
gain_param = round(gain / 4);

numaverages = 16;
numaverages_param = round(log2(numaverages));

% pulser width in nanosecond
% 10 to 502 ns by 2 ns
pulser_width = 100;

% 25-200 V by 25 Volt
pulser_voltage = 100;

% see p 121.
% 0 to 7
damping_mode = 0;

% Pulse repetition rate
% 1 Hz to 20 kHz by 1 Hz
prf = 1000;

waveform_mode = 1;  % full waveform
amp_mode = 3;  % full ascan

% 1 to 12:
filter_idx = 5;
% 1 to 11:
filter_smoothing = 1;

%%
cmd = sprintf('RST %d\r', sampling_freq_mhz);
write(sock, uint8(cmd));
rst_reply = read(sock, 32, 'uint8');
assert(rst_reply(1) == 35)
%%
cmd = sprintf('DOF 1\r');
write(sock, uint8(cmd));

cmd = sprintf('NUM %d\r', test_idx);
write(sock, uint8(cmd));

cmd = sprintf('TXN %d %d\r', test_idx, tx_channel_idx);
write(sock, uint8(cmd));

cmd = sprintf('RXN %d %d\r', test_idx, rx_channel_idx);
write(sock, uint8(cmd));

cmd = sprintf('GAN %d %d\r', test_idx, gain_param);
write(sock, uint8(cmd));

cmd = sprintf('GAT %d %d %d\r', test_idx, gate_start, gate_end);
write(sock, uint8(cmd));

cmd = sprintf('AWF %d %d\r', test_idx, waveform_mode);
write(sock, uint8(cmd));

cmd = sprintf('AMP %d %d %d\r', test_idx, amp_mode, numaverages_param);
write(sock, uint8(cmd));

cmd = sprintf('PDW %d %d %d\r', tx_channel_idx, damping_mode, pulser_width);
write(sock, uint8(cmd));

cmd = sprintf('PSV %d %d\r', tx_channel_idx, pulser_voltage);
write(sock, uint8(cmd));

cmd = sprintf('FRQ %d %d %d\r', test_idx, filter_idx, filter_smoothing);
write(sock, uint8(cmd));

cmd = sprintf('PRF %d\r', prf);
write(sock, uint8(cmd));

cmd = sprintf('ETM %d 0\r', test_idx);
write(sock, uint8(cmd));

%%
datasize = gate_end - gate_start + 8;
cmd = sprintf('CAL %d\r', test_idx);
write(sock, uint8(cmd));
reply = read(sock, datasize, 'uint8');
timetrace = reply(9:datasize);
%%
timevect = (gate_start:(gate_end - 1)) / sampling_freq_mhz;
figure();
plot(timevect, timetrace);
xlabel('time (µs)')
