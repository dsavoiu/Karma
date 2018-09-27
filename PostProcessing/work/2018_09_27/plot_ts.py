#!/usr/bin/env python
import argparse
import datetime
import itertools

#from DijetAnalysis.PostProcessing.PP import SPLITTINGS
from DijetAnalysis.PostProcessing.Plotting import Plotter, ContextValue, LiteralString


SAMPLE_LABEL = "Run2016G, 13 TeV"
SAMPLE_LUMINOSITY = 7540487746.602

PLOT_CONFIG = {
    'input_files': {
        'ts' : "TriggerShapes_2018-09-27.root",
    },
    'figures': [
        {
            'filename' : "TriggerShapes/{quantity[name]}.png",
            'subplots' : [
                dict(expression='"ts:all/{quantity[name]}"', label='' , color='k', plot_method='errorbar', marker='o', marker_style='full'),
                #dict(expression='"ts:HLT_PFJet40/{quantity[name]}" ', label='PFJet40' , color='#1b09aa', plot_method='errorbar', marker='o', marker_style='full'),
                #dict(expression='"ts:HLT_PFJet60/{quantity[name]}" ', label='PFJet60' , color='#094aaa', plot_method='errorbar', marker='D', marker_style='full'),
                #dict(expression='"ts:HLT_PFJet80/{quantity[name]}" ', label='PFJet80' , color='#0bd1d1', plot_method='errorbar', marker='v', marker_style='full'),
                #dict(expression='"ts:HLT_PFJet140/{quantity[name]}"', label='PFJet140', color='#0ce41f', plot_method='errorbar', marker='^', marker_style='full'),
                #dict(expression='"ts:HLT_PFJet200/{quantity[name]}"', label='PFJet200', color='#dee40c', plot_method='errorbar', marker='s', marker_style='full'),
                #dict(expression='"ts:HLT_PFJet260/{quantity[name]}"', label='PFJet260', color='#e4ac0c', plot_method='errorbar', marker='>', marker_style='full'),
                #dict(expression='"ts:HLT_PFJet320/{quantity[name]}"', label='PFJet320', color='#ed690c', plot_method='errorbar', marker='o', marker_style='full'),
                #dict(expression='"ts:HLT_PFJet400/{quantity[name]}"', label='PFJet400', color='#ed360c', plot_method='errorbar', marker='x', marker_style='empty'),
                #dict(expression='"ts:HLT_PFJet450/{quantity[name]}"', label='PFJet450', color='#d1110b', plot_method='errorbar', marker='d', marker_style='full'),
                #dict(expression='"ts:HLT_PFJet500/{quantity[name]}"', label='PFJet500', color='#a52509', plot_method='errorbar', marker='s', marker_style='full'),
            ],
            'x_label' : '{quantity[label]}',
            'x_range' : ContextValue('quantity[x_range]'),
            'x_scale' : '{quantity[x_scale]}',
            'y_label' : r'Event yield',
            'y_scale' : 'linear',
            'upper_label': LiteralString(r"$\mathcal{{L}}\,=\,{:.2f}\,\,\mathrm{{fb}}^{{-1}}$ ({})".format(SAMPLE_LUMINOSITY/1e9, SAMPLE_LABEL)),
        },
        {
            'filename' : "TriggerShapeRatios/{quantity[name]}.png",
            'subplots' : [
                dict(expression='"ts:HLT_PFJet40/{quantity[name]}"  / "ts:all/{quantity[name]}"', label='PFJet40' , color='#1b09aa', plot_method='bar', stack='all', show_yerr=False),
                dict(expression='"ts:HLT_PFJet60/{quantity[name]}"  / "ts:all/{quantity[name]}"', label='PFJet60' , color='#094aaa', plot_method='bar', stack='all', show_yerr=False),
                dict(expression='"ts:HLT_PFJet80/{quantity[name]}"  / "ts:all/{quantity[name]}"', label='PFJet80' , color='#0bd1d1', plot_method='bar', stack='all', show_yerr=False),
                dict(expression='"ts:HLT_PFJet140/{quantity[name]}" / "ts:all/{quantity[name]}"', label='PFJet140', color='#0ce41f', plot_method='bar', stack='all', show_yerr=False),
                dict(expression='"ts:HLT_PFJet200/{quantity[name]}" / "ts:all/{quantity[name]}"', label='PFJet200', color='#dee40c', plot_method='bar', stack='all', show_yerr=False),
                dict(expression='"ts:HLT_PFJet260/{quantity[name]}" / "ts:all/{quantity[name]}"', label='PFJet260', color='#e4ac0c', plot_method='bar', stack='all', show_yerr=False),
                dict(expression='"ts:HLT_PFJet320/{quantity[name]}" / "ts:all/{quantity[name]}"', label='PFJet320', color='#ed690c', plot_method='bar', stack='all', show_yerr=False),
                dict(expression='"ts:HLT_PFJet400/{quantity[name]}" / "ts:all/{quantity[name]}"', label='PFJet400', color='#ed360c', plot_method='bar', stack='all', show_yerr=False),
                dict(expression='"ts:HLT_PFJet450/{quantity[name]}" / "ts:all/{quantity[name]}"', label='PFJet450', color='#d1110b', plot_method='bar', stack='all', show_yerr=False),
                dict(expression='"ts:HLT_PFJet500/{quantity[name]}" / "ts:all/{quantity[name]}"', label='PFJet500', color='#a52509', plot_method='bar', stack='all', show_yerr=False),
            ],
            'x_label' : '{quantity[label]}',
            'x_range' : ContextValue('quantity[x_range]'),
            'x_scale' : '{quantity[x_scale]}',
            'y_label' : r'Fraction of total event number',
            'y_scale' : 'linear',
            'upper_label': LiteralString(r"$\mathcal{{L}}\,=\,{:.2f}\,\,\mathrm{{fb}}^{{-1}}$ ({})".format(SAMPLE_LUMINOSITY/1e9, SAMPLE_LABEL)),
        },
    ],
    'expansions' : {
        'quantity' : [
            {
                "name": "jet1HLTAssignedPathIndex",
                "label": r"Jet 1 matched HLT path index",
                "x_scale": "linear",
                'x_range' : None,
            },
            {
                "name": "jet2HLTAssignedPathIndex",
                "label": r"Jet 2 matched HLT path index",
                "x_scale": "linear",
                'x_range' : None,
            },
            {
                "name": "jet1HLTAssignedPathEfficiency",
                "label": r"Jet 1 matched HLT path efficiency",
                "x_scale": "linear",
                'x_range' : (0, 1),
            },
            {
                "name": "jet2HLTAssignedPathEfficiency",
                "label": r"Jet 2 matched HLT path efficiency",
                "x_scale": "linear",
                'x_range' : (0, 1),
            },
            {
                "name": "jet1HLTAssignedPathPrescale",
                "label": r"Jet 1 matched HLT path prescale",
                "x_scale": "linear",
                'x_range' : None,
            },
            {
                "name": "jet2HLTAssignedPathPrescale",
                "label": r"Jet 2 matched HLT path prescale",
                "x_scale": "linear",
                'x_range' : None,
            },
        ]
    }
}



if __name__ == "__main__":
    
    ap = argparse.ArgumentParser()

    ap.add_argument('--output-folder', help="Output folder in which to place the plots produced", default=None)

    args = ap.parse_args()

    if args.output_folder is None:
        args.output_folder = "plots_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f"))


    p = Plotter(PLOT_CONFIG, output_folder=args.output_folder)
    p.run()
