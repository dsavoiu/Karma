#!/usr/bin/env python
from Karma.PostProcessing.Lumberjack import LumberjackCLI


if __name__ == "__main__":

    _cli = LumberjackCLI()

    _cli.run()

    # re-export some names for convenience (e.g. for interactive sessions)
    import ROOT
    DF = _cli._df
