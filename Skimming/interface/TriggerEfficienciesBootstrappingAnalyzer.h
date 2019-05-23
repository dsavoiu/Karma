#pragma once

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"
//#include "FWCore/Utilities/interface/Transition.h"  // CMSSW 9+

#include <boost/regex.hpp>
#include <boost/bimap.hpp>

#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"
#include "HLTrigger/HLTcore/interface/HLTPrescaleProvider.h"
#include "L1Trigger/GlobalTriggerAnalyzer/interface/L1GtUtils.h"

#include "TH1.h"

// -- common classes
#include "Karma/Common/interface/EDMTools/Caches.h"
#include "Karma/Common/interface/EDMTools/Util.h"

// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"
#include "Karma/SkimmingFormats/interface/Lumi.h"
#include "Karma/SkimmingFormats/interface/Run.h"

// -- input data formats
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/PatCandidates/interface/PackedTriggerPrescales.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"


//
// class declaration
//
namespace karma {

    /** Cache containing resources which do not change
     *  for the entire duration of the skiming job.
     */
    class GlobalCacheTEB : public karma::GlobalCacheWithOutputFile {

      public:
        GlobalCacheTEB(const edm::ParameterSet& pSet) :
            karma::GlobalCacheWithOutputFile(pSet, pSet.getParameter<std::string>("outputFile")),
            hltProcessName_(pSet.getParameter<std::string>("hltProcessName")),
            triggerEfficiencyBinning_(pSet_.getParameter<std::vector<double>>("triggerEfficiencyBinning")) {

            const auto& hltProbePathCfg = pSet_.getParameter<edm::ParameterSet>("hltProbePaths");
            for (const auto& pathName : hltProbePathCfg.getParameterNamesForType<edm::ParameterSet>()) {
                const edm::ParameterSet& pathSpec = hltProbePathCfg.getParameter<edm::ParameterSet>(pathName);
                // store regex used to match this probe path
                hltPathRegexes_.emplace(std::make_pair(pathName, boost::regex("^" + pathName + "_v[0-9]+$", boost::regex::icase | boost::regex::extended)));
                // store the trigger emulation specification (HLT and L1 pT thresholds for each path)
                hltPathL1Thresholds_[pathName] = pathSpec.getParameter<double>("l1Threshold");
                hltPathHLTThresholds_[pathName] = pathSpec.getParameter<double>("hltThreshold");
                // store the preselection ("tag") path for each probe path
                hltPathTagPaths_[pathName] = pathSpec.getParameter<std::string>("hltTagPath");
                hltTagPathRegexes_.emplace(std::make_pair(hltPathTagPaths_[pathName], boost::regex("^" + hltPathTagPaths_[pathName] + "_v[0-9]+$", boost::regex::icase | boost::regex::extended)));
                hltPathReferenceHistogramNames_[pathName] = pathName + "_Ref";
                // create trigger efficiency histogram
                makeHist1D(pathName.c_str(), pathName.c_str(), triggerEfficiencyBinning_);
                makeHist1D(hltPathReferenceHistogramNames_[pathName].c_str(), (hltPathReferenceHistogramNames_[pathName]+" ("+hltPathTagPaths_[pathName]+")").c_str(), triggerEfficiencyBinning_);
            }
        };


        // immmutable (config) cache entries
        std::string hltProcessName_;                // name of the process that producer the trigger path information
        const std::vector<double> triggerEfficiencyBinning_;  // bin edges for the trigger efficiency histograms

        std::map<std::string, boost::regex> hltPathRegexes_;     // list of pre-compiled regular expressions that 'probe' trigger paths are required to match
        std::map<std::string, boost::regex> hltTagPathRegexes_;  // list of pre-compiled regular expressions that 'tag' trigger paths are required to match
        std::map<std::string, double> hltPathL1Thresholds_;   // pT thresholds for L1 trigger objects
        std::map<std::string, double> hltPathHLTThresholds_;  // pT thresholds for HLT trigger objects
        std::map<std::string, std::string> hltPathTagPaths_;  // name of path used for preselection
        std::map<std::string, std::string> hltPathReferenceHistogramNames_;  // name of reference histogram

