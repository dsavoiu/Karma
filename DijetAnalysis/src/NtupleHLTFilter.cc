#include "Karma/Common/interface/Filters/NtupleFilterBase.h"

#include "Karma/DijetAnalysisFormats/interface/Ntuple.h"


namespace dijet {

    /**
     *  NtupleHLTFilter : passes event if at least one of the trigger bits is set
     */
    class NtupleHLTFilter : public karma::NtupleFilterBase<dijet::NtupleEntry> {

      public:
        explicit NtupleHLTFilter(const edm::ParameterSet& config) : NtupleFilterBase<dijet::NtupleEntry>(config) {
            // -- process configuration

        }
        ~NtupleHLTFilter() {};

        // -- called by 'filter' method, once per-Event
        virtual bool filterNtupleEntry(const dijet::NtupleEntry& ntupleEntry) {

            // ensure that at least one trigger fired
            return (ntupleEntry.hltBits != 0);
        }

      private:

    };
}  // end namespace


//define this as a plug-in
using DijetNtupleHLTFilter = dijet::NtupleHLTFilter;
DEFINE_FWK_MODULE(DijetNtupleHLTFilter);
