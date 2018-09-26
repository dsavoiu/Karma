import itertools

from DijetAnalysis.PostProcessing.Plotting import Plotter, ContextValue, LiteralString



_weightstring = []
for _tp in (40, 60, 80, 140, 200, 260, 320, 400, 450, 500):
    _tp_name = "HLT_PFJet{}".format(_tp)
    #_weightstring.append('("tc:{tp_name}/{{quantity[name]}}" / "tc:all/{{quantity[name]}}" * "te:{tp_name}/{{quantity[name]}}")'.format(tp_name=_tp_name))
    #_weightstring.append('("tc:{tp_name}/{{quantity[name]}}" / "tc:all/{{quantity[name]}}" * "te:{tp_name}/{{quantity[name]}}" / "tp:{tp_name}/{{quantity[name]}}")'.format(tp_name=_tp_name))
    _weightstring.append('(("tc:{tp_name}/{{quantity[name]}}" / "tc:all/{{quantity[name]}}") * nanguard_zero("tp:{tp_name}/{{quantity[name]}}"/"te:{tp_name}/{{quantity[name]}}"))'.format(tp_name=_tp_name))
    #_weightstring.append('"tc:{tp_name}/{{quantity[name]}}" * (1.0 - "te:{tp_name}/{{quantity[name]}}") / "tc:all/{{quantity[name]}}"'.format(tp_name=_tp_name))
    #_weightstring.append('(1.0 - ("te:{tp_name}/{{quantity[name]}}"/"tp:{tp_name}/{{quantity[name]}}"))'.format(tp_name=_tp_name))
#_weightstring = '(1.0 - ({}))'.format(" * ".join(_weightstring))
_weightstring = '({})'.format(" + ".join(_weightstring))


SAMPLE_LABEL = "Run2016G, 13 TeV"
SAMPLE_LUMINOSITY = 7540487746.602


