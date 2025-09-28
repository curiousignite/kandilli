# Kandilli

A quick script to get notified whenever there is an earthquake near Türkiye.

## Quickstart

For default, script is set to only notify for earthquakes greater than 4.5 ML
You can change this behaviour by changing the code below

```python
THRESHOLD: float = 4.0
```

Script sends a POST request at <http://100.88.78.22:1111/kandilli>.
You can change this behaviour by changing the code below

```python
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}
requests.post("http://100.88.78.22:1111/kandilli", headers=headers, data=data)
```

> [!NOTE]
> Errors will be logged at <http://100.88.78.22:1111/kandilli>
> Also at ~/.local/state/kandilli.log
> [!WARNING]
> This addresses are my local tailscale addresses so they won't work for you.

## TODO

- [x] Redirect errors and logs to a different URL
- [x] Save logs to a file
- [ ] Use systemd services maybe?
- [ ] Add other sources like AFAD or Google
