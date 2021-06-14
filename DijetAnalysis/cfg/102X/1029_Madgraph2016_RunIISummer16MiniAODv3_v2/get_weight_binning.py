#!/usr/bin/env python
import numpy as np

from dijetAna_deploy import *

def _find_nice_break(a, b):
    '''
    find a value `t` with `a` < `t` < `b` such that log10(t) has the least
    number of significant digits possible
    '''
    assert a != b, "`a` and `b` cannot have the same value!"
    log_a, log_b = np.log10(a), np.log10(b)
    log_avg = 0.5 * (log_a + log_b)

    sig = int(-np.sign(log_avg) * (int(abs(log_avg)) - np.sign(log_avg)*1))

    #print("[{}, {}] -> {} (at sig {}: {}) log_avg = {}".format(a, b, 10 ** log_avg, sig, round(10 ** log_avg, sig), log_avg))
    #print("[{}, {}] -> {}".format(a, b, round(10 ** log_avg, sig)))
    return round(10 ** log_avg, sig)

print("[INFO] Computing nice bin edges for stitching weights.")
print("[INFO] Reading weights from deployment file.")

# compute weights and convert to log space
WEIGHTS = {}
for s in CROSS_SECTION_LOOKUP:
    WEIGHTS[s] = float(CROSS_SECTION_LOOKUP[s]) / float(NUMBER_OF_EVENTS_LOOKUP[s])

weights = sorted(WEIGHTS.values())

print("[INFO] Weight values are:")
print("[INFO]     {}".format(weights))

# add dummy values outside range
weights = [weights[0]/10] + weights + [weights[-1]*10]

# find nice bin edges
bin_edges = [
    _find_nice_break(a, b)
    for a, b in zip(weights[:-1], weights[1:])
]

# check that all weights are within bin bounds
_check = list(
    a < be < b
    for a, b, be in zip(weights[:-1], weights[1:], bin_edges)
)

# inform if check failed
if not all(_check):
    print("[ERROR] Failed to find nice binning.")
    print("[INFO] Potential bin edges are:")
    print("[INFO]     {}".format(bin_edges))
    print("[INFO] But not all weights are between the edge bounds:")
    print("[INFO]     {}".format(_check))
else:
    print("[INFO] Found nice binning. Bin edges are:")
    print("[INFO]     {}".format(bin_edges))
