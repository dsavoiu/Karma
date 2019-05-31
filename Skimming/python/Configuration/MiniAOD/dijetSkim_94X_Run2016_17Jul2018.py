"""
Karma dijet skim config for 94X miniAOD files
=============================================

This skim config should be used for 2016 samples produced with CMSSW 94X,
e.g. 17Jul2018 Re-MiniAOD or the corresponding Monte-Carlo.

To use:

    # import the module
    from Karma.Skimming.Configuration.MiniAOD import dijetSkim_94X_Run2016_17Jul2018_cff

    # register the options
    options = dijetSkim_94X_Run2016_17Jul2018_cff.register_options(options)

    # configure the process
    dijetSkim_94X_Run2016_17Jul2018_cff.configure(process)


"""
import FWCore.ParameterSet.Config as cms

from .karmaSkim_94X_base import register_options as _base_register_options
from .karmaSkim_94X_base import configure as _base_configure

def register_options(options):
    """Command-Line option flags used by the configuration below."""
    return (
        _base_register_options(options)
            .setDefault('hltRegexes', [
                # single-jet triggers
                "HLT_(AK8)?PFJet[0-9]+_v[0-9]+",
                # di-jet triggers
                "HLT_DiPFJetAve[0-9]+_v[0-9]+"
            ])
    )

def configure(process, options):
    """Apply configuration to a process."""

    return _base_configure(process, options)
