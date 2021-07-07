#include <memory>

#include "TH1D.h"


namespace karma {
    /* Analogous to `PileupWeightProvider`, but accepts separate ROOT files for the PU profiles of the numerator and denominator */
    class PileupWeightProviderV2 {
      public:

        PileupWeightProviderV2(std::string numeratorRootFileName, std::string denominatorRootFileName, std::string pileupHistogramName);
        ~PileupWeightProviderV2() {};

        const double getPileupWeight(const double nPUMean);

      private:

        std::unique_ptr<TH1D> pileupWeightHistogram_;
    };
}
