import itertools
import os

import numpy as np

from Karma.PostProcessing.Lumberjack import Quantity


_QCD_BINNING = [15, 30, 50, 80, 120, 170, 300, 470, 600, 800, 1000, 1400, 1800, 1800, 2400, 3200, 7000]
_QCD_BINNING_FINE = np.hstack(
    [np.linspace(lo, hi, 21)[:-1] for lo, hi in zip(_QCD_BINNING[:-1], _QCD_BINNING[1:])]
        + [_QCD_BINNING[-1]]  # add final bin edge
)

__all__ = ["ROOT_MACROS", "QUANTITIES", "DEFINES", "SELECTIONS", "SPLITTINGS"]


# load ROOT macros into config string

_root_macro_file_path = os.path.join(os.path.dirname(__file__), "root_macros.C")
with open(_root_macro_file_path, 'r') as _root_macro_file:
    ROOT_MACROS = ''.join(_root_macro_file.readlines())

# specification of quantities
# NOTE: a 'Define' will be applied to the data frame for every quantity whose name is different from its expression
QUANTITIES = {
    'global': {
        'run': Quantity(
            name='run',
            expression='run',
            binning=np.linspace(278820, 280385, 30)
        ),

        # for counting experiments
        'count': Quantity(
            name='count',
            expression='0.5',
            binning=(0, 1)
        ),

        # pileup-related
        'npv': Quantity(
            name='npv',
            expression='npv',
            binning=np.arange(0, 101)-0.5
        ),
        'npvGood': Quantity(
            name='npvGood',
            expression='npvGood',
            binning=np.arange(0, 101)-0.5
        ),
        'nPUMean': Quantity(
            name='nPUMean',
            expression='nPUMean',
            binning=np.arange(0, 101)-0.5
        ),
        # same as nPUMean, but different binning
        'pileup': Quantity(
            name='pileup',
            expression='nPUMean',
            binning=np.arange(0, 80+1)
        ),

        'metOverSumET': Quantity(
            name='metOverSumET',
            expression='met/sumEt',
            binning=np.linspace(0, 1, 51)
        ),

        # "wide" binning with target resolution/bin_width of 0.5
        'jet1pt_wide': Quantity(
            name='jet1pt_wide',
            expression='jet1pt',
            binning=(60, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307, 1458, 1621, 1806, 2003, 2217, 2453, 2702, 2977, 3249, 3557, 3816, 4045),
        ),
        'jet12mass_wide': Quantity(
            name='jet12mass_wide',
            expression='jet12mass',
            binning=(100, 200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915, 3306, 3754, 4244, 4805, 5374, 5994, 6672, 7456, 8401),
            named_binnings={
                "ybys_narrow" : {
                    # target event yield per bin: 100
                    'YB_00_05_YS_00_05' : [100, 200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915, 3306, 3754, 4244, 4805, 5374,                   8401],
                    'YB_00_05_YS_05_10' : [100, 200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915, 3306, 3754, 4244, 4805, 5374,                   8401],
                    'YB_00_05_YS_10_15' : [     200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915, 3306, 3754, 4244, 4805, 5374,                   8401],
                    'YB_00_05_YS_15_20' : [               306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915, 3306, 3754, 4244, 4805, 5374,                   8401],
                    'YB_00_05_YS_20_25' : [                              539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915, 3306, 3754, 4244, 4805, 5374,                   8401],

                    'YB_05_10_YS_00_05' : [100, 200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915, 3306, 3754, 4244,             5994],
                    'YB_05_10_YS_05_10' : [100, 200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915, 3306, 3754, 4244,             5994],
                    'YB_05_10_YS_10_15' : [     200, 269, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915, 3306, 3754, 4244,             5994],
                    'YB_05_10_YS_15_20' : [               306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915, 3306, 3754, 4244,             5994],

                    'YB_10_15_YS_00_05' : [100, 200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915,       3754],
                    'YB_10_15_YS_05_10' : [100, 200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915,       3754],
                    'YB_10_15_YS_10_15' : [     200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915,       3754],

                    'YB_15_20_YS_00_05' : [100, 200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008,       2572],
                    'YB_15_20_YS_05_10' : [100, 200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008,       2572],

                    'YB_20_25_YS_00_05' : [100, 200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187,       1556],

                    'inclusive'         : [100, 200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915, 3306, 3754, 4244, 4805, 5374, 5994, 6672, 7456, 8401],
                }
            },
        ),
        'jet12ptave_wide': Quantity(
            name='jet12ptave_wide',
            expression='jet12ptave',
            binning=(75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307, 1458, 1621, 1806, 2003, 2217, 2453, 2702, 2977, 3249, 3557, 3816, 4045),
            named_binnings={
                "ybys_narrow" : {
                    # target event yield per bin: 100
                    'inclusive'         : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307, 1458, 1621, 1806, 2003, 2217, 2453, 2702, 2977, 3249, 3557, 3816, 4045],

                    'YB_00_05_YS_00_05' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307, 1458, 1621, 1806, 2003, 2217, 2453, 2702],
                    'YB_00_05_YS_05_10' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307, 1458, 1621, 1806, 2003, 2217, 2453],
                    'YB_00_05_YS_10_15' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307, 1458, 1621, 1806],
                    'YB_00_05_YS_15_20' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307],
                    'YB_00_05_YS_20_25' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827],

                    'YB_05_10_YS_00_05' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307, 1458, 1621, 1806, 2003, 2217],
                    'YB_05_10_YS_05_10' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307, 1458, 1621, 1806],
                    'YB_05_10_YS_10_15' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307, 1458],
                    'YB_05_10_YS_15_20' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046],

                    'YB_10_15_YS_00_05' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307, 1458, 1621],
                    'YB_10_15_YS_05_10' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307],
                    'YB_10_15_YS_10_15' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046],

                    'YB_15_20_YS_00_05' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046],
                    'YB_15_20_YS_05_10' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931],

                    'YB_20_25_YS_00_05' : [75, 100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732],
                },
            },
        ),

        # "narrow" binning with target resolution/bin_width of 1.0
        'jet1pt_narrow': Quantity(
            name='jet1pt_narrow',
            expression='jet1pt',
            binning=(60, 69, 79, 90, 102, 115, 129, 144, 160, 177, 194, 213, 233, 254, 277, 301, 326, 352, 380, 411, 443, 476, 510, 546, 584, 624, 665, 709, 755, 803, 852, 903, 956, 1012, 1070, 1130, 1193, 1258, 1326, 1398, 1472, 1549, 1629, 1712, 1799, 1884, 1971, 2062, 2156, 2256, 2361, 2461, 2562, 2669, 2778, 2893, 3019, 3143, 3267, 3402, 3569, 3715, 3805, 3930, 4084, 4413)
        ),
        'jet12mass_narrow': Quantity(
            name='jet12mass_narrow',
            expression='jet12mass',
            binning=(200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3533, 3730, 3933, 4147, 4373, 4612, 4861, 5105, 5355, 5617, 5890, 6174, 6470, 6801, 7141, 7506, 7900, 8396, 8930, 9551, 9951),
            named_binnings={
                "ybys_narrow" : {
                    # target event yield per bin: 10
                    'inclusive'         : [200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3533, 3730, 3933, 4147, 4373, 4612, 4861, 5105, 5355, 5617, 5890, 6174, 6470, 6801, 7141, 7506, 7900, 8396, 8930, 9551, 9951],
                    'YB_00_05_YS_00_05' : [200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3533, 3730, 3933, 4147, 4373, 4612, 4861, 5105, 5355, 5890],
                    'YB_00_05_YS_05_10' : [200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3533, 3730, 3933, 4147, 4373, 4612, 4861, 5105, 5355, 5617, 5890, 6470],
                    'YB_00_05_YS_10_15' : [200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3533, 3730, 3933, 4147, 4373, 4612, 4861, 5105, 5355, 5617, 5890, 6174, 6801],
                    'YB_00_05_YS_15_20' : [200, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3533, 3730, 3933, 4147, 4373, 4612, 4861, 5105, 5355, 5617, 5890, 6174, 6470, 6801, 8396],
                    'YB_00_05_YS_20_25' : [200, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3533, 3730, 3933, 4147, 4373, 4612, 4861, 5105, 5355, 5617, 5890, 6174, 6470, 6801, 7900],
                    'YB_05_10_YS_00_05' : [200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3533, 3730, 3933, 4147, 4373, 4612],
                    'YB_05_10_YS_05_10' : [200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3533, 3730, 3933, 4147, 4373, 4612, 4861],
                    'YB_05_10_YS_10_15' : [200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3533, 3730, 3933, 4147, 4373, 4612, 4861, 5105, 6470],
                    'YB_05_10_YS_15_20' : [200, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3533, 3730, 3933, 4147, 4373, 4612, 4861, 5105, 5355],
                    'YB_10_15_YS_00_05' : [200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3346],
                    'YB_10_15_YS_05_10' : [200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346],
                    'YB_10_15_YS_10_15' : [200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3730],
                    'YB_15_20_YS_00_05' : [200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173],
                    'YB_15_20_YS_05_10' : [200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2418],
                    'YB_20_25_YS_00_05' : [200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397],
                },
            },
        ),
        'jet12ptave_narrow': Quantity(
            name='jet12ptave_narrow',
            expression='jet12ptave',
            binning=                      (60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055, 1108, 1163, 1220, 1280, 1342, 1406, 1473, 1543, 1615, 1690, 1768, 1850, 1935, 2023, 2114, 2209, 2307, 2410, 2515, 2624, 2738, 2857, 2979, 3104, 3233, 3372, 3517, 3580, 3709, 3810, 3914, 3973),
            named_binnings={
                "ybys_narrow" : {
                    # target event yield per bin: 10
                    'inclusive'         : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055, 1108, 1163, 1220, 1280, 1342, 1406, 1473, 1543, 1615, 1690, 1768, 1850, 1935, 2023, 2114, 2209, 2307, 2410, 2515, 2624, 2738, 2857, 2979, 3104, 3233, 3372, 3517, 3580, 3709, 3810, 3914, 3973],
                    'YB_00_05_YS_00_05' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055, 1108, 1163, 1220, 1280, 1342, 1406, 1473, 1543, 1615, 1690, 1768, 1850, 1935, 2023, 2114, 2209, 2307, 2410, 2515, 2738],
                    'YB_00_05_YS_05_10' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055, 1108, 1163, 1220, 1280, 1342, 1406, 1473, 1543, 1615, 1690, 1768, 1850, 1935, 2023, 2114, 2209, 2307, 2410, 2738],
                    'YB_00_05_YS_10_15' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055, 1108, 1163, 1220, 1280, 1342, 1406, 1473, 1543, 1615, 1690, 1768, 1850],
                    'YB_00_05_YS_15_20' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055, 1108, 1163, 1220, 1342],
                    'YB_00_05_YS_20_25' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820],
                    'YB_05_10_YS_00_05' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055, 1108, 1163, 1220, 1280, 1342, 1406, 1473, 1543, 1615, 1690, 1768, 1850, 1935, 2023, 2209],
                    'YB_05_10_YS_05_10' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055, 1108, 1163, 1220, 1280, 1342, 1406, 1473, 1543, 1615, 1690, 1768, 1935],
                    'YB_05_10_YS_10_15' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055, 1108, 1163, 1220, 1280, 1342, 1406, 1543],
                    'YB_05_10_YS_15_20' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1055],
                    'YB_10_15_YS_00_05' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055, 1108, 1163, 1220, 1280, 1342, 1406, 1473, 1615],
                    'YB_10_15_YS_05_10' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055, 1108, 1163, 1220, 1280, 1473],
                    'YB_10_15_YS_10_15' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1055],
                    'YB_15_20_YS_00_05' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055],
                    'YB_15_20_YS_05_10' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908],
                    'YB_20_25_YS_00_05' : [60, 100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 778],
                },
            },
        ),

        # other jet quantities
        'jet1y': Quantity(
            name='jet1y',
            expression='jet1y',
            binning=[-5, -3.0, -2.853, -2.650, -2.500, -2.322, -2.172, -1.930, -1.653, -1.479, -1.305, -1.044, -0.783, -0.522, -0.261, 0.000, 0.261, 0.522, 0.783, 1.044, 1.305, 1.479, 1.653, 1.930, 2.172, 2.322, 2.500, 2.650, 2.853, 3.0, 5]
        ),
        'absjet1y': Quantity(
            name='absjet1y',
            expression='abs(jet1y)',
            binning=[0.000, 0.261, 0.522, 0.783, 1.044, 1.305, 1.479, 1.653, 1.930, 2.172, 2.322, 2.500, 2.650, 2.853, 3.0, 5]
        ),
        'jet1phi': Quantity(
            name='jet1phi',
            expression='jet1phi',
            binning=np.linspace(-np.pi, np.pi, 41),
        ),
        'jet2y': Quantity(
            name='jet2y',
            expression='jet2y',
            binning=[-5, -3.0, -2.853, -2.650, -2.500, -2.322, -2.172, -1.930, -1.653, -1.479, -1.305, -1.044, -0.783, -0.522, -0.261, 0.000, 0.261, 0.522, 0.783, 1.044, 1.305, 1.479, 1.653, 1.930, 2.172, 2.322, 2.500, 2.650, 2.853, 3.0, 5]
        ),
        'absjet2y': Quantity(
            name='absjet2y',
            expression='abs(jet2y)',
            binning=[0.000, 0.261, 0.522, 0.783, 1.044, 1.305, 1.479, 1.653, 1.930, 2.172, 2.322, 2.500, 2.650, 2.853, 3.0, 5]
        ),
        'jet2phi': Quantity(
            name='jet2phi',
            expression='jet2phi',
            binning=np.linspace(-np.pi, np.pi, 41),
        ),

        # derived jet quantities
        'jet12DeltaPhi': Quantity(
            name='jet12DeltaPhi',
            #expression='abs(abs(jet1phi-jet2phi)-TMath::Pi())',
            expression='TMath::Pi() - fabs(fmod(fabs(jet1phi-jet2phi), 2*TMath::Pi()) - TMath::Pi())',
            binning=np.linspace(0, np.pi, 31),
        ),
        'jet12DeltaR': Quantity(
            name='jet12DeltaR',
            expression='TMath::Sqrt(TMath::Sq(TMath::Pi() - fabs(fmod(fabs(jet1phi-jet2phi), 2*TMath::Pi()) - TMath::Pi())) + TMath::Sq(abs(jet1eta-jet2eta)))',
            binning=np.linspace(0, 7, 51),
        ),

        # fine binning in y*/yb
        'ystar': Quantity(
            name='ystar',
            expression='abs(jet12ystar)',
            binning=np.arange(0, 3.0 + 0.1, 0.1)
        ),
        'yboost': Quantity(
            name='yboost',
            expression='abs(jet12yboost)',
            binning=np.arange(0, 3.0 + 0.1, 0.1)
        ),
        # fine binning in y*/yb
        'ystar_wide': Quantity(
            name='ystar_wide',
            expression='abs(jet12ystar)',
            binning=np.arange(0, 3.0 + 0.5, 0.5)
        ),
        'yboost_wide': Quantity(
            name='yboost_wide',
            expression='abs(jet12yboost)',
            binning=np.arange(0, 3.0 + 0.5, 0.5)
        ),

        # global index of bin (for unfolding)
        'binIndexJet12PtAve': Quantity(
            name='binIndexJet12PtAve',
            expression='binIndexJet12PtAve',
            binning=np.arange(-0.5, 300.5+1.0, 1.0)
        ),
        'binIndexJet12Mass': Quantity(
            name='binIndexJet12Mass',
            expression='binIndexJet12Mass',
            binning=np.arange(-0.5, 300.5+1.0, 1.0)
        ),
    },
    'mc': {
        'computedWeightForStitching': Quantity(
            name='computedWeightForStitching',
            #expression='weightForStitching',
            expression='getWeightForStitching(binningValue)',  # defined in '_root_macros.C'
            binning=[8E-09, 7E-08, 8E-07, 3E-06, 5E-06, 2E-05, 9E-05, 0.0006, 0.006, 0.03, 0.2, 0.9, 5, 30, 60],
        ),
        'nPU': Quantity(
            name='nPU',
            expression='nPU',
            binning=np.arange(0, 101)-0.5
        ),
        'binningValue': Quantity(
            name='binningValue',
            expression='binningValue',
            binning=_QCD_BINNING,
        ),
        'binningValue_fine': Quantity(
            name='binningValue_fine',
            expression='binningValue',
            binning=_QCD_BINNING_FINE,
        ),
    },
    'data_ak4': {
        #'activeAK4TriggerPathByPtAve': Quantity(
        #    name='activeAK4TriggerPathByPtAve',
        #    expression='getActiveAK4TriggerPathByPtAve(jet12ptave)',  # defined in '_root_macros.C'
        #    binning=np.arange(0, 30)-0.5,
        #),
        'ak4EventLuminosityWeightByPtAve_PFJetTriggers': Quantity(
            name='ak4EventLuminosityWeightByPtAve_PFJetTriggers',
            expression='getAK4EventLuminosityWeightByPtAve_PFJetTriggers(jet12ptave, hltBits)',  # defined in '_root_macros.C'
            binning=[6.65E-05, 0.0006105, 0.002157, 0.0064985, 0.046681, 0.179976, 1.4921055, 5.408151, 10.808753],
        ),
        'ak4EventLuminosityWeightByPtAve_DiPFJetAveTriggers': Quantity(
            name='ak4EventLuminosityWeightByPtAve_DiPFJetAveTriggers',
            expression='getAK4EventLuminosityWeightByPtAve_DiPFJetAveTriggers(jet12ptave, hltBits)',  # defined in '_root_macros.C'
            binning=[6.65E-05, 0.0006105, 0.002157, 0.0064985, 0.046681, 0.179976, 1.4921055, 5.408151, 10.808753],
        ),
    },
    'data_ak8': {
        #'activeAK8TriggerPathByPtAve': Quantity(
        #    name='activeAK8TriggerPathByPtAve',
        #    expression='getActiveAK8TriggerPathByPtAve(jet12ptave)',  # defined in '_root_macros.C'
        #    binning=np.arange(0, 30)-0.5,
        #),
        'ak8EventLuminosityWeightByPtAve_AK8PFJetTriggers': Quantity(
            name='ak8EventLuminosityWeightByPtAve_AK8PFJetTriggers',
            expression='getAK8EventLuminosityWeightByPtAve_AK8PFJetTriggers(jet12ptave, hltBits)',  # defined in '_root_macros.C'
            binning=[6.65E-05, 0.0006105, 0.002157, 0.0064985, 0.046681, 0.179976, 1.4921055, 5.408151, 10.808753],
        ),
        'ak8EventLuminosityWeightByPtAve_DiPFJetAveTriggers': Quantity(
            name='ak8EventLuminosityWeightByPtAve_DiPFJetAveTriggers',
            expression='getAK8EventLuminosityWeightByPtAve_DiPFJetAveTriggers(jet12ptave, hltBits)',  # defined in '_root_macros.C'
            binning=[6.65E-05, 0.0006105, 0.002157, 0.0064985, 0.046681, 0.179976, 1.4921055, 5.408151, 10.808753],
        ),
    },
}
QUANTITIES['global'].update({
    'jet1eta':          Quantity(name='jet1eta',       expression='jet1eta',       binning=QUANTITIES['global']['jet1y'].binning),
    'absjet1eta':       Quantity(name='absjet1eta',    expression='abs(jet1eta)',  binning=QUANTITIES['global']['absjet1y'].binning),
})
QUANTITIES['global'].update({
    'absjet2y':         Quantity(name='absjet2y',      expression='abs(jet2y)',    binning=QUANTITIES['global']['absjet1y'].binning),
    'absjet2eta':       Quantity(name='absjet2eta',    expression='abs(jet2eta)',  binning=QUANTITIES['global']['absjet1eta'].binning),

    'jet2pt_narrow':    Quantity(name='jet2pt_narrow', expression='jet2pt',        binning=QUANTITIES['global']['jet1pt_narrow'].binning),
    'jet2pt_wide':      Quantity(name='jet2pt_wide',   expression='jet2pt',        binning=QUANTITIES['global']['jet1pt_wide'].binning),
    'jet2phi':          Quantity(name='jet2phi',       expression='jet2phi',       binning=QUANTITIES['global']['jet1phi'].binning),
    'jet2y':            Quantity(name='jet2y',         expression='jet2y',         binning=QUANTITIES['global']['jet1y'].binning),
    'jet2eta':          Quantity(name='jet2eta',       expression='jet2eta',       binning=QUANTITIES['global']['jet1eta'].binning),
})
QUANTITIES['mc'].update({
    'jet1MatchedGenJetPt_narrow': Quantity(
        name='jet1MatchedGenJetPt_narrow',
        expression='jet1MatchedGenJetPt',
        binning=QUANTITIES['global']['jet1pt_narrow'].binning,
        named_binnings=QUANTITIES['global']['jet1pt_narrow'].named_binnings,
    ),
    'jet12MatchedGenJetPairPtAve_narrow': Quantity(
        name='jet12MatchedGenJetPairPtAve_narrow',
        expression='jet12MatchedGenJetPairPtAve',
        binning=QUANTITIES['global']['jet12ptave_narrow'].binning,
        named_binnings=QUANTITIES['global']['jet12ptave_narrow'].named_binnings,
    ),
    'jet12MatchedGenJetPairMass_narrow': Quantity(
        name='jet12MatchedGenJetPairMass_narrow',
        expression='jet12MatchedGenJetPairMass',
        binning=QUANTITIES['global']['jet12mass_narrow'].binning,
        named_binnings=QUANTITIES['global']['jet12mass_narrow'].named_binnings,
    ),

    'jet1MatchedGenJetPt_wide': Quantity(
        name='jet1MatchedGenJetPt_wide',
        expression='jet1MatchedGenJetPt',
        binning=QUANTITIES['global']['jet1pt_wide'].binning,
        named_binnings=QUANTITIES['global']['jet1pt_wide'].named_binnings,
    ),
    'jet12MatchedGenJetPairPtAve_wide': Quantity(
        name='jet12MatchedGenJetPairPtAve_wide',
        expression='jet12MatchedGenJetPairPtAve',
        binning=QUANTITIES['global']['jet12ptave_wide'].binning,
        named_binnings=QUANTITIES['global']['jet12ptave_wide'].named_binnings,
    ),
    'jet12MatchedGenJetPairMass_wide': Quantity(
        name='jet12MatchedGenJetPairMass_wide',
        expression='jet12MatchedGenJetPairMass',
        binning=QUANTITIES['global']['jet12mass_wide'].binning,
        named_binnings=QUANTITIES['global']['jet12mass_wide'].named_binnings,
    ),

    'absJet12MatchedGenJetPairYBoost': Quantity(
        name='absJet12MatchedGenJetPairYBoost',
        expression='abs(jet12MatchedGenJetPairYBoost)',
        binning=QUANTITIES['global']['yboost'].binning,
        named_binnings=QUANTITIES['global']['yboost'].named_binnings,
    ),
    'absJet12MatchedGenJetPairYStar': Quantity(
        name='absJet12MatchedGenJetPairYStar',
        expression='abs(jet12MatchedGenJetPairYStar)',
        binning=QUANTITIES['global']['ystar'].binning,
        named_binnings=QUANTITIES['global']['ystar'].named_binnings,
    ),

    'absJet12MatchedGenJetPairYBoost_wide': Quantity(
        name='absJet12MatchedGenJetPairYBoost_wide',
        expression='abs(jet12MatchedGenJetPairYBoost)',
        binning=QUANTITIES['global']['yboost_wide'].binning,
        named_binnings=QUANTITIES['global']['yboost_wide'].named_binnings,
    ),
    'absJet12MatchedGenJetPairYStar_wide': Quantity(
        name='absJet12MatchedGenJetPairYStar_wide',
        expression='abs(jet12MatchedGenJetPairYStar)',
        binning=QUANTITIES['global']['ystar_wide'].binning,
        named_binnings=QUANTITIES['global']['ystar_wide'].named_binnings,
    ),
})