PLOT_CONFIG = {
    'input_files': {
        'tc' : "/portal/ekpbms1/home/dsavoiu/Dijet/CMSSW_10_0_2_dijetAnalysisCMSSW/src/DijetAnalysis/PostProcessing/test/CrossSection/testPP_TriggerComposition_v3_binning.root",
        'te' : "/portal/ekpbms1/home/dsavoiu/Dijet/CMSSW_10_0_2_dijetAnalysisCMSSW/src/DijetAnalysis/PostProcessing/test/CrossSection/testPP_TriggerEfficiencies_v4_binning.root",
        'tp' : "/portal/ekpbms1/home/dsavoiu/Dijet/CMSSW_10_0_2_dijetAnalysisCMSSW/src/DijetAnalysis/PostProcessing/test/CrossSection/testPP_TriggerPrescales_v4_binning.root",
        'xs' : "/portal/ekpbms1/home/dsavoiu/Dijet/CMSSW_10_0_2_dijetAnalysisCMSSW/src/DijetAnalysis/PostProcessing/test/CrossSection/testPP_CrossSection_v4_binning.root",
    },
    'figures': [
        #{
        #    'filename' : "fig_TriggerEfficiencies_{quantity[name]}.png",
        #    'subplots' : [
        #        dict(expression='"te:HLT_PFJet40/{quantity[name]}"' , label='PFJet40' , color='#1b09aa', marker='o', marker_style='full'),
        #        dict(expression='"te:HLT_PFJet60/{quantity[name]}"' , label='PFJet60' , color='#094aaa', marker='D', marker_style='full'),
        #        dict(expression='"te:HLT_PFJet80/{quantity[name]}"' , label='PFJet80' , color='#0bd1d1', marker='v', marker_style='full'),
        #        dict(expression='"te:HLT_PFJet140/{quantity[name]}"', label='PFJet140', color='#0ce41f', marker='^', marker_style='full'),
        #        dict(expression='"te:HLT_PFJet200/{quantity[name]}"', label='PFJet200', color='#dee40c', marker='s', marker_style='full'),
        #        dict(expression='"te:HLT_PFJet260/{quantity[name]}"', label='PFJet260', color='#e4ac0c', marker='>', marker_style='full'),
        #        dict(expression='"te:HLT_PFJet320/{quantity[name]}"', label='PFJet320', color='#ed690c', marker='o', marker_style='full'),
        #        dict(expression='"te:HLT_PFJet400/{quantity[name]}"', label='PFJet400', color='#ed360c', marker='x', marker_style='empty'),
        #        dict(expression='"te:HLT_PFJet450/{quantity[name]}"', label='PFJet450', color='#d1110b', marker='d', marker_style='full'),
        #        dict(expression='"te:HLT_PFJet500/{quantity[name]}"', label='PFJet500', color='#a52509', marker='s', marker_style='full'),
        #    ],
        #    'x_label' : '{quantity[label]}',
        #    'x_range' : ContextValue('quantity[x_range]'),
        #    'x_scale' : '{quantity[scale]}',
        #    'y_label' : 'Mean efficiency',
        #    'y_range' : (-0.1, 1.2),
        #    'y_scale' : 'linear',
        #    'legend_kwargs': dict(loc='lower right'),
        #    'upper_label': LiteralString(r"$\mathcal{{L}}\,=\,{:.2f}\,\,\mathrm{{fb}}^{{-1}}$ ({})".format(SAMPLE_LUMINOSITY/1e9, SAMPLE_LABEL)),
        #},
        #{
        #    'filename' : "fig_TriggerPrescales_{quantity[name]}.png",
        #    'subplots' : [
        #        dict(expression='"tp:HLT_PFJet40/{quantity[name]}"' , label='PFJet40' , color='#1b09aa', marker='o', marker_style='full'),
        #        dict(expression='"tp:HLT_PFJet60/{quantity[name]}"' , label='PFJet60' , color='#094aaa', marker='D', marker_style='full'),
        #        dict(expression='"tp:HLT_PFJet80/{quantity[name]}"' , label='PFJet80' , color='#0bd1d1', marker='v', marker_style='full'),
        #        dict(expression='"tp:HLT_PFJet140/{quantity[name]}"', label='PFJet140', color='#0ce41f', marker='^', marker_style='full'),
        #        dict(expression='"tp:HLT_PFJet200/{quantity[name]}"', label='PFJet200', color='#dee40c', marker='s', marker_style='full'),
        #        dict(expression='"tp:HLT_PFJet260/{quantity[name]}"', label='PFJet260', color='#e4ac0c', marker='>', marker_style='full'),
        #        dict(expression='"tp:HLT_PFJet320/{quantity[name]}"', label='PFJet320', color='#ed690c', marker='o', marker_style='full'),
        #        dict(expression='"tp:HLT_PFJet400/{quantity[name]}"', label='PFJet400', color='#ed360c', marker='x', marker_style='empty'),
        #        dict(expression='"tp:HLT_PFJet450/{quantity[name]}"', label='PFJet450', color='#d1110b', marker='d', marker_style='full'),
        #        dict(expression='"tp:HLT_PFJet500/{quantity[name]}"', label='PFJet500', color='#a52509', marker='s', marker_style='full'),
        #    ],
        #    'x_label' : '{quantity[label]}',
        #    'x_range' : ContextValue('quantity[x_range]'),
        #    'x_scale' : '{quantity[scale]}',
        #    'y_label' : 'Mean prescale value',
        #    'y_scale' : 'linear',
        #    'upper_label': LiteralString(r"$\mathcal{{L}}\,=\,{:.2f}\,\,\mathrm{{fb}}^{{-1}}$ ({})".format(SAMPLE_LUMINOSITY/1e9, SAMPLE_LABEL)),
        #},
        #{
        #    'filename' : "fig_TriggerComposition_{quantity[name]}.png",
        #    'subplots' : [
        #        dict(expression='"tc:HLT_PFJet40/{quantity[name]}" /"tc:all/{quantity[name]}"', label='PFJet40' , color='#1F194D', plot_method='bar', stack='all', show_yerr=False),
        #        dict(expression='"tc:HLT_PFJet60/{quantity[name]}" /"tc:all/{quantity[name]}"', label='PFJet60' , color='#192E4D', plot_method='bar', stack='all', show_yerr=False),
        #        dict(expression='"tc:HLT_PFJet80/{quantity[name]}" /"tc:all/{quantity[name]}"', label='PFJet80' , color='#246B6B', plot_method='bar', stack='all', show_yerr=False),
        #        dict(expression='"tc:HLT_PFJet140/{quantity[name]}"/"tc:all/{quantity[name]}"', label='PFJet140', color='#297A30', plot_method='bar', stack='all', show_yerr=False),
        #        dict(expression='"tc:HLT_PFJet200/{quantity[name]}"/"tc:all/{quantity[name]}"', label='PFJet200', color='#787A29', plot_method='bar', stack='all', show_yerr=False),
        #        dict(expression='"tc:HLT_PFJet260/{quantity[name]}"/"tc:all/{quantity[name]}"', label='PFJet260', color='#7A6529', plot_method='bar', stack='all', show_yerr=False),
        #        dict(expression='"tc:HLT_PFJet320/{quantity[name]}"/"tc:all/{quantity[name]}"', label='PFJet320', color='#824F2B', plot_method='bar', stack='all', show_yerr=False),
        #        dict(expression='"tc:HLT_PFJet400/{quantity[name]}"/"tc:all/{quantity[name]}"', label='PFJet400', color='#823B2B', plot_method='bar', stack='all', show_yerr=False),
        #        dict(expression='"tc:HLT_PFJet450/{quantity[name]}"/"tc:all/{quantity[name]}"', label='PFJet450', color='#6B2624', plot_method='bar', stack='all', show_yerr=False),
        #        dict(expression='"tc:HLT_PFJet500/{quantity[name]}"/"tc:all/{quantity[name]}"', label='PFJet500', color='#492118', plot_method='bar', stack='all', show_yerr=False),
        #    ],
        #    'x_label' : '{quantity[label]}',
        #    'x_range' : ContextValue('quantity[x_range]'),
        #    'x_scale' : '{quantity[scale]}',
        #    'y_label' : 'Fraction of events triggered',
        #    'y_range' : (-0.1, 1.2),
        #    'y_scale' : 'linear',
        #    'upper_label': LiteralString(r"$\mathcal{{L}}\,=\,{:.2f}\,\,\mathrm{{fb}}^{{-1}}$ ({})".format(SAMPLE_LUMINOSITY/1e9, SAMPLE_LABEL)),
        #},
        #{
        #    'filename' : "fig_TriggerCompositionWeightedEfficiency_{quantity[name]}.png",
        #    'subplots' : [
        #        dict(expression='"tc:HLT_PFJet40/{quantity[name]}"  / "tc:all/{quantity[name]}" * "te:HLT_PFJet40/{quantity[name]}"' , label='PFJet40' , color='#1b09aa', plot_method='errorbar', marker='o', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet60/{quantity[name]}"  / "tc:all/{quantity[name]}" * "te:HLT_PFJet60/{quantity[name]}"' , label='PFJet60' , color='#094aaa', plot_method='errorbar', marker='D', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet80/{quantity[name]}"  / "tc:all/{quantity[name]}" * "te:HLT_PFJet80/{quantity[name]}"' , label='PFJet80' , color='#0bd1d1', plot_method='errorbar', marker='v', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet140/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet140/{quantity[name]}"', label='PFJet140', color='#0ce41f', plot_method='errorbar', marker='^', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet200/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet200/{quantity[name]}"', label='PFJet200', color='#dee40c', plot_method='errorbar', marker='s', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet260/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet260/{quantity[name]}"', label='PFJet260', color='#e4ac0c', plot_method='errorbar', marker='>', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet320/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet320/{quantity[name]}"', label='PFJet320', color='#ed690c', plot_method='errorbar', marker='o', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet400/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet400/{quantity[name]}"', label='PFJet400', color='#ed360c', plot_method='errorbar', marker='x', marker_style='empty'),
        #        dict(expression='"tc:HLT_PFJet450/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet450/{quantity[name]}"', label='PFJet450', color='#d1110b', plot_method='errorbar', marker='d', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet500/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet500/{quantity[name]}"', label='PFJet500', color='#a52509', plot_method='errorbar', marker='s', marker_style='full'),
        #    ],
        #    'x_label' : '{quantity[label]}',
        #    'x_range' : ContextValue('quantity[x_range]'),
        #    'x_scale' : '{quantity[scale]}',
        #    'y_label' : r'TC Weight / Scale factor (TE)',
        #    'y_range' : (-0.1, 1.2),
        #    'y_scale' : 'linear',
        #    'upper_label': LiteralString(r"$\mathcal{{L}}\,=\,{:.2f}\,\,\mathrm{{fb}}^{{-1}}$ ({})".format(SAMPLE_LUMINOSITY/1e9, SAMPLE_LABEL)),
        #},
        #{
        #    'filename' : "fig_TriggerCompositionWeightedEfficiencyPrescale_{quantity[name]}.png",
        #    'subplots' : [
        #        dict(expression='"tc:HLT_PFJet40/{quantity[name]}"  / "tc:all/{quantity[name]}" * "te:HLT_PFJet40/{quantity[name]}"  / "tp:HLT_PFJet40/{quantity[name]}" ', label='PFJet40' , color='#1b09aa', plot_method='errorbar', marker='o', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet60/{quantity[name]}"  / "tc:all/{quantity[name]}" * "te:HLT_PFJet60/{quantity[name]}"  / "tp:HLT_PFJet60/{quantity[name]}" ', label='PFJet60' , color='#094aaa', plot_method='errorbar', marker='D', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet80/{quantity[name]}"  / "tc:all/{quantity[name]}" * "te:HLT_PFJet80/{quantity[name]}"  / "tp:HLT_PFJet80/{quantity[name]}" ', label='PFJet80' , color='#0bd1d1', plot_method='errorbar', marker='v', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet140/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet140/{quantity[name]}" / "tp:HLT_PFJet140/{quantity[name]}"', label='PFJet140', color='#0ce41f', plot_method='errorbar', marker='^', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet200/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet200/{quantity[name]}" / "tp:HLT_PFJet200/{quantity[name]}"', label='PFJet200', color='#dee40c', plot_method='errorbar', marker='s', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet260/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet260/{quantity[name]}" / "tp:HLT_PFJet260/{quantity[name]}"', label='PFJet260', color='#e4ac0c', plot_method='errorbar', marker='>', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet320/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet320/{quantity[name]}" / "tp:HLT_PFJet320/{quantity[name]}"', label='PFJet320', color='#ed690c', plot_method='errorbar', marker='o', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet400/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet400/{quantity[name]}" / "tp:HLT_PFJet400/{quantity[name]}"', label='PFJet400', color='#ed360c', plot_method='errorbar', marker='x', marker_style='empty'),
        #        dict(expression='"tc:HLT_PFJet450/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet450/{quantity[name]}" / "tp:HLT_PFJet450/{quantity[name]}"', label='PFJet450', color='#d1110b', plot_method='errorbar', marker='d', marker_style='full'),
        #        dict(expression='"tc:HLT_PFJet500/{quantity[name]}" / "tc:all/{quantity[name]}" * "te:HLT_PFJet500/{quantity[name]}" / "tp:HLT_PFJet500/{quantity[name]}"', label='PFJet500', color='#a52509', plot_method='errorbar', marker='s', marker_style='full'),
        #    ],
        #    'x_label' : '{quantity[label]}',
        #    'x_range' : ContextValue('quantity[x_range]'),
        #    'x_scale' : '{quantity[scale]}',
        #    'y_label' : r'TC Weight / Scale factor (TE, TP)',
        #    'y_range' : (-0.1, 1.2),
        #    'y_scale' : 'linear',
        #    'upper_label': LiteralString(r"$\mathcal{{L}}\,=\,{:.2f}\,\,\mathrm{{fb}}^{{-1}}$ ({})".format(SAMPLE_LUMINOSITY/1e9, SAMPLE_LABEL)),
        #},
        #{
        #    'filename' : "fig_EventYieldWeight_{quantity[name]}.png",
        #    'subplots' : [
        #        dict(expression='({})'.format(_weightstring), color='k',  plot_method='errorbar', marker='o', marker_style='empty'),
        #    ],
        #    'x_label' : '{quantity[label]}',
        #    'x_range' : ContextValue('quantity[x_range]'),
        #    'x_scale' : '{quantity[scale]}',
        #    'y_label' : 'Event yield weight',
        #    #'y_range' : (-0.1, 1.2),
        #    'y_scale' : 'linear',
        #    'upper_label': LiteralString(r"$\mathcal{{L}}\,=\,{:.2f}\,\,\mathrm{{fb}}^{{-1}}$ ({})".format(SAMPLE_LUMINOSITY/1e9, SAMPLE_LABEL)),
        #},
        #{
        #    'filename' : "fig_EventYield_{quantity[name]}.png",
        #    'subplots' : [
        #        dict(expression='"xs:YB01_YS01/{quantity[name]}"', label='YB01_YS01', color='royalblue',        plot_method='errorbar', marker='D', marker_style='full'),
        #        dict(expression='"xs:YB01_YS12/{quantity[name]}"', label='YB01_YS12', color='forestgreen',      plot_method='errorbar', marker='v', marker_style='full'),
        #        dict(expression='"xs:YB01_YS23/{quantity[name]}"', label='YB01_YS23', color='darkred',          plot_method='errorbar', marker='^', marker_style='full'),
        #        dict(expression='"xs:YB12_YS01/{quantity[name]}"', label='YB12_YS01', color='darkorchid',       plot_method='errorbar', marker='s', marker_style='full'),
        #        dict(expression='"xs:YB12_YS12/{quantity[name]}"', label='YB12_YS12', color='orange',           plot_method='errorbar', marker='>', marker_style='full'),
        #        dict(expression='"xs:YB23_YS01/{quantity[name]}"', label='YB23_YS01', color='darkturquoise',    plot_method='errorbar', marker='o', marker_style='full'),
        #        dict(expression='"xs:inclusive/{quantity[name]}"', label='inclusive', color='k',                plot_method='errorbar', marker='o', marker_style='empty'),
        #    ],
        #    'x_label' : '{quantity[label]}',
        #    'x_range' : ContextValue('quantity[x_range]'),
        #    'x_scale' : '{quantity[scale]}',
        #    'y_label' : 'Event yield',
        #    'y_scale' : 'log',
        #    'upper_label': LiteralString(r"$\mathcal{{L}}\,=\,{:.2f}\,\,\mathrm{{fb}}^{{-1}}$ ({})".format(SAMPLE_LUMINOSITY/1e9, SAMPLE_LABEL)),
        #},
        ##{
        ##    'filename' : "fig_WeightedTriggerPrescales_{quantity[name]}.png",
        ##    'subplots' : [
        ##        dict(expression='"tp:HLT_PFJet40/{{quantity[name]}}" / ({})'.format(_weightstring) , label='PFJet40' , color='#1b09aa', marker='o', marker_style='full'),
        ##        dict(expression='"tp:HLT_PFJet60/{{quantity[name]}}" / ({})'.format(_weightstring) , label='PFJet60' , color='#094aaa', marker='D', marker_style='full'),
        ##        dict(expression='"tp:HLT_PFJet80/{{quantity[name]}}" / ({})'.format(_weightstring) , label='PFJet80' , color='#0bd1d1', marker='v', marker_style='full'),
        ##        dict(expression='"tp:HLT_PFJet140/{{quantity[name]}}" / ({})'.format(_weightstring), label='PFJet140', color='#0ce41f', marker='^', marker_style='full'),
        ##        dict(expression='"tp:HLT_PFJet200/{{quantity[name]}}" / ({})'.format(_weightstring), label='PFJet200', color='#dee40c', marker='s', marker_style='full'),
        ##        dict(expression='"tp:HLT_PFJet260/{{quantity[name]}}" / ({})'.format(_weightstring), label='PFJet260', color='#e4ac0c', marker='>', marker_style='full'),
        ##        dict(expression='"tp:HLT_PFJet320/{{quantity[name]}}" / ({})'.format(_weightstring), label='PFJet320', color='#ed690c', marker='o', marker_style='full'),
        ##        dict(expression='"tp:HLT_PFJet400/{{quantity[name]}}" / ({})'.format(_weightstring), label='PFJet400', color='#ed360c', marker='x', marker_style='empty'),
        ##        dict(expression='"tp:HLT_PFJet450/{{quantity[name]}}" / ({})'.format(_weightstring), label='PFJet450', color='#d1110b', marker='d', marker_style='full'),
        ##        dict(expression='"tp:HLT_PFJet500/{{quantity[name]}}" / ({})'.format(_weightstring), label='PFJet500', color='#a52509', marker='s', marker_style='full'),
        ##    ],
        ##    'x_label' : '{quantity[label]}',
        ##    'x_range' : ContextValue('quantity[x_range]'),
        ##    'x_scale' : '{quantity[scale]}',
        ##    'y_label' : 'Weighted prescale value',
        ##    'y_scale' : 'linear',
        ##    'upper_label': LiteralString(r"$\mathcal{{L}}\,=\,{:.2f}\,\,\mathrm{{fb}}^{{-1}}$ ({})".format(SAMPLE_LUMINOSITY/1e9, SAMPLE_LABEL)),
        ##},
        #{
        #    'filename' : "fig_WeightedEventYield_{quantity[name]}.png",
        #    'subplots' : [
        #        dict(expression='"xs:YB01_YS01/{{quantity[name]}}" * ({})'.format(_weightstring), label='YB01_YS01', color='royalblue',     plot_method='errorbar', marker='D', marker_style='full'),
        #        dict(expression='"xs:YB01_YS12/{{quantity[name]}}" * ({})'.format(_weightstring), label='YB01_YS12', color='forestgreen',   plot_method='errorbar', marker='v', marker_style='full'),
        #        dict(expression='"xs:YB01_YS23/{{quantity[name]}}" * ({})'.format(_weightstring), label='YB01_YS23', color='darkred',       plot_method='errorbar', marker='^', marker_style='full'),
        #        dict(expression='"xs:YB12_YS01/{{quantity[name]}}" * ({})'.format(_weightstring), label='YB12_YS01', color='darkorchid',    plot_method='errorbar', marker='s', marker_style='full'),
        #        dict(expression='"xs:YB12_YS12/{{quantity[name]}}" * ({})'.format(_weightstring), label='YB12_YS12', color='orange',        plot_method='errorbar', marker='>', marker_style='full'),
        #        dict(expression='"xs:YB23_YS01/{{quantity[name]}}" * ({})'.format(_weightstring), label='YB23_YS01', color='darkturquoise', plot_method='errorbar', marker='o', marker_style='full'),
        #        dict(expression='"xs:inclusive/{{quantity[name]}}" * ({})'.format(_weightstring), label='inclusive', color='k',             plot_method='errorbar', marker='o', marker_style='empty'),
        #    ],
        #    'x_label' : '{quantity[label]}',
        #    'x_range' : ContextValue('quantity[x_range]'),
        #    'x_scale' : '{quantity[scale]}',
        #    'y_label' : 'Weighted event yield',
        #    'y_scale' : 'log',
        #    'upper_label': LiteralString(r"$\mathcal{{L}}\,=\,{:.2f}\,\,\mathrm{{fb}}^{{-1}}$ ({})".format(SAMPLE_LUMINOSITY/1e9, SAMPLE_LABEL)),
        #},
        {
            'filename' : "fig_CrossSection_{quantity[name]}.png",
            'subplots' : [
                dict(expression='1e12 * "xs:inclusive/{{quantity[name]}}" * ({}) / {}'.format(_weightstring, SAMPLE_LUMINOSITY/1e6), label=r'inclusive ($\times 10^{{12}}$)',
                     color='k',
                     plot_method='errorbar', marker='o', marker_style='empty', normalize_to_width=True),
                dict(expression='1e11 * "xs:YB01_YS01/{{quantity[name]}}" * ({}) / {}'.format(_weightstring, SAMPLE_LUMINOSITY/1e6), label=r'YB01_YS01 ($\times 10^{{11}}$)',
                     color='royalblue',
                     plot_method='errorbar', marker='D', marker_style='full',  normalize_to_width=True),
                dict(expression='1e8  * "xs:YB01_YS12/{{quantity[name]}}" * ({}) / {}'.format(_weightstring, SAMPLE_LUMINOSITY/1e6), label=r'YB01_YS12 ($\times 10^8$)',
                     color='forestgreen',
                     plot_method='errorbar', marker='v', marker_style='full',  normalize_to_width=True),
                dict(expression='1e6  * "xs:YB01_YS23/{{quantity[name]}}" * ({}) / {}'.format(_weightstring, SAMPLE_LUMINOSITY/1e6), label=r'YB01_YS23 ($\times 10^6$)',
                     color='darkred',
                     plot_method='errorbar', marker='^', marker_style='full',  normalize_to_width=True),
                dict(expression='1e2  * "xs:YB12_YS01/{{quantity[name]}}" * ({}) / {}'.format(_weightstring, SAMPLE_LUMINOSITY/1e6), label=r'YB12_YS01 ($\times 10^2$)',
                     color='darkorchid',
                     plot_method='errorbar', marker='s', marker_style='full',  normalize_to_width=True),
                dict(expression='1e0  * "xs:YB12_YS12/{{quantity[name]}}" * ({}) / {}'.format(_weightstring, SAMPLE_LUMINOSITY/1e6), label=r'YB12_YS12 ($\times 10^0$)',
                     color='orange',
                     plot_method='errorbar', marker='>', marker_style='full',  normalize_to_width=True),
                dict(expression='1e0  * "xs:YB23_YS01/{{quantity[name]}}" * ({}) / {}'.format(_weightstring, SAMPLE_LUMINOSITY/1e6), label=r'YB23_YS01 ($\times 10^0$)',
                     color='darkturquoise',
                     plot_method='errorbar', marker='o', marker_style='full',  normalize_to_width=True),
            ],
            'x_label' : '{quantity[label]}',
            'x_range' : ContextValue('quantity[x_range]'),
            'x_scale' : '{quantity[scale]}',
            'y_label' : 'Diff. cross section',  #r"$\frac{{\mathrm{{d}}^3\sigma}}{{\mathrm{{d}}{{{}}}\,\mathrm{{d}}y_{{\mathrm{{b}}}}\,\mathrm{{d}}y*}}\,\,/\,\,\mathrm{{pb}}/\mathrm{{GeV}}$"
            'y_scale' : 'log',
            'y_range' : (1e-9, 1e23),
            'upper_label': LiteralString(r"$\mathcal{{L}}\,=\,{:.2f}\,\,\mathrm{{fb}}^{{-1}}$ ({})".format(SAMPLE_LUMINOSITY/1e9, SAMPLE_LABEL)),
        },
        {
            'filename' : "fig_CrossSectionOLD_{quantity[name]}.png",
            'subplots' : [
                dict(expression='1e12 * "xs:inclusive/{{quantity[name]}}_totalWeight" / {}'.format(SAMPLE_LUMINOSITY/1e6), label=r'inclusive ($\times 10^{{12}}$)',
                     color='k',
                     plot_method='errorbar', marker='o', marker_style='empty', normalize_to_width=True),
                dict(expression='1e11 * "xs:YB01_YS01/{{quantity[name]}}_totalWeight" / {}'.format(SAMPLE_LUMINOSITY/1e6), label=r'YB01_YS01 ($\times 10^{{11}}$)',
                     color='royalblue',
                     plot_method='errorbar', marker='D', marker_style='full',  normalize_to_width=True),
                dict(expression='1e8  * "xs:YB01_YS12/{{quantity[name]}}_totalWeight" / {}'.format(SAMPLE_LUMINOSITY/1e6), label=r'YB01_YS12 ($\times 10^8$)',
                     color='forestgreen',
                     plot_method='errorbar', marker='v', marker_style='full',  normalize_to_width=True),
                dict(expression='1e6  * "xs:YB01_YS23/{{quantity[name]}}_totalWeight" / {}'.format(SAMPLE_LUMINOSITY/1e6), label=r'YB01_YS23 ($\times 10^6$)',
                     color='darkred',
                     plot_method='errorbar', marker='^', marker_style='full',  normalize_to_width=True),
                dict(expression='1e2  * "xs:YB12_YS01/{{quantity[name]}}_totalWeight" / {}'.format(SAMPLE_LUMINOSITY/1e6), label=r'YB12_YS01 ($\times 10^2$)',
                     color='darkorchid',
                     plot_method='errorbar', marker='s', marker_style='full',  normalize_to_width=True),
                dict(expression='1e0  * "xs:YB12_YS12/{{quantity[name]}}_totalWeight" / {}'.format(SAMPLE_LUMINOSITY/1e6), label=r'YB12_YS12 ($\times 10^0$)',
                     color='orange',
                     plot_method='errorbar', marker='>', marker_style='full',  normalize_to_width=True),
                dict(expression='1e0  * "xs:YB23_YS01/{{quantity[name]}}_totalWeight" / {}'.format(SAMPLE_LUMINOSITY/1e6), label=r'YB23_YS01 ($\times 10^0$)',
                     color='darkturquoise',
                     plot_method='errorbar', marker='o', marker_style='full',  normalize_to_width=True),
            ],
            'x_label' : '{quantity[label]}',
            'x_range' : ContextValue('quantity[x_range]'),
            'x_scale' : '{quantity[scale]}',
            'y_label' : 'Diff. cross section',  #r"$\frac{{\mathrm{{d}}^3\sigma}}{{\mathrm{{d}}{{{}}}\,\mathrm{{d}}y_{{\mathrm{{b}}}}\,\mathrm{{d}}y*}}\,\,/\,\,\mathrm{{pb}}/\mathrm{{GeV}}$"
            'y_scale' : 'log',
            'y_range' : (1e-9, 1e23),
            'upper_label': LiteralString(r"$\mathcal{{L}}\,=\,{:.2f}\,\,\mathrm{{fb}}^{{-1}}$ ({})".format(SAMPLE_LUMINOSITY/1e9, SAMPLE_LABEL)),
        },
    ],
    'expansions' : {
        'quantity' : [
            {
                "name": "jet1pt",
                "label": r"${p_{\mathrm{T}}^{\mathrm{jet1}}}$",
                "scale": "log",
                'x_range' : (60, 5000),
            },
            {
                "name": "jet12ptave",
                "label": r"${\langle p_{\mathrm{T}} \rangle}_{1,2}$",
                "scale": "log",
                'x_range' : (60, 5000),
            },
            {
                "name": "jet12mass",
                "label": r"${m_{\mathrm{jj}}}$",
                "scale": "log",
                'x_range' : (60, 8000),
            },
        ]
    }
}



if __name__ == "__main__":
    p = Plotter(PLOT_CONFIG)
    p.run()
