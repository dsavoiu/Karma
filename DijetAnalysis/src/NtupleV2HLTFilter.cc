#include "Karma/Common/interface/Filters/NtupleFilterBase.h"

#include "Karma/DijetAnalysisFormats/interface/NtupleV2.h"


namespace dijet {

    /**
     *  NtupleV2HLTFilter : passes event if at least one of the trigger bits is set
     */
    class NtupleV2HLTFilter : public karma::NtupleFilterBase<dijet::NtupleV2Entry> {

      public:
        explicit NtupleV2HLTFilter(const edm::ParameterSet& config) : NtupleFilterBase<dijet::NtupleV2Entry>(config) {
            // -- process configuration

        }
        ~NtupleV2HLTFilter() {};

        // -- called by 'filter' method, once per-Event
        virtual bool filterNtupleEntry(const dijet::NtupleV2Entry& ntupleEntry) {

            // ensure that at least one trigger fired
            return (ntupleEntry.triggerResults != 0);
        }

      private:

    };
}  // end namespace


//define this as a plug-in
using DijetNtupleV2HLTFilter = dijet::NtupleV2HLTFilter;
DEFINE_FWK_MODULE(DijetNtupleV2HLTFilter);
