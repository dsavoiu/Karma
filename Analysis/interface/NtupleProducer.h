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

    // -- main producer

    class NtupleProducer : public edm::stream::EDProducer<> {

      public:
        explicit NtupleProducer(const edm::ParameterSet&);
        ~NtupleProducer();

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        // -- "regular" per-Event 'produce' method
        virtual void produce(edm::Event&, const edm::EventSetup&);


      private:

        // -- helper methods

        dijet::HLTAssignment getHLTAssignment(unsigned int jetIndex);

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

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
