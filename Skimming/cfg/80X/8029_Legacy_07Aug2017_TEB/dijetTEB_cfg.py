import FWCore.PythonUtilities.LumiList as LumiList

from Karma.Common.Tools import KarmaOptions, KarmaProcess


# -- for testing and debugging
if not os.getenv("GC_VERSION"):
    # -- override CLI options for test
    options.inputFiles="file://{}".format(os.path.realpath("../../../data/test_JetHT2016G.root"))
    options.isData=1
    options.globalTag="80X_dataRun2_2016LegacyRepro_v4"
    options.outputFile="testTriggerEfficiencies_out.root"
    options.maxEvents=10000 #100
    options.dumpPython=1
else:
    # -- running on grid node
    options.globalTag = "__GLOBALTAG__"
    options.isData = __IS_DATA__
    #options.edmOut = options.outputFile  # FIXME #.split('.')[:-1] + "_edmOut.root"
    options.dumpPython=False
    options.reportEvery = int(max(1, 10**(round(math.log(__MAX_EVENTS__)/math.log(10))-1)))

    # temporary; gc later sets process.source.fileNames directly!
    options.inputFiles = [__FILE_NAMES__]


# -- must be called at the beginning
process = createProcess("DIJET", num_threads=1)

# modules will add to this list to register a product
# for writeout
_accumulated_output_commands = ['drop *']


# -- only process certified runs and lumisections
process.source.lumisToProcess = LumiList.LumiList(
    filename = os.path.realpath("{}/src/Karma/Skimming/data/json/2016/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.json".format(os.getenv("CMSSW_BASE")))
).getVLuminosityBlockRange()


# -- configure CMSSW modules

from Karma.Skimming.TriggerEfficienciesBootstrappingAnalyzer_cfi import dijetTriggerEfficienciesBootstrappingAnalyzer

process.triggerEfficiencies = dijetTriggerEfficienciesBootstrappingAnalyzer
process.path *= process.triggerEfficiencies


# -- must be called at the end
finalizeAndRun(process, outputCommands=_accumulated_output_commands)

