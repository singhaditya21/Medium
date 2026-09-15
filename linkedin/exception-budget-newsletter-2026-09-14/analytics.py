"""Reproducible hypothetical planning calculations; no measured customer data."""
import json
import math
from pathlib import Path


def wilson(k, n, z=1.959963984540054):
    if n <= 0 or not 0 <= k <= n or z <= 0:
        raise ValueError('Require n > 0, 0 <= k <= n, z > 0')
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)


def recovery_hours(actions, probability, mean_minutes):
    if actions < 0 or not 0 <= probability <= 1 or mean_minutes <= 0:
        raise ValueError('Invalid workload')
    return actions * probability * mean_minutes / 60


def planning_cap(hours, use_fraction, probability, mean_minutes):
    if hours < 0 or not 0 < use_fraction <= 1 or not 0 < probability <= 1 or mean_minutes <= 0:
        raise ValueError('Invalid capacity inputs')
    return math.floor(60 * hours * use_fraction / (probability * mean_minutes))


def mmc(arrivals_per_hour, service_per_hour=5, servers=4):
    if arrivals_per_hour < 0 or service_per_hour <= 0 or not isinstance(servers, int) or servers < 1:
        raise ValueError('Invalid M/M/c inputs')
    a = arrivals_per_hour / service_per_hour
    rho = a / servers
    if rho >= 1:
        return {'rho': rho, 'stable': False, 'p_wait': None, 'mean_wait_min': None, 'p95_wait_min': None}
    tail = a ** servers / (math.factorial(servers) * (1 - rho))
    c = tail / (sum(a ** k / math.factorial(k) for k in range(servers)) + tail)
    spare = servers * service_per_hour - arrivals_per_hour
    p95 = 0 if c <= .05 else 60 * math.log(c / .05) / spare
    return {'rho': rho, 'stable': True, 'p_wait': c, 'mean_wait_min': 60 * c / spare, 'p95_wait_min': p95}


def fluid_backlog(days, actions, probability, daily_case_capacity, initial=0):
    if days < 0 or actions < 0 or not 0 <= probability <= 1 or daily_case_capacity < 0 or initial < 0:
        raise ValueError('Invalid fluid inputs')
    values = [initial]
    for _ in range(days):
        values.append(max(0, values[-1] + actions * probability - daily_case_capacity))
    return values


def results():
    lo, hi = wilson(100, 10000)
    return {
        'evidence_class': 'Hypothetical worked scenarios; analytic outputs, not observed results',
        'assumptions': {'actions_per_day': 10000, 'human_exception_probability': .01,
                        'mean_recovery_minutes': 12, 'reviewers': 4, 'hours_per_reviewer_day': 4,
                        'planning_use_fraction': .75, 'hypothetical_exceptions': 100,
                        'hypothetical_mature_cohort': 10000},
        'baseline_demand_hours': recovery_hours(10000, .01, 12),
        'capacity_hours': 16, 'capacity_cases': 80,
        'planned_hours': 12, 'planned_cases': 60,
        'cap_point_estimate': planning_cap(16, .75, .01, 12),
        'wilson_95': [lo, hi], 'cap_wilson_upper': planning_cap(16, .75, hi, 12),
        'scenarios': [{'p': p, 'cases': 10000*p, 'demand_hours': recovery_hours(10000,p,12),
                       'backlog': fluid_backlog(5,10000,p,80)} for p in [.002,.01,.02]],
        'queue_rows': [mmc(rho*20) for rho in [.5,.75,.9,.95,.98]],
        'queue_curve': [mmc(i/10*20/100) for i in range(500,981,4)],
        'capacity_curve': [{'p': i/10000, 'cap': planning_cap(16,.75,i/10000,12)} for i in range(20,251)],
        'economics': {'hypothetical_baseline_minutes_per_action': 3,
                      'gross_capacity_hours': 500, 'recovery_hours': 20,
                      'verification_hours_assumption': 30, 'control_operations_hours_assumption': 40,
                      'net_capacity_hours': 410},
    }


if __name__ == '__main__':
    Path(__file__).with_name('calculations.json').write_text(json.dumps(results(), indent=2) + '\n')
