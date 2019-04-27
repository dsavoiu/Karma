#pragma once

#include "Karma/DijetAnalysis/interface/NtupleFilterBase.h"


namespace dijet {

    // -- main filter

    class LeadingJetRapidityFilter : public NtupleFilterBase {

      public:
        explicit LeadingJetRapidityFilter(const edm::ParameterSet&);
        ~LeadingJetRapidityFilter();

        // -- 'filter' method, called once per-Event
        virtual bool filterNtupleEntry(const dijet::NtupleEntry&);


      private:
        double maxJetAbsRapidity_;
    };
}  // end namespace
