# analyze.py
# SUMMARY: km_since_service, avg_daily_km, and load_factor separate breakdown cars from healthy
# ones (60%, 22%, and 19% higher means respectively); odometer_km and age_years do NOT separate
# them at all (ratio ≈ 1.0). Risk score built from those three columns: 50% of top-30 broke down
# vs 0% of the bottom-30, confirming the score is meaningful.

# ---------------------------------------------------------------------------
# STEP 1 — Load and inspect
# ---------------------------------------------------------------------------
# We load fleet_history.csv and immediately split the 120 cars into two groups:
# those that later broke down (broke_down == 1) and those that did not (broke_down == 0).
# We then compare the mean of every feature column between the two groups.
# A large mean-difference tells us the column separates the groups.
# A tiny difference tells us it does not.
# We do NOT assume anything — we let the numbers speak.

import pandas as pd

df = pd.read_csv("fleet_history.csv")

features = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]

broken     = df[df["broke_down"] == 1]
not_broken = df[df["broke_down"] == 0]

print("=" * 60)
print(f"Total cars: {len(df)}   Broke down: {len(broken)}   Did not: {len(not_broken)}")
print("=" * 60)

# ---------------------------------------------------------------------------
# STEP 2 — Compare every column between the two groups
# ---------------------------------------------------------------------------
# For each feature we show:
#   mean for broken cars / mean for healthy cars / ratio (broken ÷ healthy)
# A ratio well above 1.0 means broken cars score higher on that column.
# A ratio near 1.0 means the column does NOT separate the groups.

print("\nColumn-by-column comparison (broken vs healthy):\n")
print(f"{'Column':<22} {'Mean (broke)':>14} {'Mean (ok)':>12} {'Ratio':>8}  Verdict")
print("-" * 72)

separators = []

for col in features:
    m_broke = broken[col].mean()
    m_ok    = not_broken[col].mean()
    ratio   = m_broke / m_ok if m_ok != 0 else float("inf")
    # A ratio outside [0.85, 1.15] is a meaningful signal (>15% difference).
    separates = abs(ratio - 1.0) > 0.15
    verdict = "SEPARATES" if separates else "no signal"
    if separates:
        separators.append(col)
    print(f"{col:<22} {m_broke:>14.2f} {m_ok:>12.2f} {ratio:>8.3f}  {verdict}")

print(f"\nColumns that genuinely separate the groups: {separators}")

# ---------------------------------------------------------------------------
# STEP 3 — Build a risk score 0–100 using only the separating columns
# ---------------------------------------------------------------------------
# We min-max normalise each separating column to [0, 1], then average them,
# then scale to [0, 100].  Min-max normalisation means the car with the
# highest value on a column scores 1.0, the car with the lowest scores 0.0,
# and everyone else sits in between.  No heavy ML — just transparent scaling.

print("\n" + "=" * 60)
print("Building risk score from separating columns only …")
print("=" * 60)

score = pd.Series(0.0, index=df.index)

for col in separators:
    col_min = df[col].min()
    col_max = df[col].max()
    if col_max > col_min:
        normalised = (df[col] - col_min) / (col_max - col_min)
    else:
        normalised = pd.Series(0.0, index=df.index)
    score += normalised

# Average across separating columns, then scale to 0–100
score = (score / len(separators)) * 100
df["risk_score"] = score.round(1)

# ---------------------------------------------------------------------------
# STEP 4 — Rank by risk, print top 10
# ---------------------------------------------------------------------------

ranked = df.sort_values("risk_score", ascending=False).reset_index(drop=True)

print("\nTop 10 highest-risk cars (flag these BEFORE the 80% rule fires):\n")
print(f"{'Rank':<6} {'car_id':<12} {'risk_score':>10}  {'broke_down':>10}  details")
print("-" * 72)

for rank, (_, row) in enumerate(ranked.head(10).iterrows(), start=1):
    detail_parts = [f"{col}={row[col]:.0f}" for col in separators]
    detail = "  ".join(detail_parts)
    flag = " ** BROKE" if row["broke_down"] == 1 else ""
    print(f"{rank:<6} {row['car_id']:<12} {row['risk_score']:>10.1f}  {int(row['broke_down']):>10}  {detail}{flag}")

# ---------------------------------------------------------------------------
# STEP 5 — Sanity check: do the high-risk cars actually align with breakdowns?
# ---------------------------------------------------------------------------
# We check what fraction of the TOP-30 (by risk score) actually broke down,
# versus the bottom-30.  If the score is meaningful, the top group should
# have a much higher breakdown rate.

top30_rate    = ranked.head(30)["broke_down"].mean()
bottom30_rate = ranked.tail(30)["broke_down"].mean()

print(f"\nSanity check:")
print(f"  Breakdown rate in TOP-30 risk cars    : {top30_rate:.0%}")
print(f"  Breakdown rate in BOTTOM-30 risk cars : {bottom30_rate:.0%}")
print(f"  (A useful score puts most breakdowns in the top group.)")

# ---------------------------------------------------------------------------
# Print the two-line summary so we can paste it at the top of the file.
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("COPY THIS TO THE TOP OF analyze.py:")
print(f"  Separating columns: {separators}")
print(f"  Top-30 breakdown rate: {top30_rate:.0%}  |  Bottom-30: {bottom30_rate:.0%}")
