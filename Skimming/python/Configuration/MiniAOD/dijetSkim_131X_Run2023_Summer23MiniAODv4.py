"""
Karma dijet skim config for 131X miniAOD files
==============================================

This skim config should be used for 2023 samples produced with CMSSW 13*X.

To use:

    # import the module
    from Karma.Skimming.Configuration.MiniAOD import dijetSkim_131X_Run2023_Summer23MiniAODv4_cff

    # register the options
    options = dijetSkim_131X_Run2023_Summer23MiniAODv4_cff.register_options(options)

    # configure the process
    dijetSkim_131X_Run2023_Summer23MiniAODv4_cff.configure(process)
"""
import FWCore.ParameterSet.Config as cms

from .karmaSkim_131X_base import register_options as _base_register_options
from .karmaSkim_131X_base import configure as _base_configure

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
            .setDefault('metFiltersProcess', 'DQM')
    )

def configure(process, options):
    """Apply configuration to a process."""

    return _base_configure(process, options)
