#!/usr/bin/env python3
"""payoff.py — compare debt payoff orders: avalanche (highest APR first) vs snowball (smallest balance first).

    python3 payoff.py example_accounts.json                 # table for several extra-payment amounts
    python3 payoff.py example_accounts.json --extra 200     # one amount, with the payoff order

Each month every account accrues interest (APR / 12) and gets its minimum payment; the extra amount, plus
the minimums of accounts already paid off ("freed" money), goes to the first unpaid account in the order.
Standard library only. This is arithmetic, not financial advice.
"""
import argparse, copy, json, sys


def load(path):
    """accounts.json: [{"name": str, "balance": float, "apr": 0.25, "min_payment": float}, ...]"""
    with open(path) as f:
        accts = json.load(f)
    for a in accts:
        if a["balance"] < 0 or a["apr"] < 0 or a["min_payment"] <= 0:
            raise ValueError(f"bad account {a['name']!r}: balance/apr must be >= 0 and min_payment > 0")
    return accts


def avalanche(accts):
    return [a["name"] for a in sorted(accts, key=lambda a: -a["apr"])]


def snowball(accts):
    return [a["name"] for a in sorted(accts, key=lambda a: a["balance"])]


def simulate(accts, extra, order, max_months=600):
    """Returns {"months", "total_paid", "total_interest", "paid_off": [names in payoff order]}."""
    acc = {a["name"]: copy.deepcopy(a) for a in accts}
    months = 0; paid = interest = freed = 0.0; done = []
    while any(a["balance"] > 0.005 for a in acc.values()) and months < max_months:
        months += 1
        for a in acc.values():
            if a["balance"] <= 0.005:
                continue
            i = a["balance"] * a["apr"] / 12
            a["balance"] += i; interest += i
            pay = min(a["min_payment"], a["balance"])
            a["balance"] -= pay; paid += pay
        pool = extra + freed
        for name in order:
            a = acc[name]
            if pool <= 0:
                break
            if a["balance"] <= 0.005:
                continue
            pay = min(pool, a["balance"]); a["balance"] -= pay; pool -= pay; paid += pay
        for name, a in acc.items():
            if a["balance"] <= 0.005 and name not in done:
                done.append(name); freed += a["min_payment"]; a["balance"] = 0.0
    return {"months": months, "total_paid": round(paid, 2), "total_interest": round(interest, 2), "paid_off": done}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Avalanche vs snowball debt payoff")
    ap.add_argument("accounts")
    ap.add_argument("--extra", type=float, help="extra dollars per month on top of the minimums")
    a = ap.parse_args(argv)
    try:
        accts = load(a.accounts)
    except (OSError, ValueError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr); return 1
    print(f"Total debt: ${sum(x['balance'] for x in accts):,.2f}; minimums: ${sum(x['min_payment'] for x in accts):,.2f}/mo\n")
    if a.extra is not None:
        for label, order in (("Avalanche", avalanche(accts)), ("Snowball", snowball(accts))):
            r = simulate(accts, a.extra, order)
            print(f"{label}: {r['months']} months, interest ${r['total_interest']:,.2f}; paid off in order: {' -> '.join(r['paid_off'])}")
        return 0
    print(f"{'Extra/mo':>9} | {'Avalanche':>22} | {'Snowball':>22} | Avalanche saves")
    for extra in (0, 50, 100, 200, 400):
        av = simulate(accts, extra, avalanche(accts)); sn = simulate(accts, extra, snowball(accts))
        print(f"{extra:>9.0f} | {av['months']:>3} mo, ${av['total_interest']:>10,.2f} | {sn['months']:>3} mo, ${sn['total_interest']:>10,.2f} | ${sn['total_interest'] - av['total_interest']:,.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