# PF energy fractions
for _pf_energy_fraction in ['NeutralHadron', 'ChargedHadron', 'Muon', 'Photon', 'Electron', 'HFHadron', 'HFEM']:
    for _ijet in (1, 2):
        _qname ='jet{}{}Fraction'.format(_ijet, _pf_energy_fraction)
        QUANTITIES['global'][_qname] = Quantity(
            name=_qname,
            expression=_qname,
            binning=np.linspace(0, 1, 100),
        )

# map trigger path names to indices in analysis config (always cross-check!)
_trigger_index_map = {
    # extract HLT path bits
    "HLT_IsoMu24":        0,

    "HLT_PFJet40":        1,
    "HLT_PFJet60":        2,
    "HLT_PFJet80":        3,
    "HLT_PFJet140":       4,
    "HLT_PFJet200":       5,
    "HLT_PFJet260":       6,
    "HLT_PFJet320":       7,
    "HLT_PFJet400":       8,
    "HLT_PFJet450":       9,
    "HLT_PFJet500":      10,

    "HLT_AK8PFJet40":    11,
    "HLT_AK8PFJet60":    12,
    "HLT_AK8PFJet80":    13,
    "HLT_AK8PFJet140":   14,
    "HLT_AK8PFJet200":   15,
    "HLT_AK8PFJet260":   16,
    "HLT_AK8PFJet320":   17,
    "HLT_AK8PFJet400":   18,
    "HLT_AK8PFJet450":   19,
    "HLT_AK8PFJet500":   20,

    "HLT_DiPFJetAve40":  21,
    "HLT_DiPFJetAve60":  22,
    "HLT_DiPFJetAve80":  23,
    "HLT_DiPFJetAve140": 24,
    "HLT_DiPFJetAve200": 25,
    "HLT_DiPFJetAve260": 26,
    "HLT_DiPFJetAve320": 27,
    "HLT_DiPFJetAve400": 28,
    "HLT_DiPFJetAve500": 29,
}

