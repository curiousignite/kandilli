#!/usr/bin/env python3

from datetime import datetime, timedelta
from time import sleep
import requests
import re
from itertools import islice


def main():
    THRESHOLD: float = 4.5
    HOUR_OFFSET: int = 0
    MINUTE_OFFSET: int = 15
    SLEEP_INTERVAL: int = 10
    INITIAL_PATTERN = r"<pre>.*</pre>"
    MAIN_PATTERN = r"""^(\d{4}\.\d{2}\.\d{2})\s*(\d{2}:\d{2}:\d{2})
                        \s*\d{2}\.\d{4}\s*\d{2}\.\d{4}\s*\d{1,2}\.\d{1,2}\s*
                        (-\.-|\d*\.\d*)\s*(-\.-|\d*\.\d*)\s*(-\.-|\d*\.\d*)
                        \s*(\S*\s\S*|\S)"""

    HOUR_OFFSET += MINUTE_OFFSET // 60
    MINUTE_OFFSET = MINUTE_OFFSET % 60

    now = datetime.now()
    found = False
    offset_time = now - timedelta(hours=+HOUR_OFFSET, minutes=+MINUTE_OFFSET)

    while True:
        try:
            r = requests.get("http://www.koeri.boun.edu.tr/scripts/lst0.asp")
        except requests.exceptions.Timeout:
            print("Timeout exception occured")
            sleep(10)
            continue
        except requests.exceptions.TooManyRedirects:
            print("Too many redirects")
            sleep(10)
            continue
        except requests.exceptions.ConnectionError:
            print("Too many redirects")
            sleep(10)
            continue
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        html_text = r.text
        between_pre = re.findall(
            INITIAL_PATTERN, html_text, flags=re.MULTILINE | re.DOTALL
        )[0]
        tokens: list[str] = between_pre.split("\n")
        tokens_len = len(tokens)
        data_lines = islice(tokens, 7, tokens_len - 3)
        for line in data_lines:
            match = re.findall(MAIN_PATTERN, line, flags=re.VERBOSE | re.MULTILINE)
            for group in match:
                if (
                    float(group[3]) >= THRESHOLD
                    and group[0] >= offset_time.strftime("%Y.%m.%d")
                    and group[1] >= offset_time.strftime("%H:%M:%S")
                ):
                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded",
                    }
                    data = f"Saat {group[1]}'de {group[5]} bölgesinde {group[3]} büyüklüğünde bir deprem oldu!"
                    requests.post("http://ntfy.sh/kandilli", headers=headers, data=data)
                    found = True
        if found:
            print(found)
            sleep(MINUTE_OFFSET * HOUR_OFFSET * 60)
            found = False
        else:
            sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExited")
