#pragma once

// system include files
#include <memory>
#include <numeric>
#include <algorithm>

#include "Math/VectorUtil.h"

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include <boost/regex.hpp>

#include "Karma/Common/interface/EDMTools/Caches.h"
#include "Karma/Common/interface/EDMTools/Util.h"
#include "Karma/Common/interface/Providers/TriggerEfficienciesProvider.h"
#include "Karma/Common/interface/Providers/NPUMeanProvider.h"
#include "Karma/Common/interface/Providers/JetIDProvider.h"
#include "Karma/Common/interface/Providers/FlexGridBinProvider.h"
#include "Karma/Common/interface/Providers/PileupWeightProvider.h"

// -- output data formats
#include "Karma/DijetAnalysisFormats/interface/Ntuple.h"

// -- input data formats
#include "Karma/SkimmingFormats/interface/Event.h"
#include "Karma/SkimmingFormats/interface/Lumi.h"
#include "Karma/SkimmingFormats/interface/Run.h"

//~ // for karma::JetTriggerObjectMap type
//~ #include "Karma/DijetAnalysis/interface/JetTriggerObjectMatchingProducer.h"


//
// class declaration
//
namespace dijet {

    // alias for representing an array of booleans, one for each trigger path
    typedef std::bitset<8*sizeof(unsigned long)> TriggerBits;

    // -- helper objects

    struct HLTAssignment {
        unsigned int numMatchedTriggerObjects = 0;
        unsigned int numUniqueMatchedTriggerObjects = 0;
        int assignedPathIndex = -1;
        double assignedObjectPt = UNDEFINED_DOUBLE;
    };

    /**
     * Set of bit masks to encode existence of HLT/L1 matches for jets and
     * whether these matches pass the configured thresholds.
     */
    struct TriggerBitsets {
        dijet::TriggerBits hltMatches;
        dijet::TriggerBits hltPassThresholds;
        dijet::TriggerBits l1Matches;
        dijet::TriggerBits l1PassThresholds;
    };

    // -- caches

    /** Cache containing resources which do not change
     *  for the entire duration of the analysis job.
     */
    class NtupleProducerGlobalCache : public karma::CacheBase {

      public:
        NtupleProducerGlobalCache(const edm::ParameterSet& pSet) :
            karma::CacheBase(pSet),
            hltVersionPattern_(boost::regex("(HLT_.*)_v[0-9]+", boost::regex::extended)) {

            /// // create the global trigger efficiencies provider instance
            /// triggerEfficienciesProvider_ = std::unique_ptr<karma::TriggerEfficienciesProvider>(
            ///     new TriggerEfficienciesProvider(m_configPSet.getParameter<std::string>("triggerEfficienciesFile"))
            /// );

            // create list of requested HLT path names
            const auto& hltPathsCfg = pSet_.getParameter<std::vector<edm::ParameterSet>>("hltPaths");
            for (size_t iPath = 0; iPath < hltPathsCfg.size(); ++iPath) {
                const auto& hltPathCfg = hltPathsCfg[iPath];
                hltPaths_.push_back(hltPathCfg.getParameter<std::string>("name"));
                l1Thresholds_.push_back(hltPathCfg.getParameter<double>("l1Threshold"));
                hltThresholds_.push_back(hltPathCfg.getParameter<double>("hltThreshold"));
                hltZeroThresholdMask_[iPath] = (hltPathCfg.getParameter<double>("hltThreshold") == 0);
                l1ZeroThresholdMask_[iPath] = (hltPathCfg.getParameter<double>("l1Threshold") == 0);
            }

            // throw if number of configured paths exceeds size of TTree branch used to store them
            assert(hltPaths_.size() <= 8 * sizeof(unsigned long));

            // if JetID set to 'None', leave jetIDProvider_ as nullptr
            if (pSet_.getParameter<std::string>("jetIDSpec") != "None") {
                jetIDProvider_ = std::unique_ptr<karma::JetIDProvider>(
                    new karma::JetIDProvider(
                        pSet_.getParameter<std::string>("jetIDSpec"),
                        pSet_.getParameter<std::string>("jetIDWorkingPoint")
                    )
                );
            }

        };

        const boost::regex hltVersionPattern_;
        std::vector<std::string> hltPaths_;
        std::vector<double> hltThresholds_;
        std::vector<double> l1Thresholds_;
        // bit *i* is set iff non-zero threshold configured for path with index *i*
        dijet::TriggerBits hltZeroThresholdMask_;
        dijet::TriggerBits l1ZeroThresholdMask_;

