import enum


@enum.unique
class Header(enum.IntEnum):
    ERROR = 0x6


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


def parse_error(msg):
    if msg[0] != Header.ERROR:
        raise ValueError
    return Error(msg[1])
