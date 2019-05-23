#include <map>


namespace karma {
    class NPUMeanProvider {
      public:

        NPUMeanProvider(std::string fileName, double minBiasCrossSection);
        ~NPUMeanProvider() {};

        const double getNPUMean(const unsigned long run, const unsigned long luminosityBlock);

      private:

        std::map<unsigned long, std::map<unsigned long, double>> mapRunLumiBlockToNPUMean_;

    };
}
