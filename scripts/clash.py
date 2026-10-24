#!/usr/bin/env python3
"""Cubbie Clash client. Talks only to the declared game server over HTTPS.

Privacy: sends percentage, assignment type, difficulty and salted hashes only.
Never sends assignment names, course names or raw Canvas ids.
Standard library only.
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

HOST = "clash-server-one.vercel.app"  # must match network.runtime in cubbie.yaml
BASE = f"https://{HOST}"
TYPES = {"final_exam", "capstone", "test", "quiz", "homework"}


def state_path():
    d = os.environ.get("SKILL_DATA_DIR") or os.path.expanduser("~/.local/share/cubbie-clash")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "player.json")


def load_state():
    try:
        with open(state_path()) as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def save_state(state):
    path = state_path()
    with open(path, "w") as f:
        json.dump(state, f)
    os.chmod(path, 0o600)


def call(path, body, token=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 **({"Authorization": f"Bearer {token}"} if token else {})},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:200]
        sys.exit(f"Server said {e.code}: {msg}")
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach the game server: {e.reason}")


def salted(token, value):
    return hashlib.sha256(f"{token}:{value}".encode()).hexdigest()[:24]


def cmd_optin(a):
    if load_state():
        sys.exit("Already set up. Use 'link' for the game link.")
    res = call("/api/skill/optin", {"name": a.name, "code": a.code})
    save_state({"token": res["token"]})
    print("Set up done.")
    if res.get("new_squad_code"):
        print(f"New squad code: {res['new_squad_code']} (the student shares it with friends)")
    print(res["link"])


def cmd_sync(a):
    st = load_state() or sys.exit("Not set up. Run optin first.")
    with open(a.file) as f:
        items = json.load(f)
    out = []
    for it in items:
        t = it.get("type", "homework")
        out.append({
            "assignment_key": salted(st["token"], it["id"]),
            "course_key": salted(st["token"], it["course_id"]),
            "type": t if t in TYPES else "homework",
            "pct": max(0.0, min(100.0, float(it["pct"]))),
            "difficulty": max(1.0, min(1.5, float(it.get("difficulty", 1.0)))),
        })
    res = call("/api/skill/grades", {"items": out}, st["token"])
    print(f"Points +{res['points']}, Mana +{res['mana']}, Shields +{res.get('shields', 0)}")
    print(res["link"])


def cmd_link(a):
    st = load_state() or sys.exit("Not set up. Run optin first.")
    print(call("/api/skill/link", {}, st["token"])["link"])


def cmd_leave(a):
    st = load_state() or sys.exit("Not set up.")
    call("/api/skill/leave", {}, st["token"])
    os.remove(state_path())
    print("Left Clash. Game data deleted.")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("optin")
    o.add_argument("--name", required=True)
    o.add_argument("--code")
    o.set_defaults(fn=cmd_optin)
    s = sub.add_parser("sync")
    s.add_argument("--file", required=True)
    s.set_defaults(fn=cmd_sync)
    sub.add_parser("link").set_defaults(fn=cmd_link)
    sub.add_parser("leave").set_defaults(fn=cmd_leave)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