DEFINES = dict()

# defines to be applied globally
DEFINES['global'] = dict()

# boolean values indicating if a particular trigger path fired for an event
DEFINES['global'].update({
    "{}".format(_trigger_name) : "(hltBits&{})>0".format(2**(_trigger_index)) for (_trigger_name, _trigger_index) in _trigger_index_map.items()
})

# boolean values indicating if the leading jet is matched to a particular trigger path
DEFINES['global'].update({
    "{}_".format(_trigger_name)+("Jet12Match" if "DiPFJetAve" in _trigger_name else "Jet1Match") : "(hlt"+("Jet12Match" if "DiPFJetAve" in _trigger_name else "Jet1Match")+"&{})>0".format(2**(_trigger_index)) for (_trigger_name, _trigger_index) in _trigger_index_map.items()
})

# boolean values indicating if the leading jet passes the L1  pT thresholds for a particular trigger path
DEFINES['global'].update({
    "{}_".format(_trigger_name)+("Jet12PtAve" if "DiPFJetAve" in _trigger_name else "Jet1Pt")+"PassThresholdsL1" : "(hlt"+("Jet12PtAve" if "DiPFJetAve" in _trigger_name else "Jet1Pt")+"PassThresholdsL1&{})>0".format(2**(_trigger_index)) for (_trigger_name, _trigger_index) in _trigger_index_map.items()
})
# boolean values indicating if the leading jet passes the HLT pT thresholds for a particular trigger path
DEFINES['global'].update({
    "{}_".format(_trigger_name)+("Jet12PtAve" if "DiPFJetAve" in _trigger_name else "Jet1Pt")+"PassThresholdsHLT" : "(hlt"+("Jet12PtAve" if "DiPFJetAve" in _trigger_name else "Jet1Pt")+"PassThresholdsHLT&{})>0".format(2**(_trigger_index)) for (_trigger_name, _trigger_index) in _trigger_index_map.items()
})

