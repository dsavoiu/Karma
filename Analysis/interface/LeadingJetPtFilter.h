#pragma once

#include "DijetAnalysis/Analysis/interface/NtupleFilterBase.h"


namespace dijet {

    // -- main filter

    class LeadingJetPtFilter : public NtupleFilterBase {

      public:
        explicit LeadingJetPtFilter(const edm::ParameterSet&);
        ~LeadingJetPtFilter();

        // -- 'filter' method, called once per-Event
        virtual bool filterNtupleEntry(const dijet::NtupleEntry&);


      private:
        double minJetPt_;
    };
}  // end namespace
