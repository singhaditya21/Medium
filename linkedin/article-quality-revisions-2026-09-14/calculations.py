"""Scenario arithmetic only: inputs are assumptions, not account analytics."""
import math


def probability(value):
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("probability outside [0,1]")
    return value


def expected_escapes(volume, error, high_given_error, timely_recall):
    if not math.isfinite(volume) or volume < 0:
        raise ValueError("volume must be nonnegative")
    return volume * probability(error) * probability(high_given_error) * (1 - probability(timely_recall))


def repair_hours(volume_per_day, days, error_rate, minutes_per_error):
    if any(not math.isfinite(v) or v < 0 for v in (volume_per_day, days, minutes_per_error)):
        raise ValueError("negative or nonfinite workload input")
    return volume_per_day * days * probability(error_rate) * minutes_per_error / 60


def zero_failure_upper_bound(trials, alpha=0.05):
    if type(trials) is not int or trials <= 0 or not 0 < alpha < 1:
        raise ValueError("positive integer trials and 0 < alpha < 1 required")
    # One-sided exact binomial bound for zero failures in independent trials.
    return -math.expm1(math.log(alpha) / trials)
