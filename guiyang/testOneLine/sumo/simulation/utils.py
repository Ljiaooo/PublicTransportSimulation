from datetime import datetime


def seconds2datetime(t):
    hour = t % 3600
    minute = t % 60
    second = t - hour * 3600
    return datetime(2022, 8, 1, hour=hour, minute=minute, second=second)

def str2seconds(s):
    splits = s.split(':')
    hour = int(splits[0])
    minute = int(splits[1])
    second = int(splits[2])
    total_seconds = hour * 3600 + minute * 60 + second
    return total_seconds

def seconds2str(t):
    hour = t // 3600
    minute = (t - hour * 3600) // 60
    second = t % 60
    return '{:02d}:{:02d}:{:02d}'.format(hour, minute, second)
