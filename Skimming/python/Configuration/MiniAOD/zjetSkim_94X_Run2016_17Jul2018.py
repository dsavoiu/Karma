"""
Karma skim config for 94X miniAOD files
=======================================

This skim config should be used for 2016 samples produced with CMSSW 94X,
e.g. 17Jul2018 Re-MiniAOD or the corresponding Monte-Carlo.

To use:

    # import the module
    from Karma.Skimming.Configuration.MiniAOD import karmaSkim_94X_Run2016_17Jul2018_cff

    # register the options
    options = karmaSkim_94X_Run2016_17Jul2018_cff.register_options(options)

    # configure the process
    karmaSkim_94X_Run2016_17Jul2018_cff.configure(process)


"""
import FWCore.ParameterSet.Config as cms

from .karmaSkim_94X_base import register_options as _base_register_options
from .karmaSkim_94X_base import configure as _base_configure

def register_options(options):
    """Command-Line option flags used by the configuration below."""
    return (
        _base_register_options(options)
            .setDefault('hltRegexes', [
                # single-muon triggers, e.g. HLT_IsoMu24_v3
                "^HLT_(Iso)?(Tk)?Mu[0-9]+(_eta2p1|_TrkIsoVVL)?_v[0-9]+$",
                # double-muon triggers, e.g. HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v1
                "^HLT_Mu[0-9]+(_TrkIsoVVL)?_(Tk)?Mu[0-9]+(_TrkIsoVVL)?(_DZ)?(_Mass[0-9p]+)?_v[0-9]+$",
                # double-electron trigger
                "^HLT_Ele[0-9]+_Ele[0-9]+(_CaloIdL)?(_TrackIdL)?(_IsoVL)?(_DZ)?_v[0-9]+$",
            ])
    )

def configure(process, options):
    """Apply configuration to a process."""

    _process = _base_configure(process, options)

    # == Z+Jet customizations =============================================

    # (none so far)

    return _process
