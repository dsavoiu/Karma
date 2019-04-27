#pragma once

#include "Karma/DijetAnalysis/interface/NtupleFilterBase.h"


namespace dijet {

    // -- main filter

    class LeadingJetEtaFilter : public NtupleFilterBase {

      public:
        explicit LeadingJetEtaFilter(const edm::ParameterSet&);
        ~LeadingJetEtaFilter();

        // -- 'filter' method, called once per-Event
        virtual bool filterNtupleEntry(const dijet::NtupleEntry&);


      private:
        double maxJetAbsEta_;
    };
}  // end namespace
