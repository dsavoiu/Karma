"""
module fragment containing some useful functions
"""


__all__ = ['xs_expression', 'xs_expression_mc']


def xs_expression(ey_nick, tep_nick, ybys_dict, tp_dict, trigger_expansions):
    """Return expression for cross section with phase space partitioning choosing trigger path with maximal event yield."""
    # let outer expansion determine ybys slice
    if ybys_dict is None:
        ybys_dict = dict(name='{ybys[name]}')

    # get yield for trigger path which maximizes yield
    _max_yield_string = ('max(' +
        ', '.join([
            (
                '"{ey}:'+ybys_dict['name']+'/'+_tpi['name']+'/h_{{quantity[name]}}" * threshold('
                    '"{tep}:'+ybys_dict['name']+'/'+_tpi['name']+'/jet1HLTAssignedPathEfficiency/p_{{quantity[name]}}", '
                    '0.99'
                ')'
            )
            for _tpi in trigger_expansions
            if _tpi['name'] != "all"
        ]) + ')'
    )

    return (
        # only display point if the first argument maximal
        'mask_if_less('
            # event yield
            '"{ey}:{ybys[name]}/{tp[name]}/h_{{quantity[name]}}"'
            # but only if the corresponding trigger efficiency is >99%
            '* threshold('
                '"{tep}:{ybys[name]}/{tp[name]}/jet1HLTAssignedPathEfficiency/p_{{quantity[name]}}", '
                '0.99'
            '),' +
            # reference is the maximum of all clipped event yields
            _max_yield_string +
        ')'
        # divide by the trigger efficiency
        ' / discard_errors("{tep}:{ybys[name]}/{tp[name]}/jet1HLTAssignedPathEfficiency/p_{{quantity[name]}}")'
        # divide by the luminosity
        ' / ' + str(tp_dict['lumi_ub']/1e6)
    ).format(ey=ey_nick, tep=tep_nick, ybys=ybys_dict, tp=tp_dict)


def xs_expression_mc(ey_nick, ybys_dict):
    """Return expression for MC cross section."""

    # let outer expansion determine ybys slice
    if ybys_dict is None:
        ybys_dict = dict(name='{ybys[name]}')

    return (
        '"{ey}:{ybys[name]}/h_{{quantity[name]}}_weightForStitching"'
    ).format(ey=ey_nick, ybys=ybys_dict)
