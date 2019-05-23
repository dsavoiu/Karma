#include <memory>

#include "TH1D.h"


namespace karma {
    class PileupWeightProvider {
      public:

        PileupWeightProvider(std::string rootFileName, std::string pileupWeightHistogramName);
        ~PileupWeightProvider() {};

        const double getPileupWeight(const double nPUMean);

      private:

        std::unique_ptr<TH1D> pileupWeightHistogram_;
    };
}
