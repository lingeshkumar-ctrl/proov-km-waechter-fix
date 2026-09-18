# What I checked, and what the agent got wrong

## What the agent got wrong

The agent hit a Windows console encoding crash on the first run of analyze.py. It used a
left-arrow character inside an f-string that was printed to the terminal, and PowerShell's
cp1252 codec cannot encode that character, so the script aborted before printing the top-10
table or the sanity-check numbers. The agent caught it in the error output and replaced the
character with `** BROKE` on the next edit. No data was wrong -- it was purely an output
encoding mistake -- but it meant the first run of analyze.py produced no useful results
until the fix was applied.

A second thing worth noting: the agent's initial loop variable in the top-10 table used `i`
from `iterrows()` (which is the DataFrame row index, not the rank number), so the rank
column would have printed the original CSV row numbers instead of 1-10. That was fixed in
the same edit as the encoding issue.

## What I checked before I accepted its work

I ran `python verify.py` after every round of changes and only accepted the result when the
relevant checks showed PASS. Specifically:

- **Wear calculation**: verify.py reports `a car at 14,900 of 15,000 km reports 99.3%`
  under the "Wear is no longer floored to 0" check. Before the fix it reported 0%. I
  confirmed the change was simply `//` replaced by `/` in `wear_percent()`, which cannot
  accidentally touch the 15 000 km interval or the 80% threshold -- those constants are not
  involved in the division operator change.

- **80% rule untouched**: verify.py checks `km.SERVICE_INTERVAL_KM == 15000 and
  km.WARN_AT_PERCENT == 80` directly in code and `get_int(s, "service_interval_km") ==
  15000` from settings.cfg. Both showed PASS and the values were not edited.

- **Missing-reading handling**: the test `test_missing_reading_is_not_treated_as_zero`
  passed, and verify.py's "A missing reading is handled" check confirmed `needs_service`
  returns False for a car with no last_service_km key.

- **km-to-miles**: verify.py checks `61.0 <= km_to_miles(100) <= 62.5`. The old constant
  1.609 gave 160.9 miles for 100 km (plainly wrong). The corrected constant 0.621371
  gives 62.1, which falls inside the expected range.

- **Full test suite**: `pytest` showed 4/4 PASS before the final push.

## What the data actually said

The obvious assumption going in was that high-mileage or older cars break down more. The
data does not support that at all. `odometer_km` has a broken-vs-healthy ratio of 1.003 --
the mean total mileage is virtually identical between cars that broke down and cars that did
not. `age_years` is even flatter at 0.998 -- the two groups have the same average age.

What actually separates the groups is how hard the car is being worked right now:

- `km_since_service` -- broken cars are on average 61% further past their last service
  (mean 11,678 km vs 7,261 km). This is the strongest single signal.
- `avg_daily_km` -- broken cars are driven about 22% more kilometres per day (160 vs 131).
- `load_factor` -- broken cars carry about 19% heavier loads (0.60 vs 0.51).

A min-max risk score built from just those three columns concentrated all the signal
correctly: 50% of the top-30 risk cars actually broke down, while 0% of the bottom-30 did.
The overall fleet breakdown rate is 22%, so the score is meaningfully separating high-risk
cars from low-risk ones -- exactly what the team needs to act before the 80% wear rule would
ever fire.
