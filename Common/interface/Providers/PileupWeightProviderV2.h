#include <memory>
#include <map>

#include "TH1D.h"


namespace karma {
    // helper enum

    enum PileupVariation { central = 0, up = 1, down = 2 };

    /* Analogous to `PileupWeightProvider`, but accepts separate ROOT files for the PU profiles of the numerator and denominator */
    class PileupWeightProviderV2 {
      public:

        PileupWeightProviderV2(std::string numeratorRootFileName, std::string denominatorRootFileName, std::string pileupHistogramName);
        ~PileupWeightProviderV2() {};

        const double getPileupWeight(const double nPUMean, PileupVariation var);

      private:

        std::map<PileupVariation, std::unique_ptr<TH1D>> pileupWeightHistograms_;
    };
}
