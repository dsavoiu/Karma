#!/usr/bin/env python
import argparse
import glob
import os
import shutil
import time
import fnmatch


class DijetAnalysisDeployerGC(object):

    def __init__(self, nick, cmsrun_config, gc_config_base, work_directory, input_files=[], files_per_job=1):
        self._nick = nick
        self._timestamp = time.strftime("%Y-%m-%d_%H-%M")
        self._workdir = os.path.join(work_directory, "{}_{}".format(self._nick, self._timestamp))
        self._gc_config_base = gc_config_base
        self._cmsrun_config = cmsrun_config
        self._files_per_job = files_per_job

        self._input_files = []
        if input_files:
            self.add_input_files(input_files)

        self._constants = dict()


    def _write_dbs_file(self, dbsfile_name):
        """create dbs file so GC knows where to get the data"""
        _file_prefix = os.path.dirname(os.path.commonprefix(self._input_files))
        with open(dbsfile_name, 'wb') as f:
            f.write("[{}]\n".format(self._nick))
            f.write("nickname = {}\n".format(self._nick))
            f.write("events = {}\n".format(-len(self._input_files)))
            f.write("prefix = {}\n".format(_file_prefix))
            for _file in self._input_files:
                f.write("{} = -1\n".format(os.path.relpath(_file, _file_prefix)))

    def _deploy_configs(self, gc_config_filename):
        """create GC config by substituting patterns in the base GC config"""

        # copy cmsRun config to work path
        _cmsrun_cfg_name = "{}_cfg.py".format(self._nick)
        shutil.copyfile(self._cmsrun_config, os.path.join(self._workdir, _cmsrun_cfg_name))

        # read the base GC config
        with open(self._gc_config_base) as f_in:
            _cfgtext = f_in.read()

        # do all pattern replacements
        _replace_dict = {
            '@NICK@': self._nick,
            '@CMSRUN_CONFIG@': os.path.realpath(os.path.join(self._workdir, _cmsrun_cfg_name)),
            '@WORKPATH@' : os.path.realpath(self._workdir),
            '@FILES_PER_JOB@': str(self._files_per_job),
        }
        for _src, _dest in _replace_dict.iteritems():
            _cfgtext = _cfgtext.replace(_src, _dest)

        # configure additional constants
        if self._constants:
            _cfgtext += "\nconstants = {}".format(" ".join(self._constants.keys()))
            for _constant_name, _constant_value in self._constants.iteritems():
                _cfgtext += "\n{} = {}".format(_constant_name, _constant_value)

        # write out modified GC config
        _gc_outpath = os.path.join(self._workdir, gc_config_filename)
        with open(_gc_outpath, 'wb') as f_out:
            f_out.write(_cfgtext)

    def add_input_files(self, path_spec):
        _protocol = ""  # local file
        _path = path_spec
        if '://' in path_spec:
            _protocol, _path = path_spec.split('://', 1)

        _files = []
        if _protocol == '':
            _files =  glob.glob(_path)
        elif _protocol == 'srm':
            import gfal2
            _grid_context = gfal2.creat_context()
            _folder = os.path.dirname(_path)
            _file_pattern = os.path.basename(_path)
            _file_list = _grid_context.listdir(_folder)
            for _filename in _file_list:
                if fnmatch.fnmatch(_filename, _file_pattern):
                    _files.append("{}://{}/{}".format(_protocol, _folder, _filename))

        return self._input_files.extend(_files)

    def add_constant(self, name, value):
        assert name not in self._constants
        self._constants[name] = value

    def replace_file_prefix(self, prefix, replacement):
        for _i_file, _filepath in enumerate(self._input_files):
            if _filepath.startswith(prefix):
                self._input_files[_i_file] = replacement + _filepath[len(prefix):]

    def deploy(self):
        """Deploy analysis to GC work directory"""
        os.makedirs(self._workdir)  # create work directory
        self._write_dbs_file(os.path.join(self._workdir, "files.dbs"))
        self._deploy_configs("{}.conf".format(self._nick))

