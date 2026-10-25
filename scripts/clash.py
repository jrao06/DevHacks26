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


class ServerError(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code
        self.msg = msg


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
        raise ServerError(e.code, e.read().decode()[:200])
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


def battles_line(res):
    """One line about waiting challenges and turns, so Cubbie can mention it in the student's text."""
    b = res.get("battles") or {}
    bits = []
    if b.get("invites"):
        bits.append(f"{b['invites']} challenge(s) waiting")
    if b.get("your_turn"):
        bits.append(f"{b['your_turn']} battle(s) where it is the student's turn")
    if bits:
        print("Battles: " + ", ".join(bits))


def cmd_sync(a):
    st = load_state() or sys.exit("Not set up. Run optin first.")
    with open(a.file) as f:
        items = json.load(f)
    out = []
    for it in items:
        t = it.get("type", "homework")
        # Canvas may not give an assignment id. Fall back to the name.
        # Both are hashed here and never leave this machine.
        ident = it.get("id") or it.get("name")
        if not ident or it.get("course_id") is None:
            continue
        if "pct" in it:
            pct = float(it["pct"])
        elif it.get("points_possible"):
            pct = 100.0 * float(it["points_earned"]) / float(it["points_possible"])
        else:
            continue
        out.append({
            "assignment_key": salted(
                st["token"], f"{it['course_id']}:{ident}:{it.get('points_possible', '')}"),
            "course_key": salted(st["token"], it["course_id"]),
            "type": t if t in TYPES else "homework",
            "pct": max(0.0, min(100.0, pct)),
            "difficulty": max(1.0, min(1.5, float(it.get("difficulty", 1.0)))),
        })
    res = call("/api/skill/grades", {"items": out}, st["token"])
    print(f"Points +{res['points']}, Mana +{res['mana']}, Shields +{res.get('shields', 0)}")
    battles_line(res)
    print(res["link"])


def cmd_link(a):
    st = load_state() or sys.exit("Not set up. Run optin first.")
    res = call("/api/skill/link", {}, st["token"])
    battles_line(res)
    print(res["link"])


def cmd_leave(a):
    st = load_state() or sys.exit("Not set up.")
    try:
        call("/api/skill/leave", {}, st["token"])
    except ServerError as e:
        if e.code != 401:  # 401 means the server already forgot this player
            raise
    os.remove(state_path())
    print("Left Clash. Game data deleted.")


def cmd_reset(a):
    """Clear this device's saved sign-in without calling the server."""
    try:
        os.remove(state_path())
        print("Cleared the saved Clash sign-in. Run optin to set up again.")
    except FileNotFoundError:
        print("Nothing to clear.")


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
    sub.add_parser("reset").set_defaults(fn=cmd_reset)
    a = p.parse_args()
    try:
        a.fn(a)
    except ServerError as e:
        if e.code == 401:
            sys.exit("The game server does not recognize this sign-in. Run 'reset', then set up again.")
        sys.exit(f"Server said {e.code}: {e.msg}")


if __name__ == "__main__":
    main()
