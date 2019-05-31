import argparse
import glob
import os
import shutil
import time
import fnmatch


class KarmaAnalysisDeployerGC(object):
    """Helper class for deploying an analysis on a computing cluster using grid-control."""
    def __init__(self, nick, cmsrun_config, gc_config_base, work_directory, input_files={}, files_per_job=1):
        self._nick = nick
        self._timestamp = time.strftime("%Y-%m-%d_%H-%M")
        self._workdir = os.path.join(work_directory, "{}_{}".format(self._nick, self._timestamp))
        self._gc_config_base = gc_config_base
        self._cmsrun_config = cmsrun_config
        self._files_per_job = files_per_job

        self._input_files = {}
        if input_files:
            for _dataset, _filelist in input_files.iteritems():
                self.add_input_files(_dataset, _filelist)

        self._constants = dict()
        self._lu_parameters = dict()


    def _write_dbs_file(self, dbsfile_name):
        """create dbs file so GC knows where to get the data"""
        with open(dbsfile_name, 'wb') as f:
            for _dataset_nick, _filelist in self._input_files.iteritems():
                _file_prefix = os.path.dirname(os.path.commonprefix(_filelist))
                f.write("\n[{}]\n".format(_dataset_nick))
                f.write("nickname = {}\n".format(_dataset_nick))
                f.write("events = {}\n".format(-len(_filelist)))
                f.write("prefix = {}\n".format(_file_prefix))
                for _file in _filelist:
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
            '@DATASET_SPEC@': '\n    '.join(["{nick} : {path}/files.dbs%{nick}".format(nick=_nick, path=os.path.realpath(self._workdir)) for _nick in self._input_files.keys()]),
            '@CMSRUN_CONFIG@': os.path.realpath(os.path.join(self._workdir, _cmsrun_cfg_name)),
            '@FILES_PER_JOB@': str(self._files_per_job),
        }
        for _src, _dest in _replace_dict.iteritems():
            _cfgtext = _cfgtext.replace(_src, _dest)

        # configure additional constants
        if self._constants:
            _cfgtext += "\n\nconstants = {}".format(" ".join(self._constants.keys()))
            for _constant_name, _constant_value in self._constants.iteritems():
                _cfgtext += "\n{} = {}".format(_constant_name, _constant_value)

        # configure lookup parameters
        if self._lu_parameters:
            _cfgtext += "\n\nparameters = {}".format(", ".join(["{}[{}]".format(_k, _v['key']) for _k, _v in self._lu_parameters.iteritems()]))

            for _par_name, _par_dict in self._lu_parameters.iteritems():
                _cfgtext += "\n\n{} empty set = {}".format(_par_name, _par_dict['empty_set'])
                _cfgtext += "\n{} matcher = {}".format(_par_name, _par_dict['matcher'])
                _cfgtext += "\n{} = ".format(_par_name)
                for _k, _v in _par_dict['lookup_dict'].iteritems():
                    _cfgtext += "\n  ({key}, ) => {value} ".format(key=_k, value=_v)
                _cfgtext += "\n"

        # write out modified GC config
        _gc_outpath = os.path.join(self._workdir, gc_config_filename)
        with open(_gc_outpath, 'wb') as f_out:
            f_out.write(_cfgtext)

    def add_input_files(self, dataset_nick, path_spec):
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

        return self._input_files.setdefault(dataset_nick, []).extend(_files)

    def add_constant(self, name, value):
        assert name not in self._constants
        self._constants[name] = value

    def add_lookup_parameter(self, name, lookup_dict, key, matcher='end', empty_set=True):
        assert name not in self._lu_parameters
        self._lu_parameters[name] = dict(lookup_dict=lookup_dict, key=key, matcher=matcher, empty_set=empty_set)

    def replace_file_prefix(self, prefix, replacement):
        for _dataset_nick, _filelist in self._input_files.iteritems():
            for _i_file, _filepath in enumerate(_filelist):
                if _filepath.startswith(prefix):
                    self._input_files[_dataset_nick][_i_file] = replacement + _filepath[len(prefix):]

    def deploy(self):
        """Deploy analysis to GC work directory"""
        os.makedirs(self._workdir)  # create work directory
        self._write_dbs_file(os.path.join(self._workdir, "files.dbs"))
        self._deploy_configs("{}.conf".format(self._nick))
        print("[KarmaAnalysisDeployer] Analysis deployment area created: {}".format(self._workdir))

