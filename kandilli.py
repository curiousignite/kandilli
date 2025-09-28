#!/usr/bin/env python3

import re
from datetime import datetime, timedelta
from itertools import islice
from time import sleep
import os
import platform
import requests

DEBUG_FLAG: bool = True  # NOTE: FOR DEVELEOPMENT ONLY CHANGE TO `False` BEFORE USING
KANDILLI_WEBSITE: str = "http://www.koeri.boun.edu.tr/scripts/lst0.asp"
INITIAL_PATTERN = r"<pre>.*</pre>"
MAIN_PATTERN = r"""^(\d{4}\.\d{2}\.\d{2})\s*(\d{2}:\d{2}:\d{2})
                    \s*\d{2}\.\d{4}\s*\d{2}\.\d{4}\s*\d{1,2}\.\d{1,2}\s*
                    (-\.-|\d*\.\d*)\s*(-\.-|\d*\.\d*)\s*(-\.-|\d*\.\d*)
                    \s*(\S*\s\S*|\S)"""
REQUEST_HEADER = {
    "Content-Type": "application/x-www-form-urlencoded",
}
NTFY_HEADER = {"Tags": "warning"}

THRESHOLD: float
HOUR_OFFSET: int
MINUTE_OFFSET: int
SLEEP_INTERVAL: int
TOTAL_SECONDS: int
NTFY_KANDILLI: str
NTFY_LOG: str

if DEBUG_FLAG:
    THRESHOLD = 0.0
    HOUR_OFFSET = 0
    MINUTE_OFFSET = 30
    SLEEP_INTERVAL = 60  # Lower at your own risk, you can be banned from the site
    NTFY_KANDILLI = "http://100.88.78.22:1111/kandilli_debug"
    NTFY_LOG = "http://100.88.78.22:1111/kandilli_log_debug"
else:
    THRESHOLD = 4.0
    HOUR_OFFSET = 0
    MINUTE_OFFSET = 15
    SLEEP_INTERVAL = 5  # Lower at your own risk, you can be banned from the site
    NTFY_KANDILLI = "http://100.88.78.22:1111/kandilli"
    NTFY_LOG = "http://100.88.78.22:1111/kandilli_log"

TOTAL_SECONDS = (HOUR_OFFSET * 60 + MINUTE_OFFSET) * 60


def get_html(error_counter: int) -> str:
    try:
        r = requests.get(KANDILLI_WEBSITE)
    except requests.exceptions.Timeout:
        data = "Timeout exception occurred."
        append_log("ERROR", data)
        sleep(SLEEP_INTERVAL * error_counter)
        return "error"
    except requests.exceptions.TooManyRedirects:
        data = "Too many redirects"
        append_log("ERROR", data)
        sleep(SLEEP_INTERVAL * error_counter)
        return "error"
    except requests.exceptions.ConnectionError:
        data = "Connection Error occurred"
        append_log("ERROR", data)
        sleep(SLEEP_INTERVAL * error_counter)
        return "error"
    except requests.exceptions.RequestException as e:
        data = "Fatal Error"
        append_log("ERROR", data)
        raise SystemExit(e)
    return r.text


def parser(html_text: str):
    now = datetime.now()
    found = False
    offset_time = now - timedelta(hours=+HOUR_OFFSET, minutes=+MINUTE_OFFSET)
    between_pre = re.findall(
        INITIAL_PATTERN, html_text, flags=re.MULTILINE | re.DOTALL
    )[0]
    tokens: list[str] = between_pre.split("\n")
    tokens_len = len(tokens)
    data_lines = islice(tokens, 7, tokens_len - 3)  # Data lines start at 7
    for line in data_lines:
        match = re.findall(MAIN_PATTERN, line, flags=re.VERBOSE | re.MULTILINE)
        for group in match:
            if (
                float(group[3]) >= THRESHOLD
                and group[0] >= offset_time.strftime("%Y.%m.%d")
                and group[1] >= offset_time.strftime("%H:%M:%S")
            ):
                data = f"Saat {group[1]}'de {group[5]} bölgesinde {group[3]} büyüklüğünde bir deprem oldu!"
                found = True
                append_log("INFO", data, priority="urgent")
    if found:
        append_log(
            "LOG",
            f"Found, waiting for {str(TOTAL_SECONDS)} seconds",
        )
        sleep(TOTAL_SECONDS)
        found = False
    else:
        if DEBUG_FLAG:
            append_log(
                "LOG", f"Nothing found, trying again in {SLEEP_INTERVAL} seconds"
            )
        sleep(SLEEP_INTERVAL)


def append_log(type: str, data: str, priority: str = "default") -> None:
    write_log(type, data)
    send_request(type, data, priority)


def send_request(type: str, data: str, priority: str) -> None:
    NTFY_HEADER.update({"X-Priority": priority})
    try:
        if type == "INFO":
            NTFY_HEADER.update({"Title": "Deprem"})
            requests.post(NTFY_KANDILLI, headers=NTFY_HEADER, data=data)
        else:
            NTFY_HEADER.update({"Title": "DEBUG"})
            requests.post(NTFY_LOG, headers=NTFY_HEADER, data=data)
    except requests.exceptions.RequestException as e:
        write_log("ERROR", str(e))


def write_log(type, data) -> None:
    # TODO:Check for other iOS and BSD later
    if platform.system() == "Linux":
        log_path = os.path.expanduser("~/.local/state/kandilli.log")
    elif platform.system() == "Windows":
        log_path = os.path.expanduser("%AppData%\\kandilli.log")

    print(datetime.now().strftime("%d.%m.%Y (%H:%M:%S)"), end="")
    print(" | ", end="")
    print(f"[{type}]: ", end="")
    print(data, end="")
    print("\n", end="")
    try:
        file = open(log_path, "a")
        file.write(datetime.now().strftime("%d.%m.%Y (%H:%M:%S)"))
        file.write(" | ")
        file.write(f"[{type}]: ")
        file.write(data)
        file.write("\n")
        file.close()
    except FileNotFoundError as e:
        print(e)


def main():
    error_counter = 1
    append_log("LOG", "Program started")
    while True:
        html_text: str = get_html(error_counter)
        if html_text == "error":
            error_counter += 1
            continue
        else:
            parser(html_text)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        data = "Keyboard Interrupt"
        append_log("LOG", data)
    finally:
        append_log("LOG", "Program terminated")