# defines to be applied for MC samples only
DEFINES['mc'] = {
    # product of all weights
    "totalWeight" : "weightForStitching*generatorWeight*pileupWeight",
    # jet flavor categories
    "Flavor_QQ":  "(abs(jet1PartonFlavor)>0)&&(abs(jet1PartonFlavor)<=5)&&(abs(jet2PartonFlavor)>0)&&(abs(jet2PartonFlavor)<=5)",
    "Flavor_QG":  "((abs(jet1PartonFlavor)>0)&&(abs(jet1PartonFlavor)<=5)&&(jet2PartonFlavor==21))||((abs(jet2PartonFlavor)>0)&&(abs(jet2PartonFlavor)<=5)&&(jet1PartonFlavor==21))",
    "Flavor_GG":  "(jet1PartonFlavor==21)&&(jet2PartonFlavor==21)",
    "Flavor_XX":  "(jet1PartonFlavor==0)||(jet2PartonFlavor==0)",

    "Flavor_aa":  "(jet1PartonFlavor<0)&&(jet2PartonFlavor<0)",
    "Flavor_pp":  "(jet1PartonFlavor>0)&&(jet2PartonFlavor>0)",
    "Flavor_ap":  "((jet1PartonFlavor>0)&&(jet2PartonFlavor<0))||((jet1PartonFlavor<0)&&(jet2PartonFlavor>0))",

    "Flavor_IsDiagonal":  "abs(jet1PartonFlavor)==abs(jet2PartonFlavor)",

    # qcd subprocess categories
    "QCDSubprocess_XX":  "(incomingParton1Flavor==0)||(incomingParton2Flavor==0)",
    "QCDSubprocess_QQ":  "(abs(incomingParton1Flavor)>0)&&(abs(incomingParton1Flavor)<=5)&&(abs(incomingParton2Flavor)>0)&&(abs(incomingParton2Flavor)<=5)",
    "QCDSubprocess_GG":  "(incomingParton1Flavor==21)&&(incomingParton2Flavor==21)",
    "QCDSubprocess_QG":  "((abs(incomingParton1Flavor)>0)&&(abs(incomingParton1Flavor)<=5)&&(incomingParton2Flavor==21))||((abs(incomingParton2Flavor)>0)&&(abs(incomingParton2Flavor)<=5)&&(incomingParton1Flavor==21))",

    "QCDSubprocess_xg_gt_xq": "((incomingParton1Flavor==21)&&(incomingParton1x>incomingParton2x))||((incomingParton2Flavor==21)&&(incomingParton2x>incomingParton1x))",

    "QCDSubprocess_aa":  "(incomingParton1Flavor<0)&&(incomingParton2Flavor<0)",
    "QCDSubprocess_pp":  "(incomingParton1Flavor>0)&&(incomingParton2Flavor>0)",
    "QCDSubprocess_ap":  "((incomingParton1Flavor>0)&&(incomingParton2Flavor<0))||((incomingParton1Flavor<0)&&(incomingParton2Flavor>0))",

    "QCDSubprocess_IsDiagonal":  "abs(incomingParton1Flavor)==abs(incomingParton2Flavor)",
}

