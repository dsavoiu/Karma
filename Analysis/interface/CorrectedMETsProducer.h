#pragma once

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

// -- output data formats
#include "DijetAnalysis/DataFormats/interface/Event.h"

// -- input data formats
#include "DijetAnalysis/DataFormats/interface/Event.h"
#include "DijetAnalysis/DataFormats/interface/Lumi.h"
#include "DijetAnalysis/DataFormats/interface/Run.h"


//
// class declaration
//
namespace dijet {
    // -- caches

    // -- main producer

    class CorrectedMETsProducer : public edm::stream::EDProducer<> {

      public:
        explicit CorrectedMETsProducer(const edm::ParameterSet&);
        ~CorrectedMETsProducer();

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        // -- "regular" per-Event 'produce' method
        virtual void produce(edm::Event&, const edm::EventSetup&);


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;
        double typeICorrectionMinJetPt_;

        // -- handles and tokens
        typename edm::Handle<dijet::Event> dijetEventHandle;
        edm::EDGetTokenT<dijet::Event> dijetEventToken;

        typename edm::Handle<dijet::METCollection> dijetMETCollectionHandle;
        edm::EDGetTokenT<dijet::METCollection> dijetMETCollectionToken;

        typename edm::Handle<dijet::JetCollection> dijetCorrectedJetCollectionHandle;
        edm::EDGetTokenT<dijet::JetCollection> dijetCorrectedJetCollectionToken;

    };
}  // end namespace
