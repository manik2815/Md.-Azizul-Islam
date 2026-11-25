#!/usr/bin/env python3
"""Fetch Binance P2P USDT/BDT ads and write p2p.json for the Mini App.

Runs from the repo root (GitHub Actions) or from the miniapp dir (local).
No API key needed: the Binance P2P search endpoint is public.
Output: p2p.json with the top 10 buy ads and top 10 sell ads.
"""
import json
import os
import urllib.request
import datetime

URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"


def fetch_side(trade):
    body = json.dumps({
        "asset": "USDT", "fiat": "BDT",
        "page": 1, "rows": 10, "tradeType": trade,
    }).encode()
    req = urllib.request.Request(
        URL, data=body,
        headers={"Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    ads = []
    for item in data.get("data", []):
        a = item.get("adv", {})
        try:
            ads.append({
                "p": float(a["price"]),
                "min": float(a["minSingleTransAmount"]),
                "max": float(a["maxSingleTransAmount"]),
                "minq": float(a.get("minSingleTransQuantity") or 0),
                "maxq": float(a.get("maxSingleTransQuantity") or 0),
                "pays": sorted({m.get("tradeMethodName")
                                for m in a.get("tradeMethods", [])
                                if m.get("tradeMethodName")}),
            })
        except (KeyError, TypeError, ValueError):
            continue
    return ads


def main():
    out = {
        "updated": datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "asset": "USDT",
        "fiat": "BDT",
        "buy": fetch_side("BUY"),    # ads to BUY USDT from (sellers)
        "sell": fetch_side("SELL"),  # ads to SELL USDT to (buyers)
    }
    here = os.path.dirname(os.path.abspath(__file__))
    # p2p.json lives next to index.html, one level above scripts/
    # (locally: miniapp/p2p.json; in Actions: repo-root p2p.json).
    target = os.path.join(os.path.dirname(here), "p2p.json")
    with open(target, "w", encoding="utf-8") as f:
        json.dump(out, f)
    print(f"wrote {target}: {len(out['buy'])} buy, {len(out['sell'])} sell ads")


if __name__ == "__main__":
    main()
