"""A synthetic EU market with planted defects and an answer key.

Generates fictional campaigns across markets, plants known defects in some of them, and
writes the answer key separately. Then scores any QA checker against that key, so a demo
becomes a test: if a planted defect isn't found, the check is wrong. Standard library only.
"""
import json
import random
import sys

MARKETS = {
    "HR": {"currency": "€", "lang": "hr"}, "SI": {"currency": "€", "lang": "sl"},
    "AT": {"currency": "€", "lang": "de"}, "GR": {"currency": "€", "lang": "el"},
    "HU": {"currency": "Ft", "lang": "hu"}, "CZ": {"currency": "Kč", "lang": "cs"},
    "RS": {"currency": "RSD", "lang": "sr"}, "LV": {"currency": "€", "lang": "lv"},
}
DEFECTS = ["missing_unsubscribe", "late_send", "missing_consent_filter",
           "english_price_format", "wrong_currency", "missing_proof"]


def clean_campaign(i, market, rnd):
    cur = MARKETS[market]["currency"]
    return {"id": f"{market}-{i:03d}", "market": market,
            "html": f'<p>{rnd.randint(19, 999)},00 {cur}</p><a href="https://example.com/unsubscribe">x</a>',
            "send_time": f"{rnd.randint(8, 19):02d}:{rnd.choice(['00', '30'])}",
            "filters": ["marketing_optin"], "proof_by": f"{market.lower()}.marketing"}


def plant(c, defect):
    if defect == "missing_unsubscribe":
        c["html"] = c["html"].replace("unsubscribe", "preferences")
    elif defect == "late_send":
        c["send_time"] = "23:30"
    elif defect == "missing_consent_filter":
        c["filters"] = []
    elif defect == "english_price_format":
        c["html"] = c["html"].replace("<p>", "<p>€").replace(",00 €", ".00").replace(",00 ", ".00 ")
    elif defect == "wrong_currency":
        wrong = "Ft" if MARKETS[c["market"]]["currency"] != "Ft" else "Kč"
        c["html"] = c["html"].replace(MARKETS[c["market"]]["currency"], wrong)
    elif defect == "missing_proof":
        c["proof_by"] = ""
    return c


def generate(n=40, defect_rate=0.3, seed=7):
    rnd = random.Random(seed)
    campaigns, key = [], {}
    for i in range(n):
        market = rnd.choice(sorted(MARKETS))
        c = clean_campaign(i, market, rnd)
        if rnd.random() < defect_rate:
            d = rnd.choice(DEFECTS)
            plant(c, d)
            key[c["id"]] = d
        campaigns.append(c)
    return campaigns, key


def basic_checker(c):
    """A typical first QA checker. It knows 5 of the 6 defect types."""
    found = []
    if "unsubscribe" not in c["html"]:
        found.append("missing_unsubscribe")
    if not "08:00" <= c["send_time"] <= "21:00":
        found.append("late_send")
    if "marketing_optin" not in c["filters"]:
        found.append("missing_consent_filter")
    if "<p>€" in c["html"]:
        found.append("english_price_format")
    if not c["proof_by"]:
        found.append("missing_proof")
    return found


def score(checker, campaigns, key):
    hits, misses, false_alarms = 0, {}, 0
    for c in campaigns:
        found = set(checker(c))
        planted = key.get(c["id"])
        if planted and planted in found:
            hits += 1
        elif planted:
            misses[planted] = misses.get(planted, 0) + 1
        false_alarms += len(found - {planted})
    return {"planted": len(key), "found": hits, "missed": misses, "false_alarms": false_alarms}


def main(argv):
    n = int(argv[0]) if argv else 40
    campaigns, key = generate(n)
    with open("out_campaigns.json", "w", encoding="utf-8") as fh:
        json.dump(campaigns, fh, indent=1, ensure_ascii=False)
    with open("out_answer_key.json", "w", encoding="utf-8") as fh:
        json.dump(key, fh, indent=1)
    s = score(basic_checker, campaigns, key)
    print(f"{n} synthetic campaigns across {len(MARKETS)} markets, {s['planted']} defects planted")
    print(f"basic checker found {s['found']}/{s['planted']}, false alarms {s['false_alarms']}")
    for defect, count in s["missed"].items():
        print(f"  MISSED {count} x {defect}")


if __name__ == "__main__":
    main(sys.argv[1:])