        // mutable cache entries

        mutable HLTConfigProvider hltConfigProvider_;  // helper object to obtain HLT configuration (default-constructed)

    };

    /** Cache containing resources which do not change
     *  for the entire duration of a luminosity block
     */
    class LumiCacheTE : public karma::CacheBase {

      public:
        LumiCacheTE(const edm::ParameterSet& pSet) : karma::CacheBase(pSet) {};

    };


    /** Cache containing resources which do not change
     *  for the entire duration of a run
     */
    class RunCacheTEB : public karma::CacheBase {

      public:
        RunCacheTEB(const edm::ParameterSet& pSet) : karma::CacheBase(pSet) {};

        /*
        void initHLTPrescaleProvider(const edm::ParameterSet& hltPrescaleProvider, const edm::EDAnalyzer& parentAnalyzer, edm::ConsumesCollector& consumesCollector) {
            // create the HLT/L1 prescale provider object
            hltPrescaleProvider_ = std::unique_ptr<HLTPrescaleProvider>(new HLTPrescaleProvider(hltPrescaleProviderConfigPSet, consumesCollector, parentAnalyzer));
        }
        */

        std::map<std::string, std::string> hltVersionedPathNames_;  // map generic path name to versioned path name (end in '_v[0-9]+')
        std::map<std::string, unsigned int> hltPathIndicesInMenu_;   // map generic path name to index of trigger path in the current menu

    };


    // -- main analyzer

    class TriggerEfficienciesBootstrappingAnalyzer : public edm::stream::EDAnalyzer<
        edm::GlobalCache<karma::GlobalCacheTEB>,
        edm::RunCache<karma::RunCacheTEB>
        //edm::RunSummaryCache<karma::RunSummaryCacheTE>
        > {

      public:
        explicit TriggerEfficienciesBootstrappingAnalyzer(const edm::ParameterSet&, const karma::GlobalCacheTEB*);
        ~TriggerEfficienciesBootstrappingAnalyzer();

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        void beginStream(edm::StreamID);

        // -- global cache extension
        static std::unique_ptr<karma::GlobalCacheTEB> initializeGlobalCache(const edm::ParameterSet& pSet);
        static void globalEndJob(karma::GlobalCacheTEB*);

        // -- run cache extension
        static std::shared_ptr<karma::RunCacheTEB> globalBeginRun(const edm::Run&, const edm::EventSetup&, const GlobalCache*);
        static void globalEndRun(const edm::Run&, const edm::EventSetup&, const RunContext*) {/* noop */};

        // -- "regular" per-Event 'analyze' method
        virtual void analyze(const edm::Event&, const edm::EventSetup&);

        // -- wrap-up at end of stream
        void endStream();


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        //std::unique_ptr<HLTPrescaleProvider> m_hltPrescaleProvider;

        // -- handles and tokens
        typename edm::Handle<edm::View<pat::Jet>> jetCollectionHandle;
        edm::EDGetTokenT<edm::View<pat::Jet>> jetCollectionToken;

        typename edm::Handle<edm::TriggerResults> triggerResultsHandle;
        edm::EDGetTokenT<edm::TriggerResults> triggerResultsToken;

        typename edm::Handle<pat::TriggerObjectStandAloneCollection> triggerObjectsHandle;
        edm::EDGetTokenT<pat::TriggerObjectStandAloneCollection> triggerObjectsToken;

        // -- per-stream "scratch space"
        std::map<std::string, std::shared_ptr<TH1D>> m_triggerEfficiencyHistos;
        std::shared_ptr<TH1D> m_triggerEfficiencyDenominatorHisto;

    };

    //
    // constants, enums and typedefs
    //


    //
    // static data member definitions
    //

}  // end namespace
