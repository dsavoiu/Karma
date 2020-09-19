#!/usr/bin/env python
from __future__ import print_function

import ConfigParser
import sys
import os
import subprocess
import time
import signal
import threading
import json


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[ERROR] Expecting one argument, got {}".format(len(sys.argv)-1))

    # -- parse dataset list in GC config using ConfigParser

    c = ConfigParser.ConfigParser()
    c.read(sys.argv[1])
    _dataset_spec = c.get("CMSSW", "dataset")
    _global_tag = c.get("CMSSW", "GLOBALTAG")
 
    _datasets = []
    for _ds in _dataset_spec.split('\n'):
        _ds = _ds.strip()
        if not _ds or _ds.startswith(';'):
            continue
        _ds_split = _ds.split(':')
        assert len(_ds_split) == 2, "Cannot parse dataset line: {}".format(_ds)
        _datasets.append(_ds_split[1].strip())

    # -- query DAS to get number of events per sample

    _d_colsize = max(len(_d) for _d in _datasets)
    for _d in _datasets:

        _query_command = "dasgoclient -query 'summary dataset={sample_name}'".format(
            sample_name=_d
        )

        _proc = subprocess.Popen(
            "dasgoclient -query 'summary dataset={}'".format(_d),
            shell=True,
            stdout=subprocess.PIPE,
        )
        _proc.wait()

        _summary = json.load(_proc.stdout)
        
        for _summary_entry in _summary:
            print("{{:{}s}} {{}}".format(_d_colsize+1).format(_d+':', _summary_entry['num_event']))
