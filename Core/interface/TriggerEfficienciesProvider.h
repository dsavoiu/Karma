#include <map>

#include "TEfficiency.h"
#include "TFile.h"


namespace dijet {
    class TriggerEfficienciesProvider {
      public:

        TriggerEfficienciesProvider(std::string fileName);
        ~TriggerEfficienciesProvider() {};

        const TEfficiency* getEfficiency(const std::string&);

        const std::map<std::string,std::unique_ptr<TEfficiency>>& triggerEfficiencies() {
            return triggerEfficiencies_;
        };

      private:

        std::map<std::string,std::unique_ptr<TEfficiency>> triggerEfficiencies_;

    };
}
