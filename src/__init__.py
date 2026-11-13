import os
import re
import sys


def parser(filepath: str):
    if not os.path.exists(filepath):
        print(f"[ERROR] file does not exist: {filepath}")
        sys.exit(1)

    pattern = re.compile(r"^\[([0-9]{2}:[0-9]{2}:[0-9]{2})] \[(.+?)/(.+?)]: ?(.*)$")

    logs = []

    with open(filepath, "rt", encoding="utf-8") as f:
        info = {}
        messageList = []
        rawList = []

        for line in f:
            line = line.rstrip()
            print(line)

            result = pattern.match(line)
            if result is None:
                # not matched
                messageList.append(line)
                rawList.append(line)
                continue

            # matched
            if len(messageList) == 0:
                # No previous match (first line)
                info = {
                    "time": result.group(1),
                    "threadName": result.group(2),
                    "level": result.group(3),
                }
                messageList.append(result.group(4))
                rawList.append(line)
                continue

            info.update(
                {"messages": "\n".join(messageList), "raws": "\n".join(rawList)}
            )
            logs.append(info)

            info = {
                "time": result.group(1),
                "threadName": result.group(2),
                "level": result.group(3),
            }
            messageList = [result.group(4)]
            rawList = [line]

        if info:
            info.update(
                {"messages": "\n".join(messageList), "raws": "\n".join(rawList)}
            )
            logs.append(info)

    return logs
