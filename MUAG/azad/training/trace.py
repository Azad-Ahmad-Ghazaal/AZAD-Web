#!/usr/bin/env python3
import json, pathlib, time

STORE = pathlib.Path("/var/lib/muag/azad/training")
STORE.mkdir(parents=True, exist_ok=True)

def record(intent, observations, actions, result=None):
    trace = {
        "version": 1, "timestamp": int(time.time()), "status": "pending",
        "intent": str(intent), "observations": list(observations),
        "actions": list(actions), "result": result
    }
    path = STORE / f"trace-{trace['timestamp']}.json"
    path.write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)

if __name__ == "__main__":
    print(record("demo", ["page loaded"], ["click safe control"], "pending"))
