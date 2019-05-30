#pragma once

#include "Karma/Common/interface/Filters/NtupleFilterBase.h"

#include "Karma/DijetAnalysisFormats/interface/Ntuple.h"


namespace dijet {

    // -- main filter

    class LeadingJetPtFilter : public karma::NtupleFilterBase<dijet::NtupleEntry> {

      public:
        explicit LeadingJetPtFilter(const edm::ParameterSet&);
        ~LeadingJetPtFilter();

        // -- 'filter' method, called once per-Event
        virtual bool filterNtupleEntry(const dijet::NtupleEntry&);


      private:
        double minJetPt_;
    };
}  // end namespace
