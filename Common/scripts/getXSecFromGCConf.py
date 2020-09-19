#!/usr/bin/env python
from __future__ import print_function

import ConfigParser
import sys
import os
import subprocess
import time
import signal
import threading
import re


def _reader(in_stream, out_stream, name=None, store_lines=None):
    """Continuously read lines from `in_stream` and write them to `out_stream`.

    If `name` is given, a "[`name`]" tag is prepended to each line before writing
    it to `out_stream`.

    If `store_lines` is given, each line read from `in_stream` will be appended
    to it."""

    for line in iter(in_stream.readline, b''):
        line = line.decode('utf-8')
        if store_lines is not None:
            store_lines.append(line)
        print(
            '{} {}'.format(
                '[{}] '.format(name) if name else '',
                line
            ),
            end='',
            file=out_stream
        )

def _mkdir_existok(dirname):
    '''ensure a directory exists, returning it if yes and raising on error'''
    try:
        os.mkdir(dirname)
    except OSError as e:
        if e.errno != 17:
            raise

    return dirname

#XS_LINE_START_MARKER = "After filter: final cross section = "

XS_LINE_RE = re.compile("After filter: final cross section =\s+([0-9.e+-]+)\s+\+-\s+([0-9.e+-]+)\s+([pfma]b)")

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

    _mkdir_existok('xsec')

    _out_dir = _mkdir_existok(os.path.join('xsec', os.path.basename(sys.argv[1]).split('.')[0]))

    # -- run CMSSW with GenXSecAnalyzer to obtain cross section for each sample

    _datasets_result_files = []
    for _d in _datasets:
        _out_basename = _d.strip('/').replace('/', '_')

        _out_result_dir = _mkdir_existok(os.path.join(_out_dir, _out_basename))

        _out_fname = os.path.join(_out_result_dir, 'result.txt')
        _out_fname_stdout = os.path.join(_out_result_dir, 'stdout.log')
        _out_fname_stderr = os.path.join(_out_result_dir, 'stderr.log')

        if os.path.exists(_out_fname):
            print("[INFO] Skipping XSec for dataset '{}': file exists ('{}')'".format(_d, _out_fname))
            _datasets_result_files.append((_d, _out_fname))
            continue

        _args = ("analyzeGenXSec "
            "globalTag={global_tag} "
            "sampleName={sample} "
            "outputFile={output_file} "
            "maxEvents=1000000"
        ).format(sample=_d, output_file=_out_fname, global_tag=_global_tag).split()

        # long-running process writing to stderr and stdout (for debugging)
        #_args = ["bash", "-c", "echo START; for i in {1..3}; do echo $i; echo \"ERROR $i\" 1>&2; sleep 1; done; echo STOP;"]
    
        print("[INFO] Computing XSec for dataset '{}''".format(_d))

        _proc = subprocess.Popen(
            _args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )

        _out, _err = [], []
        _threads = [
            threading.Thread(target=_reader, args=(_proc.stdout, sys.stdout, _args[0], _out)),
            threading.Thread(target=_reader, args=(_proc.stderr, sys.stderr, _args[0], _err))            
        ]

        for _t in _threads:
            _t.start()

        _exit_code = None
        try:
            # wait for process (and reader threads) to finish
            _proc.wait()
            for _t in _threads:
                _t.join()
        except KeyboardInterrupt:
            print("KeyboardInterrupt received: terminating subprocess... (Ctrl-C to force-kill)")
            # redirect interrupt to child process
            _proc.terminate()
            try:
                _proc.wait()
            except KeyboardInterrupt:
                print("KeyboardInterrupt received: killing process '{}' (PID {})...".format(_args[0], _proc.pid))
                os.killpg(os.getpgid(_proc.pid), signal.SIGKILL)
            else:
                print("Process '{}' (PID {}) has been terminated.".format(_args[0], _proc.pid))
        finally:
            _exit_code = _proc.poll()
            if _exit_code is None:
                print("[WARNING] Subprocess '{}' still running with PID {}!".format(_args[0], _proc.pid))
                break  # return control to Python
            else:
                print("[INFO] Logging output to files.")
                with open(_out_fname_stdout, 'w') as f:
                    f.write(''.join(_out or []))
                with open(_out_fname_stderr, 'w') as f:
                    f.write(''.join(_err or []))
  
        if _exit_code is None:
            print("[ERROR] Subprocess still running or it did not report status.")
        elif _exit_code < 0:
            print("[ERROR] Subprocess was terminated by signal: {}".format(_exit_code))
        elif _exit_code > 0:
            print("[ERROR] Subprocess failed with exit code: {}".format(_exit_code))

        if _exit_code != 0 and os.path.exists(_out_fname):
            print("[INFO] Moving possibly incomplete output to: {}".format(_out_fname+'.DEBUG'))
            os.rename(_out_fname, _out_fname+'.DEBUG')

            # pretty-printed command string (for writing to output shell script)
            _pprint_args = ' '.join(['\\\n    {}'.format(_arg) if _arg.startswith('--') else repr(_arg).replace("'", '"') for _arg in _args])

            # task was not killed -> inform about task failure
            raise RuntimeError(
                "'{}' exited with non-zero status ({}).\n"
                "\nCall:\n{}\n"
                "\nCaptured stdout:\n{}"
                "\nCaptured stderr:\n{}".format(_args[0], _proc.returncode, _pprint_args, ''.join(_out or []), ''.join(_err or []))
            )

        else:
            if not os.path.exists(_out_fname):
                print("[WARNING] Task ran successfully but did not produce expected output at: {}".format(_out_fname))
            else:
                _datasets_result_files.append((_d, _out_fname))

    # -- parse result files and display cross section
    _d_colsize = max(len(_d) for _d, _ in _datasets_result_files)
    for _d, _result_file in _datasets_result_files:
        _xs = "<not found>"
        with open(_result_file, 'r') as f:
            for line in f:
                _m = re.match(XS_LINE_RE, line.strip())
                if _m:
                    _xs = "{:g}".format(float(_m.group(1)))
                    break

            print("{{:{}s}} {{}}".format(_d_colsize+1).format(_d+':', _xs))

            
                
