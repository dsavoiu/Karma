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
    class GlobalCacheTE : public karma::GlobalCacheWithOutputFile {

      public:
        GlobalCacheTE(const edm::ParameterSet& pSet) :
            karma::GlobalCacheWithOutputFile(pSet, pSet.getParameter<std::string>("outputFile")),
            hltProcessName_(pSet.getParameter<std::string>("hltProcessName")),
            triggerEfficiencyBinning_(pSet_.getParameter<std::vector<double>>("triggerEfficiencyBinning")) {

            const std::string& hltPreselectionPathRegex = pSet_.getParameter<std::string>("hltPreselectionPathRegex");
            hltPreselectionPathRegex_ = boost::regex(hltPreselectionPathRegex, boost::regex::icase | boost::regex::extended);

            // create the regex objects for matching HLTtrigger names
            const std::vector<std::string>& hltProbePaths = pSet_.getParameter<std::vector<std::string>>("hltProbePaths");
            for (const auto& probePathName : hltProbePaths) {
                edm::LogWarning("TriggerEfficienciesAnalyzer") << "Adding HLT path '" << probePathName << "'";
                //hltPathRegexes_.push_back(boost::regex("^" + probePathName + "_v[0-9]+$", boost::regex::icase | boost::regex::extended));
                hltPathRegexes_.emplace(std::make_pair(probePathName, boost::regex("^" + probePathName + "_v[0-9]+$", boost::regex::icase | boost::regex::extended)));
                // create histogram for each path in output file
                makeHist1D(probePathName.c_str(), probePathName.c_str(), triggerEfficiencyBinning_);
            }
            makeHist1D("Reference", "Reference", triggerEfficiencyBinning_);

            // create the trigger emulation specification (filters and thresholds for each path)
            const auto& hltProbePathFilterSpecs = pSet_.getParameter<edm::ParameterSet>("hltProbePathFilterSpecs");
            for (const auto& pathName : hltProbePathFilterSpecs.getParameterNamesForType<edm::VParameterSet>()) {
                // ensure that all path names are available in map
                hltPathFiltersThresholds_[pathName] = {};
                hltPathL1FiltersThresholds_[pathName] = {};
                const std::vector<edm::ParameterSet>& filterSpecs = hltProbePathFilterSpecs.getParameter<edm::VParameterSet>(pathName);
                for (const auto& filterSpec : filterSpecs) {
                    const bool& isL1 = filterSpec.getParameter<bool>("isL1");
                    const std::string& filterName = filterSpec.getParameter<std::string>("filterName");
                    const double& filterThreshold = filterSpec.getParameter<double>("filterThreshold");
                    if (isL1) {
                        hltPathL1FiltersThresholds_[pathName].push_back(std::make_pair(filterName, filterThreshold));
                    }
                    else {
                        hltPathFiltersThresholds_[pathName].push_back(std::make_pair(filterName, filterThreshold));
                    }
                }

            }

            /*
            // create the regex objects for matching HLT filter names
            const std::vector<std::string>& hltFilterRegexes = pSet_.getParameter<std::vector<std::string>>("hltFilterRegexes");
            for (const auto& regexString : hltFilterRegexes) {
                std::cout << "Adding HLT filter regex '" << regexString << "'" << std::endl;
                hltFilterRegexes_.push_back(boost::regex(regexString, boost::regex::icase | boost::regex::extended));
            }
            // create the regex objects for matching L1 filter names
            const std::vector<std::string>& hltL1FilterRegexes = pSet_.getParameter<std::vector<std::string>>("hltL1FilterRegexes");
            for (const auto& regexString : hltL1FilterRegexes) {
                std::cout << "Adding HLT filter regex '" << regexString << "'" << std::endl;
                hltFilterRegexes_.push_back(boost::regex(regexString, boost::regex::icase | boost::regex::extended));
            }*/

        };


        // immmutable (config) cache entries
        std::string hltProcessName_;                // name of the process that producer the trigger path information
        const std::vector<double> triggerEfficiencyBinning_;  // bin edges for the trigger efficiency histograms

        boost::regex hltPreselectionPathRegex_;     // 'preselection' trigger paths are required to match this precompiled regex
        std::map<std::string,boost::regex> hltPathRegexes_;  // list of pre-compiled regular expressions that 'probe' trigger paths are required to match

        std::map<std::string, std::vector<std::pair<std::string, double>>> hltPathFiltersThresholds_;
        std::map<std::string, std::vector<std::pair<std::string, double>>> hltPathL1FiltersThresholds_;

        /////////std::map<std::string, std::vector<edm::ParameterSet>> hltProbePathFilterSpecs_;

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
    class RunCacheTE : public karma::CacheBase {

      public:
        RunCacheTE(const edm::ParameterSet& pSet) : karma::CacheBase(pSet) {};

        /*
        void initHLTPrescaleProvider(const edm::ParameterSet& hltPrescaleProvider, const edm::EDAnalyzer& parentAnalyzer, edm::ConsumesCollector& consumesCollector) {
            // create the HLT/L1 prescale provider object
            hltPrescaleProvider_ = std::unique_ptr<HLTPrescaleProvider>(new HLTPrescaleProvider(hltPrescaleProviderConfigPSet, consumesCollector, parentAnalyzer));
        }
        */

        //std::unique_ptr<HLTPrescaleProvider> hltPrescaleProvider_;  // helper class for obtaining trigger (and prescale) information
        std::map<std::string, std::string> hltVersionedPathNames_;  // map generic path name to versioned path name (end in '_v[0-9]+')
        std::map<std::string, unsigned int> hltPathIndicesInMenu_;   // map generic path name to index of trigger path in the current menu
        std::string hltVersionedPreselectionPathName_;
        unsigned int hltVersionedPreselectionPathIndexInMenu_;

        boost::bimap<std::string, std::string> hltPathsFiltersBimap_;

    };


    /** Cache containing resources which accumulate during a run.
     */
    class RunSummaryCacheTE : public karma::CacheBase {

      public:
        RunSummaryCacheTE(const edm::ParameterSet& pSet) : karma::CacheBase(pSet) {
            // const std::vector<double>& triggerEfficiencyBinning = pSet_.getParameter<std::vector<double>>("triggerEfficiencyBinning");
            // // book the histograms for this run
            // for (const auto& hltPathName : hltPathNames) {
            //     hltPathNumerator_[hltPathName] = std::unique_ptr<TH1D>(new TH1D("num", "num", triggerEfficiencyBinning.size()-1, &triggerEfficiencyBinning[0]));
            //     hltPathDenominator_[hltPathName] = std::unique_ptr<TH1D>(new TH1D("denom", "denom", triggerEfficiencyBinning.size()-1, &triggerEfficiencyBinning[0]));
            // }
        };

        std::map<std::string, std::unique_ptr<TH1D>> hltPathNumerator_;
        std::map<std::string, std::unique_ptr<TH1D>> hltPathDenominator_;

    };



    // -- main analyzer

    class TriggerEfficienciesAnalyzer : public edm::stream::EDAnalyzer<
        edm::GlobalCache<karma::GlobalCacheTE>,
        edm::RunCache<karma::RunCacheTE>,
        edm::RunSummaryCache<karma::RunSummaryCacheTE>> {

      public:
        explicit TriggerEfficienciesAnalyzer(const edm::ParameterSet&, const karma::GlobalCacheTE*);
        ~TriggerEfficienciesAnalyzer();

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        void beginStream(edm::StreamID);

        // -- global cache extension
        static std::unique_ptr<karma::GlobalCacheTE> initializeGlobalCache(const edm::ParameterSet& pSet);
        static void globalEndJob(karma::GlobalCacheTE*);

        // -- run cache extension
        static std::shared_ptr<karma::RunCacheTE> globalBeginRun(const edm::Run&, const edm::EventSetup&, const GlobalCache*);
        static void globalEndRun(const edm::Run&, const edm::EventSetup&, const RunContext*) {/* noop */};

        // -- run summary cache extension
        static std::shared_ptr<karma::RunSummaryCacheTE> globalBeginRunSummary(const edm::Run&, const edm::EventSetup&, const RunContext*);
        void endRunSummary(const edm::Run&, const edm::EventSetup&, karma::RunSummaryCacheTE*) const;
        static void globalEndRunSummary(const edm::Run&, const edm::EventSetup&, const RunContext*, karma::RunSummaryCacheTE*);

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

        //typename edm::Handle<pat::PackedTriggerPrescales> triggerPrescalesHandle;
        //edm::EDGetTokenT<pat::PackedTriggerPrescales> triggerPrescalesToken;

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
