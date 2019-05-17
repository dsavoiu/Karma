#
# karmaOptions
# ------------
#
#   Register a number of standard command-line options for cmsRun.
#   Provide tools for registering additional options on a
#   config-by-config basis.
#
#   All registered options can be accessed later in the
#   config script using 'options.<optionName>'
#
#   Note: Some options are already pre-defined by CMSSW. These include:
#   ----
#         inputFiles      :  list of input filenames [default: <empty list>]
#         outputFile      :  name of the output file [default: "output.root"]
#         maxEvents       :  maximum number of events to process [default: -1 (=no limit)]
#
#   This file should be included first in every top-level configuration
#   file. It is best included in the top-level namespace, i.e.:
#
#     from Karma.Common.Tools import KarmaOptions
#
#     # create object
#     options = KarmaOptions()
#
#     # register custom option
#     options.register('myOption', default=True, type_=bools, description="...")
#
#     # finally, parse all command-line options
#     options.parseArguments()
#
#     # -- OR: all in one go
#
#     options = KarmaOptions().register(...).parseArguments()


from FWCore.ParameterSet.VarParsing import VarParsing

__all__ = ['KarmaOptions']


class KarmaOptions(VarParsing):

    # map Python types to VarParsing types
    _VPTYPE_FROM_PYTHON_TYPE = {
        str  : VarParsing.varType.string,
        int  : VarParsing.varType.int,
        float : VarParsing.varType.float,
        bool : VarParsing.varType.bool
    }
    _VPMULT_FROM_STRING = {
        'singleton'  : VarParsing.multiplicity.singleton,
        'list'  : VarParsing.multiplicity.list,
    }

    def __init__(self, *args, **kwargs):

        # temporarily replace 'register' with old API (for base constructor call)
        self.__dict__['register'] = VarParsing.register.__get__(self, self.__class__)
        super(KarmaOptions, self).__init__(*args, **kwargs)
        self.__dict__['register'] = KarmaOptions.register.__get__(self, self.__class__)

        # register some command-line options by default
        self.register('isData',
                      default="__required__",
                      type_=bool,
                      description="True if sample is data, False if Monte Carlo (default: True)")
        self.register('globalTag',
                      default="__required__",
                      type_=str,
                      description='Global tag')
        self.register('reportEvery',
                      default=1000,
                      type_=int,
                      description=("Print a message after each <reportEvery> "
                                   "events processed (default: 1000)"))
        self.register('outputFile',
                      default='__required__',
                      type_=str,
                      description=('Name of the produced output file'))
        self.register('dumpPython',
                      default=False,
                      type_=bool,
                      description=('(for testing) dump the full cmsRun Python config before '
                                   'running.'))
        self.register('configureOnly',
                      default=False,
                      type_=bool,
                      description=('(for testing only) configure, but do not run.'))
        self.register('maxEvents',
                      default=-1,
                      type_=int,
                      description="Number of events to process (-1 for all)")
        self.register('inputFiles',
                      default=[],
                      type_=str,
                      description="Files to process",
                      multiplicity='list')
        self.register('numThreads',
                      default=1,
                      type_=int,
                      description="Number of threads (for processes that support multithreading)")

    def _validate(self):
        '''check for '__required__' arguments without a value'''
        for _option in self._register:
            if getattr(self, _option) == '__required__':
                raise ValueError("Missing required option '{}'!".format(_option))

    # -- public API

    # override: allow multiple `parseArguments` calls for re-reading options from the CL
    def parseArguments(self):
        '''Obtain option values from the command line.'''
        self._beenSet = {}  # forget about previous values
        super(KarmaOptions, self).parseArguments()

        self._validate()  # check for args with default '__required__'

        return self  # allow chained calls like KarmaOptions().parseArguments()

    # override: allow chaining 'setDefault' calls
    def setDefault(self, name, value):
        '''Reset the default value of an option.'''
        super(KarmaOptions, self).setDefault(name, value)

        return self  # allow chained calls like KarmaOptions().setDefault()

    # override: provide a more Pythonic interface and allow native Python types to be used
    def register(self, name, type_, description, default=None, multiplicity='singleton'):
        '''Register a new command-line option.'''
        _vp_type = self._VPTYPE_FROM_PYTHON_TYPE.get(type_, None)
        if _vp_type is None:
            raise Exception("Cannot register option with Python type '{}': "
                            "no corresponding type defined in "
                            "'FWCore.ParameterSet.VarParsing.varType'".format(type_))

        _vp_mult = self._VPMULT_FROM_STRING.get(multiplicity, None)
        if _vp_mult is None:
            raise ValueError("Unknown option multiplicity '{}': "
                             "possible values are 'singleton' "
                             "and 'list'.".format(multiplicity))

        # call super with resolved type and multiplicity
        super(KarmaOptions, self).register(
            name,
            default,
            _vp_mult,
            _vp_type,
            description
        )
        return self  # allow chained calls like KarmaOptions().register(...).parseArguments()