DEFINES['data_ak4'] = {
    # product of all weights
    "totalWeight_PFJetTriggers" : "ak4EventLuminosityWeightByPtAve_PFJetTriggers",
    "totalWeight_DiPFJetAveTriggers" : "ak4EventLuminosityWeightByPtAve_DiPFJetAveTriggers",
}
DEFINES['data_ak8'] = {
    # product of all weights
    "totalWeight_PFJetTriggers" : "ak8EventLuminosityWeightByPtAve_AK8PFJetTriggers",
    "totalWeight_DiPFJetAveTriggers" : "ak8EventLuminosityWeightByPtAve_DiPFJetAveTriggers",
}

# specification of filters to be applied to data frame
SELECTIONS = {
    'jet1TriggerMatch' : [
        # leading jet has matched trigger object
        "hltJet1Match > 0",
    ],
    'recoJetPhaseSpace' : [
        # kinematics of leading jets
        "jet1pt > 100",
        "jet2pt > 50",
        "abs(jet1y) < 3.0",
        "abs(jet2y) < 3.0",
    ],
    'metSumEtFilter' : [
        # met/sumet cut (for background rejection)
        "metOverSumET < 0.3",
    ],
    'stitchingOutliersVeto' : [
        # prevent outliers in QCD MC
        'binningValue>=jet1pt/2.5'
    ],
    'npvGoodFilter' : [
        # at least one good primary vertex
        "npvGood > 0",
    ],
    'hltFilter' : [
        # at least one interesting trigger fired
        "hltBits > 0",
    ],
    'jetId' : [
        # both leading jets passed the Jet ID
        "jet1id > 0",
        "jet2id > 0",
    ],
    'genJetPhaseSpace' : [
        # kinematics of leading gen jets
        "genjet1pt > 100",
        "genjet2pt > 50",
        "abs(genjet1y) < 3.0",
        "abs(genjet2y) < 3.0",
    ],
}


