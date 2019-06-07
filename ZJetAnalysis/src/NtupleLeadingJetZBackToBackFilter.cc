#include "TMath.h"
#include <cmath>

#include "Karma/Common/interface/Filters/NtupleFilterBase.h"

#include "Karma/ZJetAnalysisFormats/interface/Ntuple.h"


namespace zjet {

    /**
     *  NtupleHLTFilter : passes event if at least one of the trigger bits is set
     */
    class NtupleLeadingJetZBackToBackFilter : public karma::NtupleFilterBase<zjet::NtupleEntry> {

      public:
        explicit NtupleLeadingJetZBackToBackFilter(const edm::ParameterSet& config) :
          NtupleFilterBase<zjet::NtupleEntry>(config),
          maxDeltaPhi_(config.getParameter<double>("maxDeltaPhi")) {};
        ~NtupleLeadingJetZBackToBackFilter() {};

        // -- called by 'filter' method, once per-Event
        virtual bool filterNtupleEntry(const zjet::NtupleEntry& ntupleEntry) {

            // ensure "distance" from perfect back-to-back topology is below threshold
            return (getDistanceOfDeltaPhiFromPi(ntupleEntry.jet1Phi, ntupleEntry.zPhi) < maxDeltaPhi_);
        }

      private:

        double maxDeltaPhi_;

        static inline double getDistanceOfDeltaPhiFromPi(double phi1, double phi2) {
            return std::fabs(std::fmod(std::fabs(phi1 - phi2), 2*TMath::Pi()) - TMath::Pi());
        }
    };
}  // end namespace


//define this as a plug-in
using ZJetNtupleLeadingJetZBackToBackFilter = zjet::NtupleLeadingJetZBackToBackFilter;
DEFINE_FWK_MODULE(ZJetNtupleLeadingJetZBackToBackFilter);
