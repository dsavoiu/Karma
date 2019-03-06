import datetime
import itertools

from Karma.PostProcessing.Palisade import ContextValue, LiteralString, AnalyzeProcessor

from Karma.PostProcessing.Lumberjack.cfg.zjet_excalibur import SPLITTINGS


def build_expression(source_type, quantity_path):
    '''convenience function for putting together paths in input ROOT file'''
    source_type = source_type.strip().lower()
    assert source_type in ('data', 'mc')
    if source_type == 'data':
        return '"{0}_{{corr_level[{0}]}}:{{run_period[name]}}/{{eta[name]}}/{{alpha[name]}}/{1}"'.format(source_type, quantity_path)
    elif source_type == 'mc':
        return '"{0}_{{corr_level[{0}]}}:MC/{{eta[name]}}/{{alpha[name]}}/{1}"'.format(source_type, quantity_path)


LOOKUP_MC_CORR_LEVEL = {
    'L1L2Res' : 'L1L2L3',
    'L1L2L3Res' : 'L1L2L3',
}


def get_config(channel, sample_name, jec_name, run_periods,
               corr_levels=["L1L2L3", "L1L2Res"],
               basename_data='CombinationData2018ABC',
               basename_mc='CombinationMC',
               output_format='FullCombination_Z{channel}_{sample}_{jec}_{corr_level}.root'):

    # -- construct list of input files and correction level expansion dicts
    _input_files = dict()
    _corr_level_dicts = []
    for _cl in corr_levels:
        _input_files['data_{}'.format(_cl)] = "{}_Z{}_{}_{}_{}.root".format(
            basename_data, channel, sample_name, jec_name, _cl
        )

        # MC: lookup sample w/o residuals first
        _cl_for_mc = LOOKUP_MC_CORR_LEVEL.get(_cl, _cl)
        _input_files['mc_{}'.format(_cl)] = _input_files['mc_{}'.format(_cl_for_mc)] = "{}_Z{}_{}_{}_{}.root".format(
            basename_mc, channel, sample_name, jec_name, _cl_for_mc
        )

        _corr_level_dicts.append(
            dict(name=_cl, data=_cl, mc=_cl_for_mc)
        )

    _expansions = {
        'corr_level' : _corr_level_dicts,
        'run_period' : [
            dict(name=_rp_name)
            for _rp_name in run_periods
        ],
        'eta' : [
            dict(name=_k, label="eta_{}_{}".format("{:02d}".format(int(round(10*_v['absjet1eta'][0]))), "{:02d}".format(int(round(10*_v['absjet1eta'][1])))))
            for _k, _v in SPLITTINGS['eta'].iteritems()
        ],
        'alpha' : [
            dict(name=_k, label="a{}".format(int(_v.get('alpha', (0,.99))[1]*100)))
            for _k, _v in SPLITTINGS['alpha_inclusive'].iteritems() if _k != "alpha_all"
        ]
    }

    return {
        'input_files': _input_files,
        'tasks': [
            {
                "filename" : output_format.format(
                    channel=channel,
                    sample=sample_name,
                    jec=jec_name,
                    # get other possible replacements from expansions definition
                    **{_expansion_key : "{{{0}[name]}}".format(_expansion_key) for _expansion_key in _expansions.keys()}
                ),
                'subtasks' : [
                    # Raw event number
                    {
                        'expression': build_expression(source_type='data', quantity_path='h_zpt'),
                        'output_path': '{run_period[name]}/Data_RawNEvents_CHS_{alpha[label]}_{eta[label]}_{corr_level[name]}'
                    }
                ] + [
                    # profiles vs zpt
                    {
                        'expression': 'double_profile({x}, {y})'.format(
                            x=build_expression(source_type='data', quantity_path='zpt/p_zpt_weight'),
                            y=build_expression(source_type='data', quantity_path=_qn+'/p_zpt_weight'),
                        ),
                        'output_path': '{run_period[name]}/Data_'+_ql+'_CHS_{alpha[label]}_{eta[label]}_{corr_level[name]}'
                    }
                    for _qn, _ql in zip(
                        ["mpf", "ptbalance", "npv", "rawmpf",      "rho", "zmass", "npumean"],
                        ["MPF", "PtBal",     "NPV", "MPF-notypeI", "Rho", "ZMass", "Mu"]
                    )
                ] + [
                    # profiles vs npumean
                    {
                        'expression': build_expression(source_type='data', quantity_path=_qn+'/p_npumean_weight'),
                        'output_path': '{run_period[name]}/Data_'+_qn+'_vs_npumean_CHS_{alpha[label]}_{eta[label]}_{corr_level[name]}'
                    }
                    for _qn in ["rho", "npv"]
                ] + [
                    # Raw event number (MC)
                    {
                        'expression': build_expression(source_type='mc', quantity_path='h_zpt'),
                        'output_path': '{run_period[name]}/MC_RawNEvents_CHS_{alpha[label]}_{eta[label]}_{corr_level[name]}'
                    }
                ] + [
                    # profiles vs zpt (MC)
                    {
                        'expression': 'double_profile({x}, {y})'.format(
                            x=build_expression(source_type='mc', quantity_path='zpt/p_zpt_weight'),
                            y=build_expression(source_type='mc', quantity_path=_qn+'/p_zpt_weight'),
                        ),
                        'output_path': '{run_period[name]}/MC_'+_ql+'_CHS_{alpha[label]}_{eta[label]}_{corr_level[name]}'
                    }
                    for _qn, _ql in zip(
                        ["mpf", "ptbalance", "npv", "rawmpf",      "rho", "zmass", "npumean"],
                        ["MPF", "PtBal",     "NPV", "MPF-notypeI", "Rho", "ZMass", "Mu"]
                    )
                ] + [
                    # profiles vs npumean (MC)
                    {
                        'expression': build_expression(source_type='mc', quantity_path=_qn+'/p_npumean_weight'),
                        'output_path': '{run_period[name]}/MC_'+_qn+'_vs_npumean_CHS_{alpha[label]}_{eta[label]}_{corr_level[name]}'
                    }
                    for _qn in ["rho", "npv"]
                ] + [
                    # Raw event number (Ratio)
                    {
                        'expression': '{}/{}'.format(
                            build_expression(source_type='data', quantity_path='h_zpt'),
                            build_expression(source_type='mc', quantity_path='h_zpt'),
                        ),
                        'output_path': '{run_period[name]}/Ratio_RawNEvents_CHS_{alpha[label]}_{eta[label]}_{corr_level[name]}'
                    }
                ] + [
                    # profiles vs zpt (Ratio)
                    {
                        'expression': 'h({})/h({})'.format(
                            build_expression(source_type='data', quantity_path=_qn+'/p_zpt_weight'),
                            build_expression(source_type='mc', quantity_path=_qn+'/p_zpt_weight'),
                        ),
                        'output_path': '{run_period[name]}/Ratio_'+_ql+'_CHS_{alpha[label]}_{eta[label]}_{corr_level[name]}'
                    }
                    for _qn, _ql in zip(
                        ["mpf", "ptbalance", "npv", "rawmpf",      "rho", "zmass", "npumean"],
                        ["MPF", "PtBal",     "NPV", "MPF-notypeI", "Rho", "ZMass", "Mu"]
                    )
                ] + [
                    # profiles vs npumean (Ratio)
                    {
                        'expression': 'h({})/h({})'.format(
                            build_expression(source_type='data', quantity_path=_qn+'/p_npumean_weight'),
                            build_expression(source_type='mc', quantity_path=_qn+'/p_npumean_weight'),
                        ),
                        'output_path': '{run_period[name]}/Ratio_'+_qn+'_vs_npumean_CHS_{alpha[label]}_{eta[label]}_{corr_level[name]}'
                    }
                    for _qn in ["rho", "npv"]
                ],
            },
        ],
        'expansions' : _expansions
    }