        std::unique_ptr<karma::TriggerEfficienciesProvider> triggerEfficienciesProvider_;  // not used (yet?)
        std::unique_ptr<karma::JetIDProvider> jetIDProvider_;

    };


    /** Cache containing resources which do not change
     *  for the entire duration of a run
     */
    class NtupleProducerRunCache : public karma::CacheBase {

      public:
        NtupleProducerRunCache(const edm::ParameterSet& pSet) : karma::CacheBase(pSet) {};

        std::vector<std::string> triggerPathsUnversionedNames_;
        std::vector<int> triggerPathsIndicesInConfig_;

    };

    // -- main producer

    class NtupleProducer : public edm::stream::EDProducer<
        edm::GlobalCache<dijet::NtupleProducerGlobalCache>,
        edm::RunCache<dijet::NtupleProducerRunCache>
    > {

      public:
        explicit NtupleProducer(const edm::ParameterSet&, const dijet::NtupleProducerGlobalCache*);
        ~NtupleProducer();

        // -- global cache extension
        static std::unique_ptr<dijet::NtupleProducerGlobalCache> initializeGlobalCache(const edm::ParameterSet& pSet);
        static void globalEndJob(const dijet::NtupleProducerGlobalCache*) {/* noop */};

        // -- run cache extension
        static std::shared_ptr<dijet::NtupleProducerRunCache> globalBeginRun(const edm::Run&, const edm::EventSetup&, const GlobalCache*);
        static void globalEndRun(const edm::Run&, const edm::EventSetup&, const RunContext*) {/* noop */};

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        // -- "regular" per-Event 'produce' method
        virtual void produce(edm::Event&, const edm::EventSetup&);


      private:

        // -- helper methods

        dijet::HLTAssignment getHLTAssignment(unsigned int jetIndex);
        const karma::LV* getMatchedGenJet(unsigned int jetIndex);
        dijet::TriggerBitsets getTriggerBitsetsForJet(unsigned int jetIndex);
        dijet::TriggerBitsets getTriggerBitsetsForLeadingJetPair();

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;
        bool m_isData;
        double m_weightForStitching;

        /// std::unique_ptr<karma::TriggerEfficienciesProvider> m_triggerEfficienciesProvider;
        std::unique_ptr<karma::NPUMeanProvider> m_npuMeanProvider;
        std::unique_ptr<karma::FlexGridBinProvider> m_flexGridBinProviderDijetPtAve;
        std::unique_ptr<karma::FlexGridBinProvider> m_flexGridBinProviderDijetMass;
        std::unique_ptr<karma::PileupWeightProvider> m_puWeightProvider;

        // -- handles and tokens
        typename edm::Handle<karma::Event> karmaEventHandle;
        edm::EDGetTokenT<karma::Event> karmaEventToken;

        typename edm::Handle<karma::VertexCollection> karmaVertexCollectionHandle;
        edm::EDGetTokenT<karma::VertexCollection> karmaVertexCollectionToken;

        typename edm::Handle<karma::JetCollection> karmaJetCollectionHandle;
        edm::EDGetTokenT<karma::JetCollection> karmaJetCollectionToken;

        typename edm::Handle<karma::METCollection> karmaMETCollectionHandle;
        edm::EDGetTokenT<karma::METCollection> karmaMETCollectionToken;

        typename edm::Handle<karma::JetTriggerObjectsMap> karmaJetTriggerObjectsMapHandle;
        edm::EDGetTokenT<karma::JetTriggerObjectsMap> karmaJetTriggerObjectsMapToken;

        typename edm::Handle<karma::JetGenJetMap> karmaJetGenJetMapHandle;
        edm::EDGetTokenT<karma::JetGenJetMap> karmaJetGenJetMapToken;

        typename edm::Handle<karma::GenParticleCollection> karmaGenParticleCollectionHandle;
        edm::EDGetTokenT<karma::GenParticleCollection> karmaGenParticleCollectionToken;

        typename edm::Handle<karma::GeneratorQCDInfo> karmaGeneratorQCDInfoHandle;
        edm::EDGetTokenT<karma::GeneratorQCDInfo> karmaGeneratorQCDInfoToken;

        typename edm::Handle<karma::LVCollection> karmaGenJetCollectionHandle;
        edm::EDGetTokenT<karma::LVCollection> karmaGenJetCollectionToken;

        typename edm::Handle<karma::Run> karmaRunHandle;
        edm::EDGetTokenT<karma::Run> karmaRunToken;

    };
}  // end namespace
