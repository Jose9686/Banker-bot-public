import unittest

import payoff

ACCTS = [
    {"name": "high", "balance": 1000.0, "apr": 0.30, "min_payment": 50.0},
    {"name": "small", "balance": 200.0, "apr": 0.10, "min_payment": 25.0},
]


class PayoffTests(unittest.TestCase):
    def test_orders(self):
        self.assertEqual(payoff.avalanche(ACCTS), ["high", "small"])
        self.assertEqual(payoff.snowball(ACCTS), ["small", "high"])

    def test_zero_apr_is_plain_division(self):
        r = payoff.simulate([{"name": "x", "balance": 300.0, "apr": 0.0, "min_payment": 100.0}], 0, ["x"])
        self.assertEqual((r["months"], r["total_paid"], r["total_interest"]), (3, 300.0, 0.0))

    def test_avalanche_never_costs_more_interest(self):
        for extra in (0, 50, 200):
            av = payoff.simulate(ACCTS, extra, payoff.avalanche(ACCTS))
            sn = payoff.simulate(ACCTS, extra, payoff.snowball(ACCTS))
            self.assertLessEqual(av["total_interest"], sn["total_interest"] + 1e-6)

    def test_extra_money_pays_off_sooner(self):
        slow = payoff.simulate(ACCTS, 0, payoff.avalanche(ACCTS))
        fast = payoff.simulate(ACCTS, 200, payoff.avalanche(ACCTS))
        self.assertLess(fast["months"], slow["months"])
        self.assertEqual(sorted(fast["paid_off"]), ["high", "small"])

    def test_inputs_not_mutated(self):
        before = [dict(a) for a in ACCTS]
        payoff.simulate(ACCTS, 100, payoff.avalanche(ACCTS))
        self.assertEqual(ACCTS, before)


if __name__ == "__main__":
    unittest.main()
