#pragma once

// system include files
#include "TTree.h"

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "Karma/Common/interface/Analyzers/NtupleFlatOutputAnalyzerBase.h"

// -- output data formats
#include "Karma/DijetAnalysisFormats/interface/Ntuple.h"

//
// class declaration
//
namespace dijet {

    // -- main producer

    class NtupleFlatOutput : public karma::NtupleFlatOutputAnalyzerBase<dijet::NtupleEntry> {

      public:
        explicit NtupleFlatOutput(const edm::ParameterSet& config) :
            NtupleFlatOutputAnalyzerBase<dijet::NtupleEntry>(config),
            // set a flag if we are running on (real) data
            m_isData(m_configPSet.getParameter<bool>("isData")) {};

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        virtual void setUpTTree(TTree* tree, dijet::NtupleEntry* productForFill) override;

      private:

        // ----------member data ---------------------------

        bool m_isData;

    };
}  // end namespace