# specification of ways to split sample into subsamples
SPLITTINGS = {
    # no splitting
    'none' : {
        'everything' : dict(),
    },
    # in (y_boost, y_star) bins
    'ybys' : {
        'inclusive' : dict(),
        'YB01_YS01' : dict(yboost=(0, 1), ystar=(0, 1)),
        'YB01_YS12' : dict(yboost=(0, 1), ystar=(1, 2)),
        'YB01_YS23' : dict(yboost=(0, 1), ystar=(2, 3)),
        'YB12_YS01' : dict(yboost=(1, 2), ystar=(0, 1)),
        'YB12_YS12' : dict(yboost=(1, 2), ystar=(1, 2)),
        'YB23_YS01' : dict(yboost=(2, 3), ystar=(0, 1)),
    },
    # in (y_boost, y_star) bins
    'ybys_narrow' : {
        'inclusive' : dict(),
        'YB_00_05_YS_00_05' : dict(yboost=(0.0, 0.5), ystar=(0.0, 0.5)),
        'YB_00_05_YS_05_10' : dict(yboost=(0.0, 0.5), ystar=(0.5, 1.0)),
        'YB_00_05_YS_10_15' : dict(yboost=(0.0, 0.5), ystar=(1.0, 1.5)),
        'YB_00_05_YS_15_20' : dict(yboost=(0.0, 0.5), ystar=(1.5, 2.0)),
        'YB_00_05_YS_20_25' : dict(yboost=(0.0, 0.5), ystar=(2.0, 2.5)),
        'YB_05_10_YS_00_05' : dict(yboost=(0.5, 1.0), ystar=(0.0, 0.5)),
        'YB_05_10_YS_05_10' : dict(yboost=(0.5, 1.0), ystar=(0.5, 1.0)),
        'YB_05_10_YS_10_15' : dict(yboost=(0.5, 1.0), ystar=(1.0, 1.5)),
        'YB_05_10_YS_15_20' : dict(yboost=(0.5, 1.0), ystar=(1.5, 2.0)),
        'YB_10_15_YS_00_05' : dict(yboost=(1.0, 1.5), ystar=(0.0, 0.5)),
        'YB_10_15_YS_05_10' : dict(yboost=(1.0, 1.5), ystar=(0.5, 1.0)),
        'YB_10_15_YS_10_15' : dict(yboost=(1.0, 1.5), ystar=(1.0, 1.5)),
        'YB_15_20_YS_00_05' : dict(yboost=(1.5, 2.0), ystar=(0.0, 0.5)),
        'YB_15_20_YS_05_10' : dict(yboost=(1.5, 2.0), ystar=(0.5, 1.0)),
        'YB_20_25_YS_00_05' : dict(yboost=(2.0, 2.5), ystar=(0.0, 0.5)),
    },
    # numerator/denominator selections for AK4 single-jet trigger efficiency
    'trigger_efficiencies_ak4' : {
        'all'  : dict(),
        'HLT_PFJet40_Ref'  : dict(HLT_IsoMu24=1),
        'HLT_PFJet60_Ref'  : dict(HLT_PFJet40_Jet1Match=1 ),
        'HLT_PFJet80_Ref'  : dict(HLT_PFJet60_Jet1Match=1 ),
        'HLT_PFJet140_Ref' : dict(HLT_PFJet80_Jet1Match=1 ),
        'HLT_PFJet200_Ref' : dict(HLT_PFJet140_Jet1Match=1),
        'HLT_PFJet260_Ref' : dict(HLT_PFJet200_Jet1Match=1),
        'HLT_PFJet320_Ref' : dict(HLT_PFJet260_Jet1Match=1),
        'HLT_PFJet400_Ref' : dict(HLT_PFJet320_Jet1Match=1),
        'HLT_PFJet450_Ref' : dict(HLT_PFJet400_Jet1Match=1),
        'HLT_PFJet500_Ref' : dict(HLT_PFJet450_Jet1Match=1),

        'HLT_PFJet40_Num'  : dict(HLT_IsoMu24=1,            HLT_PFJet40=1),
        'HLT_PFJet60_Num'  : dict(HLT_PFJet40_Jet1Match=1,  HLT_PFJet60_Jet1PtPassThresholdsHLT=1),
        'HLT_PFJet80_Num'  : dict(HLT_PFJet60_Jet1Match=1,  HLT_PFJet80_Jet1PtPassThresholdsHLT=1,  HLT_PFJet80_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet140_Num' : dict(HLT_PFJet80_Jet1Match=1,  HLT_PFJet140_Jet1PtPassThresholdsHLT=1, HLT_PFJet140_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet200_Num' : dict(HLT_PFJet140_Jet1Match=1, HLT_PFJet200_Jet1PtPassThresholdsHLT=1, HLT_PFJet200_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet260_Num' : dict(HLT_PFJet200_Jet1Match=1, HLT_PFJet260_Jet1PtPassThresholdsHLT=1, HLT_PFJet260_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet320_Num' : dict(HLT_PFJet260_Jet1Match=1, HLT_PFJet320_Jet1PtPassThresholdsHLT=1, HLT_PFJet320_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet400_Num' : dict(HLT_PFJet320_Jet1Match=1, HLT_PFJet400_Jet1PtPassThresholdsHLT=1, HLT_PFJet400_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet450_Num' : dict(HLT_PFJet400_Jet1Match=1, HLT_PFJet450_Jet1PtPassThresholdsHLT=1, HLT_PFJet450_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet500_Num' : dict(HLT_PFJet450_Jet1Match=1, HLT_PFJet500_Jet1PtPassThresholdsHLT=1, HLT_PFJet500_Jet1PtPassThresholdsL1=1),
    },
    # numerator/denominator selections for AK8 single-jet trigger efficiency
    'trigger_efficiencies_ak8' : {
        'all'  : dict(),
        'HLT_AK8PFJet40_Ref'  : dict(HLT_IsoMu24=1),
        'HLT_AK8PFJet60_Ref'  : dict(HLT_AK8PFJet40_Jet1Match=1),
        'HLT_AK8PFJet80_Ref'  : dict(HLT_AK8PFJet60_Jet1Match=1),
        'HLT_AK8PFJet140_Ref' : dict(HLT_AK8PFJet80_Jet1Match=1),
        'HLT_AK8PFJet200_Ref' : dict(HLT_AK8PFJet140_Jet1Match=1),
        'HLT_AK8PFJet260_Ref' : dict(HLT_AK8PFJet200_Jet1Match=1),
        'HLT_AK8PFJet320_Ref' : dict(HLT_AK8PFJet260_Jet1Match=1),
        'HLT_AK8PFJet400_Ref' : dict(HLT_AK8PFJet320_Jet1Match=1),
        'HLT_AK8PFJet450_Ref' : dict(HLT_AK8PFJet400_Jet1Match=1),
        'HLT_AK8PFJet500_Ref' : dict(HLT_AK8PFJet450_Jet1Match=1),

        'HLT_AK8PFJet40_Num'  : dict(HLT_IsoMu24=1,               HLT_AK8PFJet40=1),
        'HLT_AK8PFJet60_Num'  : dict(HLT_AK8PFJet40_Jet1Match=1,  HLT_AK8PFJet60_Jet1PtPassThresholdsHLT=1),
        'HLT_AK8PFJet80_Num'  : dict(HLT_AK8PFJet60_Jet1Match=1,  HLT_AK8PFJet80_Jet1PtPassThresholdsHLT=1,  HLT_AK8PFJet80_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet140_Num' : dict(HLT_AK8PFJet80_Jet1Match=1,  HLT_AK8PFJet140_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet140_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet200_Num' : dict(HLT_AK8PFJet140_Jet1Match=1, HLT_AK8PFJet200_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet200_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet260_Num' : dict(HLT_AK8PFJet200_Jet1Match=1, HLT_AK8PFJet260_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet260_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet320_Num' : dict(HLT_AK8PFJet260_Jet1Match=1, HLT_AK8PFJet320_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet320_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet400_Num' : dict(HLT_AK8PFJet320_Jet1Match=1, HLT_AK8PFJet400_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet400_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet450_Num' : dict(HLT_AK8PFJet400_Jet1Match=1, HLT_AK8PFJet450_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet450_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet500_Num' : dict(HLT_AK8PFJet450_Jet1Match=1, HLT_AK8PFJet500_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet500_Jet1PtPassThresholdsL1=1),
    },
    # numerator/denominator selections for dijet trigger efficiency (AK4-only)
    'trigger_efficiencies_dijet' : {
        'all'  : dict(),
        'HLT_DiPFJetAve40_Ref'  : dict(HLT_IsoMu24=1),
        'HLT_DiPFJetAve60_Ref'  : dict(HLT_DiPFJetAve40_Jet12Match=1),
        'HLT_DiPFJetAve80_Ref'  : dict(HLT_DiPFJetAve60_Jet12Match=1),
        'HLT_DiPFJetAve140_Ref' : dict(HLT_DiPFJetAve80_Jet12Match=1),
        'HLT_DiPFJetAve200_Ref' : dict(HLT_DiPFJetAve140_Jet12Match=1),
        'HLT_DiPFJetAve260_Ref' : dict(HLT_DiPFJetAve200_Jet12Match=1),
        'HLT_DiPFJetAve320_Ref' : dict(HLT_DiPFJetAve260_Jet12Match=1),
        'HLT_DiPFJetAve400_Ref' : dict(HLT_DiPFJetAve320_Jet12Match=1),
        'HLT_DiPFJetAve500_Ref' : dict(HLT_DiPFJetAve400_Jet12Match=1),

        'HLT_DiPFJetAve40_Num'  : dict(HLT_IsoMu24=1,                  HLT_DiPFJetAve40=1),
        'HLT_DiPFJetAve60_Num'  : dict(HLT_DiPFJetAve40_Jet12Match=1,  HLT_DiPFJetAve60_Jet12PtAvePassThresholdsHLT=1),
        'HLT_DiPFJetAve80_Num'  : dict(HLT_DiPFJetAve60_Jet12Match=1,  HLT_DiPFJetAve80_Jet12PtAvePassThresholdsHLT=1),
        'HLT_DiPFJetAve140_Num' : dict(HLT_DiPFJetAve80_Jet12Match=1,  HLT_DiPFJetAve140_Jet12PtAvePassThresholdsHLT=1, HLT_DiPFJetAve140_Jet12PtAvePassThresholdsL1=1),
        'HLT_DiPFJetAve200_Num' : dict(HLT_DiPFJetAve140_Jet12Match=1, HLT_DiPFJetAve200_Jet12PtAvePassThresholdsHLT=1, HLT_DiPFJetAve200_Jet12PtAvePassThresholdsL1=1),
        'HLT_DiPFJetAve260_Num' : dict(HLT_DiPFJetAve200_Jet12Match=1, HLT_DiPFJetAve260_Jet12PtAvePassThresholdsHLT=1, HLT_DiPFJetAve260_Jet12PtAvePassThresholdsL1=1),
        'HLT_DiPFJetAve320_Num' : dict(HLT_DiPFJetAve260_Jet12Match=1, HLT_DiPFJetAve320_Jet12PtAvePassThresholdsHLT=1, HLT_DiPFJetAve320_Jet12PtAvePassThresholdsL1=1),
        'HLT_DiPFJetAve400_Num' : dict(HLT_DiPFJetAve320_Jet12Match=1, HLT_DiPFJetAve400_Jet12PtAvePassThresholdsHLT=1, HLT_DiPFJetAve400_Jet12PtAvePassThresholdsL1=1),
        'HLT_DiPFJetAve500_Num' : dict(HLT_DiPFJetAve400_Jet12Match=1, HLT_DiPFJetAve500_Jet12PtAvePassThresholdsHLT=1, HLT_DiPFJetAve500_Jet12PtAvePassThresholdsL1=1),
    },
    # numerator/denominator selections for AK4 single-jet trigger efficiency
    'trigger_efficiencies_ak4_nomatch' : {
        'all'  : dict(),
        'HLT_PFJet40_Ref'  : dict(HLT_IsoMu24=1),
        'HLT_PFJet60_Ref'  : dict(HLT_PFJet40=1 ),
        'HLT_PFJet80_Ref'  : dict(HLT_PFJet60=1 ),
        'HLT_PFJet140_Ref' : dict(HLT_PFJet80=1 ),
        'HLT_PFJet200_Ref' : dict(HLT_PFJet140=1),
        'HLT_PFJet260_Ref' : dict(HLT_PFJet200=1),
        'HLT_PFJet320_Ref' : dict(HLT_PFJet260=1),
        'HLT_PFJet400_Ref' : dict(HLT_PFJet320=1),
        'HLT_PFJet450_Ref' : dict(HLT_PFJet400=1),
        'HLT_PFJet500_Ref' : dict(HLT_PFJet450=1),

        'HLT_PFJet40_Num'  : dict(HLT_IsoMu24=1,  HLT_PFJet40=1),
        'HLT_PFJet60_Num'  : dict(HLT_PFJet40=1,  HLT_PFJet60_Jet1PtPassThresholdsHLT=1),
        'HLT_PFJet80_Num'  : dict(HLT_PFJet60=1,  HLT_PFJet80_Jet1PtPassThresholdsHLT=1,  HLT_PFJet80_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet140_Num' : dict(HLT_PFJet80=1,  HLT_PFJet140_Jet1PtPassThresholdsHLT=1, HLT_PFJet140_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet200_Num' : dict(HLT_PFJet140=1, HLT_PFJet200_Jet1PtPassThresholdsHLT=1, HLT_PFJet200_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet260_Num' : dict(HLT_PFJet200=1, HLT_PFJet260_Jet1PtPassThresholdsHLT=1, HLT_PFJet260_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet320_Num' : dict(HLT_PFJet260=1, HLT_PFJet320_Jet1PtPassThresholdsHLT=1, HLT_PFJet320_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet400_Num' : dict(HLT_PFJet320=1, HLT_PFJet400_Jet1PtPassThresholdsHLT=1, HLT_PFJet400_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet450_Num' : dict(HLT_PFJet400=1, HLT_PFJet450_Jet1PtPassThresholdsHLT=1, HLT_PFJet450_Jet1PtPassThresholdsL1=1),
        'HLT_PFJet500_Num' : dict(HLT_PFJet450=1, HLT_PFJet500_Jet1PtPassThresholdsHLT=1, HLT_PFJet500_Jet1PtPassThresholdsL1=1),
    },
    # numerator/denominator selections for AK8 single-jet trigger efficiency
    'trigger_efficiencies_ak8_nomatch' : {
        'all'  : dict(),
        'HLT_AK8PFJet40_Ref'  : dict(HLT_IsoMu24=1),
        'HLT_AK8PFJet60_Ref'  : dict(HLT_AK8PFJet40=1),
        'HLT_AK8PFJet80_Ref'  : dict(HLT_AK8PFJet60=1),
        'HLT_AK8PFJet140_Ref' : dict(HLT_AK8PFJet80=1),
        'HLT_AK8PFJet200_Ref' : dict(HLT_AK8PFJet140=1),
        'HLT_AK8PFJet260_Ref' : dict(HLT_AK8PFJet200=1),
        'HLT_AK8PFJet320_Ref' : dict(HLT_AK8PFJet260=1),
        'HLT_AK8PFJet400_Ref' : dict(HLT_AK8PFJet320=1),
        'HLT_AK8PFJet450_Ref' : dict(HLT_AK8PFJet400=1),
        'HLT_AK8PFJet500_Ref' : dict(HLT_AK8PFJet450=1),

        'HLT_AK8PFJet40_Num'  : dict(HLT_IsoMu24=1,     HLT_AK8PFJet40=1),
        'HLT_AK8PFJet60_Num'  : dict(HLT_AK8PFJet40=1,  HLT_AK8PFJet60_Jet1PtPassThresholdsHLT=1),
        'HLT_AK8PFJet80_Num'  : dict(HLT_AK8PFJet60=1,  HLT_AK8PFJet80_Jet1PtPassThresholdsHLT=1,  HLT_AK8PFJet80_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet140_Num' : dict(HLT_AK8PFJet80=1,  HLT_AK8PFJet140_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet140_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet200_Num' : dict(HLT_AK8PFJet140=1, HLT_AK8PFJet200_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet200_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet260_Num' : dict(HLT_AK8PFJet200=1, HLT_AK8PFJet260_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet260_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet320_Num' : dict(HLT_AK8PFJet260=1, HLT_AK8PFJet320_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet320_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet400_Num' : dict(HLT_AK8PFJet320=1, HLT_AK8PFJet400_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet400_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet450_Num' : dict(HLT_AK8PFJet400=1, HLT_AK8PFJet450_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet450_Jet1PtPassThresholdsL1=1),
        'HLT_AK8PFJet500_Num' : dict(HLT_AK8PFJet450=1, HLT_AK8PFJet500_Jet1PtPassThresholdsHLT=1, HLT_AK8PFJet500_Jet1PtPassThresholdsL1=1),
    },
    # numerator/denominator selections for dijet trigger efficiency (AK4-only)
    'trigger_efficiencies_dijet_nomatch' : {
        'all'  : dict(),
        'HLT_DiPFJetAve40_Ref'  : dict(HLT_IsoMu24=1),
        'HLT_DiPFJetAve60_Ref'  : dict(HLT_DiPFJetAve40=1),
        'HLT_DiPFJetAve80_Ref'  : dict(HLT_DiPFJetAve60=1),
        'HLT_DiPFJetAve140_Ref' : dict(HLT_DiPFJetAve80=1),
        'HLT_DiPFJetAve200_Ref' : dict(HLT_DiPFJetAve140=1),
        'HLT_DiPFJetAve260_Ref' : dict(HLT_DiPFJetAve200=1),
        'HLT_DiPFJetAve320_Ref' : dict(HLT_DiPFJetAve260=1),
        'HLT_DiPFJetAve400_Ref' : dict(HLT_DiPFJetAve320=1),
        'HLT_DiPFJetAve500_Ref' : dict(HLT_DiPFJetAve400=1),

        'HLT_DiPFJetAve40_Num'  : dict(HLT_IsoMu24=1,       HLT_DiPFJetAve40=1),
        'HLT_DiPFJetAve60_Num'  : dict(HLT_DiPFJetAve40=1,  HLT_DiPFJetAve60_Jet12PtAvePassThresholdsHLT=1),
        'HLT_DiPFJetAve80_Num'  : dict(HLT_DiPFJetAve60=1,  HLT_DiPFJetAve80_Jet12PtAvePassThresholdsHLT=1),
        'HLT_DiPFJetAve140_Num' : dict(HLT_DiPFJetAve80=1,  HLT_DiPFJetAve140_Jet12PtAvePassThresholdsHLT=1, HLT_DiPFJetAve140_Jet12PtAvePassThresholdsL1=1),
        'HLT_DiPFJetAve200_Num' : dict(HLT_DiPFJetAve140=1, HLT_DiPFJetAve200_Jet12PtAvePassThresholdsHLT=1, HLT_DiPFJetAve200_Jet12PtAvePassThresholdsL1=1),
        'HLT_DiPFJetAve260_Num' : dict(HLT_DiPFJetAve200=1, HLT_DiPFJetAve260_Jet12PtAvePassThresholdsHLT=1, HLT_DiPFJetAve260_Jet12PtAvePassThresholdsL1=1),
        'HLT_DiPFJetAve320_Num' : dict(HLT_DiPFJetAve260=1, HLT_DiPFJetAve320_Jet12PtAvePassThresholdsHLT=1, HLT_DiPFJetAve320_Jet12PtAvePassThresholdsL1=1),
        'HLT_DiPFJetAve400_Num' : dict(HLT_DiPFJetAve320=1, HLT_DiPFJetAve400_Jet12PtAvePassThresholdsHLT=1, HLT_DiPFJetAve400_Jet12PtAvePassThresholdsL1=1),
        'HLT_DiPFJetAve500_Num' : dict(HLT_DiPFJetAve400=1, HLT_DiPFJetAve500_Jet12PtAvePassThresholdsHLT=1, HLT_DiPFJetAve500_Jet12PtAvePassThresholdsL1=1),
    },
    # by AK4 single-jet trigger path (with overlap)
    'triggers_ak4' : {
        'all' : dict(),
        'HLT_PFJet40'  : dict(HLT_PFJet40=1),
        'HLT_PFJet60'  : dict(HLT_PFJet60=1),
        'HLT_PFJet80'  : dict(HLT_PFJet80=1),
        'HLT_PFJet140' : dict(HLT_PFJet140=1),
        'HLT_PFJet200' : dict(HLT_PFJet200=1),
        'HLT_PFJet260' : dict(HLT_PFJet260=1),
        'HLT_PFJet320' : dict(HLT_PFJet320=1),
        'HLT_PFJet400' : dict(HLT_PFJet400=1),
        'HLT_PFJet450' : dict(HLT_PFJet450=1),
        'HLT_PFJet500' : dict(HLT_PFJet500=1),
    },
    # by AK8 single-jet trigger path (with overlap)
    'triggers_ak8' : {
        'all' : dict(),
        'HLT_AK8PFJet40'  : dict(HLT_AK8PFJet40=1),
        'HLT_AK8PFJet60'  : dict(HLT_AK8PFJet60=1),
        'HLT_AK8PFJet80'  : dict(HLT_AK8PFJet80=1),
        'HLT_AK8PFJet140' : dict(HLT_AK8PFJet140=1),
        'HLT_AK8PFJet200' : dict(HLT_AK8PFJet200=1),
        'HLT_AK8PFJet260' : dict(HLT_AK8PFJet260=1),
        'HLT_AK8PFJet320' : dict(HLT_AK8PFJet320=1),
        'HLT_AK8PFJet400' : dict(HLT_AK8PFJet400=1),
        'HLT_AK8PFJet450' : dict(HLT_AK8PFJet450=1),
        'HLT_AK8PFJet500' : dict(HLT_AK8PFJet500=1),
    },
    # by dijet trigger path (with overlap)
    'triggers_dijet' : {
        'all' : dict(),
        'HLT_DiPFJetAve40'  : dict(HLT_DiPFJetAve40=1),
        'HLT_DiPFJetAve60'  : dict(HLT_DiPFJetAve60=1),
        'HLT_DiPFJetAve80'  : dict(HLT_DiPFJetAve80=1),
        'HLT_DiPFJetAve140' : dict(HLT_DiPFJetAve140=1),
        'HLT_DiPFJetAve200' : dict(HLT_DiPFJetAve200=1),
        'HLT_DiPFJetAve260' : dict(HLT_DiPFJetAve260=1),
        'HLT_DiPFJetAve320' : dict(HLT_DiPFJetAve320=1),
        'HLT_DiPFJetAve400' : dict(HLT_DiPFJetAve400=1),
        'HLT_DiPFJetAve500' : dict(HLT_DiPFJetAve500=1),
    },
    # by flavor category
    'flavors' : {
        "Flavor_AllDefined":  dict(Flavor_XX=0),  # any flavor pairing, but need to be defined for both jets
        "Flavor_XX":   dict(Flavor_XX=1),  # undefined
        "Flavor_GG":   dict(Flavor_GG=1),  # gluon-gluon
        "Flavor_QG":   dict(Flavor_QG=1),  # quark-gluon (and gluon-quark)
        # quark-quark subcategories
        "Flavor_QQ_aa_ii":   dict(Flavor_QQ=1, Flavor_aa=1, Flavor_IsDiagonal=1),
        "Flavor_QQ_aa_ij":   dict(Flavor_QQ=1, Flavor_aa=1, Flavor_IsDiagonal=0),
        "Flavor_QQ_ap_ii":   dict(Flavor_QQ=1, Flavor_ap=1, Flavor_IsDiagonal=1),
        "Flavor_QQ_ap_ij":   dict(Flavor_QQ=1, Flavor_ap=1, Flavor_IsDiagonal=0),
        "Flavor_QQ_pp_ii":   dict(Flavor_QQ=1, Flavor_pp=1, Flavor_IsDiagonal=1),
        "Flavor_QQ_pp_ij":   dict(Flavor_QQ=1, Flavor_pp=1, Flavor_IsDiagonal=0),
    },
    # by QCD subprocess
    'qcd_subprocesses' : {
        "QCDSubprocess_AllDefined":  dict(QCDSubprocess_XX=0),  # any flavor pairing, but need to be defined for both incoming partons
        "QCDSubprocess_GG":   dict(QCDSubprocess_GG=1),  # gluon-gluon
        "QCDSubprocess_QG":   dict(QCDSubprocess_QG=1),  # quark-gluon (and gluon-quark)
        "QCDSubprocess_QG_xg_gt_xq":   dict(QCDSubprocess_QG=1, QCDSubprocess_xg_gt_xq=1),  # quark-gluon (and gluon-quark)
        "QCDSubprocess_QG_xq_gt_xg":   dict(QCDSubprocess_QG=1, QCDSubprocess_xg_gt_xq=0),  # quark-gluon (and gluon-quark)
        # quark-quark subcategories
        "QCDSubprocess_QQ_aa_ii":   dict(QCDSubprocess_QQ=1, QCDSubprocess_aa=1, QCDSubprocess_IsDiagonal=1),
        "QCDSubprocess_QQ_aa_ij":   dict(QCDSubprocess_QQ=1, QCDSubprocess_aa=1, QCDSubprocess_IsDiagonal=0),
        "QCDSubprocess_QQ_ap_ii":   dict(QCDSubprocess_QQ=1, QCDSubprocess_ap=1, QCDSubprocess_IsDiagonal=1),
        "QCDSubprocess_QQ_ap_ij":   dict(QCDSubprocess_QQ=1, QCDSubprocess_ap=1, QCDSubprocess_IsDiagonal=0),
        "QCDSubprocess_QQ_pp_ii":   dict(QCDSubprocess_QQ=1, QCDSubprocess_pp=1, QCDSubprocess_IsDiagonal=1),
        "QCDSubprocess_QQ_pp_ij":   dict(QCDSubprocess_QQ=1, QCDSubprocess_pp=1, QCDSubprocess_IsDiagonal=0),
    },
    # by MC subsample
    'mc_subsamples' : {
        "QCD_Pt_3200toInf"  : dict(weightForStitching=( 2E-10 , 8E-09 )),
        "QCD_Pt_2400to3200" : dict(weightForStitching=( 8E-09 , 7E-08 )),
        "QCD_Pt_1800to2400" : dict(weightForStitching=( 7E-08 , 8E-07 )),
        "QCD_Pt_1400to1800" : dict(weightForStitching=( 8E-07 , 3E-06 )),
        "QCD_Pt_1000to1400" : dict(weightForStitching=( 3E-06 , 5E-06 )),
        "QCD_Pt_800to1000"  : dict(weightForStitching=( 5E-06 , 2E-05 )),
        "QCD_Pt_600to800"   : dict(weightForStitching=( 2E-05 , 9E-05 )),
        "QCD_Pt_470to600"   : dict(weightForStitching=( 9E-05 , 0.0006)),
        "QCD_Pt_300to470"   : dict(weightForStitching=( 0.0006, 0.006 )),
        "QCD_Pt_170to300"   : dict(weightForStitching=( 0.006 , 0.03  )),
        "QCD_Pt_120to170"   : dict(weightForStitching=( 0.03  , 0.2   )),
        "QCD_Pt_80to120"    : dict(weightForStitching=( 0.2   , 0.9   )),
        "QCD_Pt_50to80"     : dict(weightForStitching=( 0.9   , 5     )),
        "QCD_Pt_30to50"     : dict(weightForStitching=( 5     , 30    )),
        "QCD_Pt_15to30"     : dict(weightForStitching=( 30    , 60    )),
        "stitched"          : dict(),
    }
}
