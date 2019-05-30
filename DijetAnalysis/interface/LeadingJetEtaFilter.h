#pragma once

#include "Karma/Common/interface/Filters/NtupleFilterBase.h"

#include "Karma/DijetAnalysisFormats/interface/Ntuple.h"


namespace dijet {

    // -- main filter

    class LeadingJetEtaFilter : public karma::NtupleFilterBase<dijet::NtupleEntry> {

      public:
        explicit LeadingJetEtaFilter(const edm::ParameterSet&);
        ~LeadingJetEtaFilter();

        // -- 'filter' method, called once per-Event
        virtual bool filterNtupleEntry(const dijet::NtupleEntry&);


      private:
        double maxJetAbsEta_;
    };
}  // end namespace
