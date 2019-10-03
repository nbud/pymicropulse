"""
Helpers function for a PeakNDT Micropulse acquisition system

Reference: command reference 2018
"""
import enum
import contextlib


class MicropulseError(Exception):
    pass


class NotAnError(ValueError):
    pass


@enum.unique
class Header(enum.IntEnum):
    ERROR = 0x6
    STA = 0x15
    ASCAN = 0x1A


@enum.unique
class Error(enum.IntEnum):
    ARG_CONFLICT = 0
    UNRECOGNISED_CMD = 1
    ARG_OUTSIDE_LIMITS = 2
    UNRECOGNISED_CMD_BIS = 3
    OVER_TEMPERATURE = 4
    EHT_SUPPLY_ERROR = 5
    SLAVE_SYSTEM_ERROR = 6
    PARALLEL_CHANNEL_ERROR = 7
    CONVENTIONAL_CHANNEL_ERROR = 8


def parse_error(data):
    if data[0] != Header.ERROR:
        raise NotAnError(f"Data: {data}")
    return Error(data[1])


def parse_rst(data):
    # p 24
    if data[0] != 0x23:
        raise ValueError

    return {"sampling_rate": data[9], "data_output_mode": data[7]}


@contextlib.contextmanager
def set_timeout_and_rollback(sock, timeout):
    previous_timeout = sock.gettimeout()
    sock.settimeout(timeout)
    try:
        yield None
    finally:
        sock.settimeout(previous_timeout)


@contextlib.contextmanager
def set_nonblocking_and_rollback(sock):
    previous_timeout = sock.gettimeout()
    sock.setblocking(False)
    try:
        yield None
    finally:
        sock.settimeout(previous_timeout)


def discard_reply(sock):
    """
    Silently discard any message from the Acq System 
    """
    with set_nonblocking_and_rollback(sock):
        try:
            while True:
                data = sock.recv(1024)
        except BlockingIOError:
            # no available data
            pass


def assert_no_error(sock, timeout=0.1):
    """
    Raises an exception if the Acq System sent any message (possibly an error)
    """
    with set_timeout_and_rollback(sock, timeout):
        try:
            data = sock.recv(1024)
        except BlockingIOError:
            # no available data
            pass
        else:
            raise MicropulseError(parse_error(data))


def block_until_ready(sock, timeout=3):
    """
    ensure the device is ready by asking its status and waiting for reply
    """
    sock.sendall(b"STA\r")
    with set_timeout_and_rollback(sock, timeout):
        data = sock.recv(1024)
    try:
        raise MicropulseError(parse_error(data))
    except NotAnError:
        pass
    if not (data[0] == Header.STA and len(data) == 18):
        raise RuntimeError(f"Unexpected reply: {data}")


def send_str_cmd(sock, cmd_str):
    """send one or multiple string commands separated by \n"""
    cmd = cmd_str.encode("ascii")
    cmd = cmd.replace(b"\n", b"\r")
    cmd += b"\r"
    return sock.sendall(cmd)
