import requests


def call_api():
    headers = {"Content-Type": "application/json; charset=utf-8", "x-access-token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImRhbi52ZWpzYWRhQGdtYWlsLmNvbSIsImlkIjoxMjE5LCJuYW1lIjpudWxsLCJzdXJuYW1lIjpudWxsLCJpYXQiOjE2NDk1ODgzMzMsImV4cCI6MTE2NDk1ODgzMzMsImlzcyI6ImdvbGVtaW8iLCJqdGkiOiJmYzg4NmRlZS0xY2MyLTQyZDktYjFhNS0yNDNjZDdhMTAxOWUifQ.2Qkq-qt0jDMkO14UcpVVTRc8sb5qqRo4O_mV_dBTw9U"}
    parameters = {"ids": "U4572Z1P", "total": 1}
    api_url = "https://api.golemio.cz/v2/pid/departureboards/"
    response = requests.get(api_url, params=parameters, headers=headers)
    reply = response.json()
    return reply["departures"][0]["departure_timestamp"]["minutes"]



