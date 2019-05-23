#pragma once

// system include files
#include <memory>

// user include files
#include "Karma/Common/interface/EDMTools/Util.h"

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
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

// -- base classes for caches
#include "Karma/Common/interface/EDMTools/Caches.h"

// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"
#include "Karma/SkimmingFormats/interface/Lumi.h"
#include "Karma/SkimmingFormats/interface/Run.h"

// -- input data formats
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/PatCandidates/interface/PackedTriggerPrescales.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"
#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"



//
// class declaration
//
namespace karma {


    /** Cache containing resources which do not change
     *  for the entire duration of the skiming job.
     */
    class GlobalCache : public karma::CacheBase {

      public:
        GlobalCache(const edm::ParameterSet& pSet) :
            karma::CacheBase(pSet),
            isData_(pSet.getParameter<bool>("isData")),
            writeOutTriggerPrescales_(pSet.getParameter<bool>("writeOutTriggerPrescales")),
            hltProcessName_(pSet.getParameter<std::string>("hltProcessName")) {

            // create the regex objects for matching HLTtrigger names
            const std::vector<std::string>& hltRegexes = pSet_.getParameter<std::vector<std::string>>("hltRegexes");
            for (const auto& regexString : hltRegexes) {
                std::cout << "Adding HLT regex '" << regexString << "'" << std::endl;
                hltPathRegexes_.push_back(boost::regex(regexString, boost::regex::icase | boost::regex::extended));
            }

        };

        bool isData_;
        bool writeOutTriggerPrescales_;  // if True, skims will contain trigger path prescales (only if they are non-ambiguous)
        std::string hltProcessName_;  // name of the process that producer the trigger path information

        std::vector<boost::regex> hltPathRegexes_;  // list of pre-compiled regular expressions that 'interesting' trigger paths are required to match

        mutable HLTConfigProvider hltConfigProvider_;  // helper object to obtain HLT configuration (default-constructed)

    };

    /** Cache containing resources which do not change
     *  for the entire duration of a luminosity block
     */
    class LumiCache : public karma::CacheBase {

      public:
        LumiCache(const edm::ParameterSet& pSet) : karma::CacheBase(pSet) {};

        std::vector<int> hltPathHLTPrescales_;
        std::vector<int> hltPathL1Prescales_;

    };


    /** Cache containing resources which do not change
     *  for the entire duration of a run
     */
    class RunCache : public karma::CacheBase {

      public:
        RunCache(const edm::ParameterSet& pSet) : karma::CacheBase(pSet) {};

        std::string hltMenuName_;
        karma::HLTPathInfos hltPathInfos_;  //! information about trigger paths

    };


    // -- main producer

    class EventProducer : public edm::stream::EDProducer<
        edm::GlobalCache<karma::GlobalCache>,
        edm::RunCache<karma::RunCache>,
        edm::LuminosityBlockCache<karma::LumiCache>,
        edm::BeginLuminosityBlockProducer,
        edm::BeginRunProducer> {

      public:
        explicit EventProducer(const edm::ParameterSet&, const karma::GlobalCache*);
        ~EventProducer();

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


        // -- global cache extension
        static std::unique_ptr<karma::GlobalCache> initializeGlobalCache(const edm::ParameterSet& pSet);
        static void globalEndJob(const karma::GlobalCache*) {/* noop */};

        // -- run cache extension
        static std::shared_ptr<karma::RunCache> globalBeginRun(const edm::Run&, const edm::EventSetup&, const GlobalCache*);
        static void globalEndRun(const edm::Run&, const edm::EventSetup&, const RunContext*) {/* noop */};

        // -- lumi cache extension
        static std::shared_ptr<karma::LumiCache> globalBeginLuminosityBlock(const edm::LuminosityBlock&, const edm::EventSetup&, const RunContext*);
        static void globalEndLuminosityBlock(const edm::LuminosityBlock&, const edm::EventSetup&, const LuminosityBlockContext*) {/* noop */};


        // -- begin lumi producer extension
        static void globalBeginLuminosityBlockProduce(edm::LuminosityBlock&, const edm::EventSetup&, const LuminosityBlockContext*);

        // -- begin run producer extension
        static void globalBeginRunProduce(edm::Run&, const edm::EventSetup&, const RunContext*);

        // -- "regular" per-Event 'produce' method
        virtual void produce(edm::Event&, const edm::EventSetup&);


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        std::unique_ptr<HLTPrescaleProvider> m_hltPrescaleProvider;

        // -- handles and tokens
        typename edm::Handle<edm::View<pat::Jet>> jetCollectionHandle;
        edm::EDGetTokenT<edm::View<pat::Jet>> jetCollectionToken;

        typename edm::Handle<edm::View<pat::Electron>> electronCollectionHandle;
        edm::EDGetTokenT<edm::View<pat::Electron>> electronCollectionToken;

        typename edm::Handle<edm::View<reco::GsfElectron>> electronCollection2Handle;
        edm::EDGetTokenT<edm::View<reco::GsfElectron>> electronCollection2Token;

        typename edm::Handle<edm::ValueMap<bool>> electronIDBoolValueMapHandle;
        edm::EDGetTokenT<edm::ValueMap<bool>> electronIDBoolValueMapToken;

        typename edm::Handle<edm::TriggerResults> triggerResultsHandle;
        edm::EDGetTokenT<edm::TriggerResults> triggerResultsToken;

        //typename edm::Handle<pat::PackedTriggerPrescales> triggerPrescalesHandle;
        //edm::EDGetTokenT<pat::PackedTriggerPrescales> triggerPrescalesToken;

        typename edm::Handle<double> pileupDensityHandle;
        edm::EDGetTokenT<double> pileupDensityToken;

        typename edm::Handle<edm::View<PileupSummaryInfo>> pileupSummaryInfosHandle;
        edm::EDGetTokenT<edm::View<PileupSummaryInfo>> pileupSummaryInfosToken;

        typename edm::Handle<edm::View<reco::Vertex>> primaryVerticesHandle;
        edm::EDGetTokenT<edm::View<reco::Vertex>> primaryVerticesToken;

        typename edm::Handle<edm::View<reco::Vertex>> goodPrimaryVerticesHandle;
        edm::EDGetTokenT<edm::View<reco::Vertex>> goodPrimaryVerticesToken;



    };

    //
    // constants, enums and typedefs
    //


    //
    // static data member definitions
    //

}  // end namespace
