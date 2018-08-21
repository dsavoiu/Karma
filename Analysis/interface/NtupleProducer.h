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

#include "DijetAnalysis/Core/interface/Caches.h"
#include "DijetAnalysis/Core/interface/TriggerEfficienciesProvider.h"
#include "DijetAnalysis/Core/interface/JetIDProvider.h"

// -- output data formats
#include "DijetAnalysis/AnalysisFormats/interface/Ntuple.h"

// -- input data formats
#include "DijetAnalysis/DataFormats/interface/Event.h"
#include "DijetAnalysis/DataFormats/interface/Lumi.h"
#include "DijetAnalysis/DataFormats/interface/Run.h"

//~ // for dijet::JetTriggerObjectMap type
//~ #include "DijetAnalysis/Analysis/interface/JetTriggerObjectMatchingProducer.h"


//
// class declaration
//
namespace dijet {

    // -- helper objects

    struct HLTAssignment {
        unsigned int numMatchedTriggerObjects = 0;
        unsigned int numUniqueMatchedTriggerObjects = 0;
        int assignedPathIndex = -1;
        double assignedObjectPt = UNDEFINED_DOUBLE;
    };

    // -- caches

    /** Cache containing resources which do not change
     *  for the entire duration of the analysis job.
     */
    class NtupleProducerGlobalCache : public dijet::CacheBase {

      public:
        NtupleProducerGlobalCache(const edm::ParameterSet& pSet) :
            dijet::CacheBase(pSet),
            hltVersionPattern_(boost::regex("(HLT_.*)_v[0-9]+", boost::regex::extended)) {

            // // create the global trigger efficiencies provider instance
            // triggerEfficienciesProvider_ = std::unique_ptr<TriggerEfficienciesProvider>(
            //     new TriggerEfficienciesProvider(m_configPSet.getParameter<std::string>("triggerEfficienciesFile"))
            // );

            // if JetID set to 'None', leave jetIDProvider_ as nullptr
            if (pSet_.getParameter<std::string>("jetIDSpec") != "None") {
                jetIDProvider_ = std::unique_ptr<JetIDProvider>(
                    new JetIDProvider(
                        pSet_.getParameter<std::string>("jetIDSpec"),
                        pSet_.getParameter<std::string>("jetIDWorkingPoint")
                    )
                );
            }

        };

        const boost::regex hltVersionPattern_;

        std::unique_ptr<TriggerEfficienciesProvider> triggerEfficienciesProvider_;  // not used (yet?)
        std::unique_ptr<JetIDProvider> jetIDProvider_;

    };


    /** Cache containing resources which do not change
     *  for the entire duration of a run
     */
    class NtupleProducerRunCache : public dijet::CacheBase {

      public:
        NtupleProducerRunCache(const edm::ParameterSet& pSet) : dijet::CacheBase(pSet) {};

        std::vector<std::string> triggerPathsUnversionedNames_;

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

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        // TODO: move to global cache
        std::unique_ptr<TriggerEfficienciesProvider> m_triggerEfficienciesProvider;

        // -- handles and tokens
        typename edm::Handle<dijet::Event> dijetEventHandle;
        edm::EDGetTokenT<dijet::Event> dijetEventToken;

        typename edm::Handle<dijet::JetCollection> dijetJetCollectionHandle;
        edm::EDGetTokenT<dijet::JetCollection> dijetJetCollectionToken;

        typename edm::Handle<dijet::JetTriggerObjectsMap> dijetJetTriggerObjectsMapHandle;
        edm::EDGetTokenT<dijet::JetTriggerObjectsMap> dijetJetTriggerObjectsMapToken;

        typename edm::Handle<dijet::Run> dijetRunHandle;
        edm::EDGetTokenT<dijet::Run> dijetRunToken;

    };
}  // end namespace
