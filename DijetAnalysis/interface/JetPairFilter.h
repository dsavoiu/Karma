#pragma once

#include "Karma/Common/interface/Filters/NtupleFilterBase.h"

#include "Karma/DijetAnalysisFormats/interface/Ntuple.h"
#include "Karma/DijetAnalysisFormats/interface/NtupleV2.h"


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

    class JetPairFilterV2 : public karma::NtupleFilterBase<dijet::NtupleV2Entry> {

      public:
        explicit JetPairFilterV2(const edm::ParameterSet&);
        ~JetPairFilterV2();

        // -- 'filter' method, called once per-Event
        virtual bool filterNtupleEntry(const dijet::NtupleV2Entry&);


      private:

    };
}  // end namespace
