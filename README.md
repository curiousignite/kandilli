# Kandilli

A quick script to get notified whenever there is an earthquake near Türkiye.

## Quickstart

For default, script is set to only notify for earthquakes greater than 4.5 ML
You can change this behaviour by changing the code below

```python
THRESHOLD: float = 4.5
```

Script sends a POST request at <https://ntfy.sh/kandilli>.
You can change this behaviour by changing the code below

```python
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}
requests.post("http://ntfy.sh/kandilli", headers=headers, data=data)
```

> [!NOTE]
> Errors will be logged at <https://ntfy.sh/kandilli_log>

## TODO

- [x] Use systemd services maybe?
- [ ] Redirect errors and logs to a different URL
- [ ] Save logs to a file
