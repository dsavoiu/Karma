EXPANSIONS = {
    'quantity' : [
        {
            "name": "jet1pt",
            "label": r"${p_{\mathrm{T}}^{\mathrm{jet1}}}$ /  GeV",
            "scale": "log",
            'range' : (60, 4827),
            'xs_range': (1e-10, 1e10),
            'xs_label': r"Diff. cross section $\frac{{\mathrm{{d}}^3\sigma}}{{\mathrm{{d}}{{{}}}\,\mathrm{{d}}y_{{\mathrm{{b}}}}\,\mathrm{{d}}y*}}\,\,/\,\,\mathrm{{pb}}\,\mathrm{{GeV}}^{{-1}}$".format(r"{p_{\mathrm{T}}^{\mathrm{jet1}}}")

        },
        {
            "name": "metOverSumET",
            "label": r"${E_{\mathrm{T}}^{\mathrm{miss}}}/\sum{|E_{\mathrm{T}}^{\mathrm{miss}}|}$",
            "scale": "linear",
            'range' : (0, 1),
            'xs_range': None,
            'xs_label': "Diff. cross section / pb",
        },
        {
            "name": "jet12ptave",
            "label": r"${\langle p_{\mathrm{T}} \rangle}_{1,2}$ / GeV",
            "scale": "log",
            'range' : (100, 4045),
            'xs_range': (1e-10, 1e10),
            'xs_label': r"Diff. cross section $\frac{{\mathrm{{d}}^3\sigma}}{{\mathrm{{d}}{{{}}}\,\mathrm{{d}}y_{{\mathrm{{b}}}}\,\mathrm{{d}}y*}}\,\,/\,\,\mathrm{{pb}}\,\mathrm{{GeV}}^{{-1}}$".format(r"{\langle p_{\mathrm{T}} \rangle}_{1,2}")
        },
        {
            "name": "jet12mass",
            "label": r"${m_{\mathrm{jj}}}$ / GeV",
            "scale": "log",
            'range' : (200, 9607),
            'xs_range': (1e-9, 1e10),
            'xs_label': r"Diff. cross section $\frac{{\mathrm{{d}}^3\sigma}}{{\mathrm{{d}}{{{}}}\,\mathrm{{d}}y_{{\mathrm{{b}}}}\,\mathrm{{d}}y*}}\,\,/\,\,\mathrm{{pb}}\,\mathrm{{GeV}}^{{-1}}$".format(r"{m_{\mathrm{jj}}}")
        },
        {
            "name": "jet1phi",
            "label": r"${\phi^{\mathrm{jet1}}}$",
            "scale": "linear",
            'range' : (-3.2, 3.2),
            'xs_range': None,
            'xs_label': "Cross section / pb",
        },
    ],
    'ybys' : [
        {
            "name": "YB01_YS01",
            "label": r"YB01_YS01",
            "color": "royalblue",
            "marker": "D",
            "marker_style": "full",
            "stagger_factor": 1e4,
        },
        {
            "name": "YB01_YS12",
            "label": r"YB01_YS12",
            "color": "forestgreen",
            "marker": "v",
            "marker_style": "full",
            "stagger_factor": 1e3,
        },
        {
            "name": "YB01_YS23",
            "label": r"YB01_YS23",
            "color": "darkred",
            "marker": "^",
            "marker_style": "full",
            "stagger_factor": 1e-1,
        },
        {
            "name": "YB12_YS01",
            "label": r"YB12_YS01",
            "color": "darkorchid",
            "marker": "s",
            "marker_style": "full",
            "stagger_factor": 1e1,
        },
        {
            "name": "YB12_YS12",
            "label": r"YB12_YS12",
            "color": "orange",
            "marker": ">",
            "marker_style": "full",
            "stagger_factor": 1e0,
        },
        {
            "name": "YB23_YS01",
            "label": r"YB23_YS01",
            "color": "darkturquoise",
            "marker": "o",
            "marker_style": "full",
            "stagger_factor": 1e-3,
        },
        {
            "name": "inclusive",
            "label": r"inclusive",
            "color": "k",
            "marker": "o",
            "marker_style": "empty",
            "stagger_factor": 1e0,
        },
    ],
    'trigger' : [
        {
            "name": "HLT_PFJet40",
            "label": r"PFJet40",
            "color": "#1b09aa",
            "marker": "o",
            'marker_style': 'full',
            'l1_factor': 10000.0,
            'lumi_ub': 48714.091,  # Run2016G
        },
        {
            "name": "HLT_PFJet60",
            "label": r"PFJet60",
            "color": "#094aaa",
            "marker": "D",
            'marker_style': 'full',
            'l1_factor': 1000.0,
            'lumi_ub': 123328.102,  # Run2016G
        },
        {
            "name": "HLT_PFJet80",
            "label": r"PFJet80",
            "color": "#0bd1d1",
            "marker": "v",
            'marker_style': 'full',
            'l1_factor': 1000.0,
            'lumi_ub': 369296.644,  # Run2016G
        },
        {
            "name": "HLT_PFJet140",
            "label": r"PFJet140",
            "color": "#0ce41f",
            "marker": "^",
            'marker_style': 'full',
            'l1_factor': 1000.0,
            'lumi_ub': 3618461.972,  # Run2016G
        },
        {
            "name": "HLT_PFJet200",
            "label": r"PFJet200",
            "color": "#dee40c",
            "marker": "s",
            'marker_style': 'full',
            'l1_factor': 100.0,
            'lumi_ub': 11962959.393,  # Run2016G
        },
        {
            "name": "HLT_PFJet260",
            "label": r"PFJet260",
            "color": "#e4ac0c",
            "marker": ">",
            'marker_style': 'full',
            'l1_factor': 1.0,
            'lumi_ub': 102345547.894,  # Run2016G
        },
        {
            "name": "HLT_PFJet320",
            "label": r"PFJet320",
            "color": "#ed690c",
            "marker": "o",
            'marker_style': 'full',
            'l1_factor': 1.0,
            'lumi_ub': 310001081.812,  # Run2016G
        },
        {
            "name": "HLT_PFJet400",
            "label": r"PFJet400",
            "color": "#ed360c",
            "marker": "x",
            'marker_style': 'empty',
            'l1_factor': 1.0,
            'lumi_ub': 918960478.743,  # Run2016G
        },
        {
            "name": "HLT_PFJet450",
            "label": r"PFJet450",
            "color": "#d1110b",
            "marker": "d",
            'marker_style': 'full',
            'l1_factor': 1.0,
            'lumi_ub': 7544015569.439,  # Run2016G
        },
        {
            "name": "HLT_PFJet500",
            "label": r"PFJet500",
            "color": "#a52509",
            "marker": "s",
            'marker_style': 'full',
            'l1_factor': 1.0,
            'lumi_ub': 7544015569.439,  # Run2016G
        },
        {
            "name": "all",
            "label": r"all triggers",
            "color": "k",
            "marker": "o",
            'marker_style': 'empty',
            'l1_factor': 1.0,
            'lumi_ub': 7544015569.439,  # Run2016G
        },
    ]
}
