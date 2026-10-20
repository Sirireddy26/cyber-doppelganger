import urllib.request
import json

def test():
    data = json.dumps({"authorized_by": "SecOps Admin", "reason": "Administrative system reset"}).encode()
    req = urllib.request.Request("http://localhost:8080/api/adaptation/unfreeze", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            print("Status:", resp.status)
            print(resp.read().decode())
    except urllib.error.HTTPError as e:
        print("HTTPError:", e.code, e.read().decode())

if __name__ == "__main__":
    test()
