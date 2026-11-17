import enum


class LevelCompletion(enum.IntEnum):
    NOTRECEIVED = 0
    TRYAGAIN = 1
    OK = 2
    SUPERB = 3
    PERFECT = 4