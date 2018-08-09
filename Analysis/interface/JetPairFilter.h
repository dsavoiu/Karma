#pragma once

#include "DijetAnalysis/Analysis/interface/NtupleFilterBase.h"


namespace dijet {

    // -- main filter

    class JetPairFilter : public NtupleFilterBase {

      public:
        explicit JetPairFilter(const edm::ParameterSet&);
        ~JetPairFilter();

        // -- 'filter' method, called once per-Event
        virtual bool filterNtupleEntry(const dijet::NtupleEntry&);


      private:

    };
}  // end namespace