def cli(argument_parser):
    '''command-line interface. builds on an existing `argparse.ArgumentParser` instance.'''

    # define CLI arguments
    argument_parser.add_argument('-s', '--sample', help="name of the sample, e.g. '17Sep2018'", required=True)
    argument_parser.add_argument('-j', '--jec', help="name of the JEC, e.g. 'Autumn18_JECV5'", required=True)
    argument_parser.add_argument('-r', '--run-periods', help="names of the run periods, e.g. 'Run2018A'", required=True, nargs='+')
    argument_parser.add_argument('-c', '--channels', help="name of the JEC, e.g. 'Autumn18_JECV5'", nargs='+', default=['mm', 'ee'], choices=['mm', 'ee'], metavar="CHANNEL")
    argument_parser.add_argument('-l', '--corr-levels', help="name of the JEC correction levels to include, e.g. 'L1L2L3'", nargs='+', choices=['L1', 'L1L2L3', 'L1L2L3Res', 'L1L2Res'], metavar="CORR_LEVEL")
    argument_parser.add_argument('--basename-data', help="prefix of ROOT files containing Data histograms", required=True)
    argument_parser.add_argument('--basename-mc', help="prefix of ROOT files containing MC histograms", required=True)
    # optional parameters
    argument_parser.add_argument('--output-format', help="format string defining name of output ROOT files. Default: '{%(default)s}'", default='FullCombination_Z{channel}_{sample}_{jec}_{corr_level}.root')

def run(args):

    if args.output_dir is None:
        args.output_dir = "full_combination_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f"))

    for channel in args.channels:
        print "Making combination file for channel '{}'...".format(channel)
        _cfg = get_config(
            channel=channel, 
            sample_name=args.sample, 
            jec_name=args.jec,
            corr_levels=args.corr_levels,
            run_periods=args.run_periods, 
            basename_data=args.basename_data,
            basename_mc=args.basename_mc,
            output_format=args.output_format)
        p = AnalyzeProcessor(_cfg, output_folder=args.output_dir)
        p.run()
