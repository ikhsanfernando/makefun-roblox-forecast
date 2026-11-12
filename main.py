import json, os

I = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
O = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
A, B, C, DECAY, TOP, N = 0.25, 0.15, 0.09, 0.9, 1.3, 10

task = json.load(open(f"{I}/task.json"))
last = json.loads([l for l in open(f"{I}/history.ndjson") if l.strip()][-1])
chart = [g["universe_id"] for g in sorted(last["up_and_coming"], key=lambda g: g["rank"])]


def forecast(chart):
    rows, total = [], {}

    def add(uid, k, w):
        if 1 <= k <= N:
            total[k] = total.get(k, 0.0) + w
            rows.append((uid, k, w))


    for n, uid in enumerate(chart[:N], start=1):
        w = DECAY ** (n - 1)
        places = {n: A * w * (TOP if n == 1 else 1), n - 1: B * w, n + 1: B * w, n - 2: C * w, n + 2: C * w}
        places = {k: v for k, v in places.items() if 1 <= k <= N and k <= len(chart)}
        s = sum(places.values()) or 1.0
        for k, v in places.items():
            add(uid, k, v / s)

    return rows, total, [int(u) for u in chart[:N]]


rows, total, top10 = forecast(chart)

out = [{"universe_id": int(u), "place": int(k), "p": round(min(p / max(total[k], 1.0), 1.0), 6)}
       for u, k, p in rows]
os.makedirs(O, exist_ok=True)
json.dump({"probabilities": out, "top10": top10},
          open(os.path.join(O, task.get("output", "forecast.json")), "w"))
