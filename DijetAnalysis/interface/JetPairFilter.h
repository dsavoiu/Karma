#pragma once

#include "Karma/Common/interface/Filters/NtupleFilterBase.h"

#include "Karma/DijetAnalysisFormats/interface/Ntuple.h"


namespace dijet {

    // -- main filter

    class JetPairFilter : public karma::NtupleFilterBase<dijet::NtupleEntry> {

      public:
        explicit JetPairFilter(const edm::ParameterSet&);
        ~JetPairFilter();

        // -- 'filter' method, called once per-Event
        virtual bool filterNtupleEntry(const dijet::NtupleEntry&);


      private:

    };
}  // end namespace
