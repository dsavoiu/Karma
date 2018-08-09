#pragma once

// system include files
#include <memory>

#include "Math/VectorUtil.h"

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/makeRefToBaseProdFrom.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "DijetAnalysis/Core/interface/Caches.h"

// JEC and JER-related objects
#include "CondFormats/JetMETObjects/interface/FactorizedJetCorrector.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"

// -- output data formats
#include "DataFormats/Common/interface/Ref.h"
#include "DataFormats/Common/interface/AssociationMap.h"

// -- input data formats
#include "DijetAnalysis/DataFormats/interface/Event.h"
#include "DijetAnalysis/DataFormats/interface/Lumi.h"
#include "DijetAnalysis/DataFormats/interface/Run.h"


//
// class declaration
//
namespace dijet {

    // -- main producer

    class JetTriggerObjectMatchingProducer : public edm::stream::EDProducer<> {

      public:
        explicit JetTriggerObjectMatchingProducer(const edm::ParameterSet&);
        ~JetTriggerObjectMatchingProducer();

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        // -- "regular" per-Event 'produce' method
        virtual void produce(edm::Event&, const edm::EventSetup&);


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        double maxDeltaR_;

        // -- handles and tokens
        typename edm::Handle<dijet::Event> dijetEventHandle;
        edm::EDGetTokenT<dijet::Event> dijetEventToken;

        typename edm::Handle<dijet::JetCollection> dijetJetCollectionHandle;
        edm::EDGetTokenT<dijet::JetCollection> dijetJetCollectionToken;

        typename edm::Handle<dijet::TriggerObjectCollection> dijetTriggerObjectCollectionHandle;
        edm::EDGetTokenT<dijet::TriggerObjectCollection> dijetTriggerObjectCollectionToken;

        typename edm::Handle<dijet::Run> dijetRunHandle;
        edm::EDGetTokenT<dijet::Run> dijetRunToken;

    };
}  // end namespace
