#pragma once

#include "Karma/Common/interface/Filters/NtupleFilterBase.h"

#include "Karma/DijetAnalysisFormats/interface/Ntuple.h"


namespace dijet {

    // -- main filter

    class LeadingJetRapidityFilter : public karma::NtupleFilterBase<dijet::NtupleEntry> {

      public:
        explicit LeadingJetRapidityFilter(const edm::ParameterSet&);
        ~LeadingJetRapidityFilter();

        // -- 'filter' method, called once per-Event
        virtual bool filterNtupleEntry(const dijet::NtupleEntry&);


      private:
        double maxJetAbsRapidity_;
    };
}  // end namespace
