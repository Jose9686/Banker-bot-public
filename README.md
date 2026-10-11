# Banker-bot-public

**Debt payoff planner:** compares the two classic strategies for paying off
several debts, using your own numbers.

- **Avalanche:** put every extra dollar on the highest-APR debt first. This
  minimizes total interest.
- **Snowball:** put it on the smallest balance first. Debts disappear sooner,
  which some people find motivating.

Each month every account accrues interest and gets its minimum payment. The
extra amount, plus the minimums of debts already paid off, goes to the next
debt in the chosen order.

```bash
python3 payoff.py example_accounts.json              # compare at $0, $50, $100, $200, $400 extra per month
python3 payoff.py example_accounts.json --extra 200  # one amount, with the payoff order
```

Put your own debts in a JSON file shaped like `example_accounts.json` (keep it
out of Git). Standard library only.

This is arithmetic, not financial advice.

## Tests

```bash
python3 -m unittest discover -s tests -t .
```
