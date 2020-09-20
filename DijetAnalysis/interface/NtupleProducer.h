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

// for random number generator service
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Utilities/interface/RandomNumberGenerator.h"
#include "CLHEP/Random/RandomEngine.h"
#include "CLHEP/Random/RandFlat.h"

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
            metFilterNames_(pSet.getParameter<std::vector<std::string>>("metFilterNames")),
            doPrescales_(pSet.getParameter<bool>("doPrescales")),
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

            // construct FlexGrid objects with final analysis binning and bin-by-bin metadata
            const auto& flexGridFileDijetPtAve = pSet.getParameter<std::string>("flexGridFileDijetPtAve");
            if (!flexGridFileDijetPtAve.empty()) {
                std::cout << "Reading FlexGrid binning information (pT average) from file: " << flexGridFileDijetPtAve << std::endl;
                flexGridDijetPtAverage_ = std::unique_ptr<FlexGrid>(new FlexGrid(flexGridFileDijetPtAve));
                // assign active trigger path for each bin based on trigger turnon information
                assignActiveTriggerPathIndices(flexGridDijetPtAverage_->_rootFlexNode, "DiPFJetAveTriggers");
            }
            const auto& flexGridFileDijetMass = pSet.getParameter<std::string>("flexGridFileDijetMass");
            if (!flexGridFileDijetMass.empty()) {
                std::cout << "Reading FlexGrid binning information (dijet mass) from file: " << flexGridFileDijetMass << std::endl;
                flexGridDijetDijetMass_ = std::unique_ptr<FlexGrid>(new FlexGrid(flexGridFileDijetMass));
                // assign active trigger path for each bin based on trigger turnon information
                assignActiveTriggerPathIndices(flexGridDijetDijetMass_->_rootFlexNode, "DiPFJetAveTriggers");
            }

        };

        /*
         * Helper function: go through a FlexNode and use 'bins', 'triggers', and 'turnon'
         * information to assign an active trigger path (index) to each bin.
         *
         * For every FlexNode that is a leaf (no further substructure), read in the active
         * trigger information given in the metadata subkey <metadataSubkey> under the keys
         * "triggers" and "turnons" and create a metadata key "activeTriggerPathIndex" that
         * contains the index of the active trigger path.
         */
        inline void assignActiveTriggerPathIndices(FlexNode& node, const std::string& metadataSubkey) {
            if (node.hasSubstructure()) {
                // recurse through the FlexGrid until reaching a node without substructure
                for (auto& subnode : node.getSubstructure()) {
                    assignActiveTriggerPathIndices(subnode, metadataSubkey);
                }
            }
            else {
                // node without substructure -> "unpack" 'triggers' and 'turnons' metadata keys
                // to obtain bin-by-bin active trigger path indices
                auto& metadata = node.getMetadata();
                std::vector<double> turnons = metadata[metadataSubkey]["turnons"].as<std::vector<double>>();
                std::vector<std::string> triggers = metadata[metadataSubkey]["triggers"].as<std::vector<std::string>>();
                std::vector<int> trigerIndices;

                // determine the index of the triggers in the analysis config
                for (const auto& triggerName : triggers) {
                    const auto& it = std::find(hltPaths_.begin(), hltPaths_.end(), triggerName);
                    if (it == triggers.end()) {
                        trigerIndices.emplace_back(-1);
                    }
                    else {
                        trigerIndices.emplace_back(std::distance(hltPaths_.begin(), it));
                    }
                }

                // go through bins, incrementing active trigger path when threshold is reached
                int currentActiveTrigger = -1;
                size_t idxTrigger = 0;
                const auto& binEdges = node.getBins();
                for (size_t i = 0; i < binEdges.size() - 1; ++i) {

                    // increment trigger index to highest-threshold fully efficient path
                    while (turnons[idxTrigger] <= binEdges[i] && idxTrigger < turnons.size()) {
                        currentActiveTrigger = idxTrigger++;  // keep path before last increment active
                    }

                    metadata[metadataSubkey]["activeTriggerPathIndex"].push_back((currentActiveTrigger < 0) ? -1 : trigerIndices[currentActiveTrigger]);
                }
            }
        }

        std::vector<std::string> metFilterNames_;  // list of MET filter names that should be written out
        bool doPrescales_;

        const boost::regex hltVersionPattern_;
        std::vector<std::string> hltPaths_;
        std::vector<double> hltThresholds_;
        std::vector<double> l1Thresholds_;
        // bit *i* is set iff non-zero threshold configured for path with index *i*
        dijet::TriggerBits hltZeroThresholdMask_;
        dijet::TriggerBits l1ZeroThresholdMask_;

        std::unique_ptr<karma::TriggerEfficienciesProvider> triggerEfficienciesProvider_;  // not used (yet?)
        std::unique_ptr<karma::JetIDProvider> jetIDProvider_;

        std::unique_ptr<FlexGrid> flexGridDijetPtAverage_;
        std::unique_ptr<FlexGrid> flexGridDijetDijetMass_;

    };


    /** Cache containing resources which do not change
     *  for the entire duration of a run
     */
    class NtupleProducerRunCache : public karma::CacheBase {

      public:
        NtupleProducerRunCache(const edm::ParameterSet& pSet) : karma::CacheBase(pSet) {};

        std::vector<std::string> triggerPathsUnversionedNames_;
        std::vector<int> triggerPathsIndicesInConfig_;
        std::vector<int> metFilterIndicesInSkim_;

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
        std::unique_ptr<karma::PileupWeightProvider> m_puWeightProviderAlt;

        std::vector<karma::PileupWeightProvider*> m_puWeightProvidersByHLT;

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

        typename edm::Handle<double> karmaPrefiringWeightHandle;
        edm::EDGetTokenT<double> karmaPrefiringWeightToken;

        typename edm::Handle<double> karmaPrefiringWeightUpHandle;
        edm::EDGetTokenT<double> karmaPrefiringWeightUpToken;

        typename edm::Handle<double> karmaPrefiringWeightDownHandle;
        edm::EDGetTokenT<double> karmaPrefiringWeightDownToken;

        typename edm::Handle<karma::Run> karmaRunHandle;
        edm::EDGetTokenT<karma::Run> karmaRunToken;

    };
}  // end namespace
