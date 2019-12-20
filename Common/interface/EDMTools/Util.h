#pragma once

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/Registry.h"
#include "FWCore/Utilities/interface/EDMException.h"
#include "FWCore/Utilities/interface/ProductLabels.h"

#include "DataFormats/Provenance/interface/ProcessHistory.h"


namespace karma {
    namespace util {

        /**
         * Tries to get a product by token. Succeeds or throws an edm::Exception.
         * 'consumer' can be e.g. an edm::Event.
         */
        template<typename ConsumerType, typename ProductType>
        void getByTokenOrThrow(const ConsumerType& consumer, const edm::EDGetTokenT<ProductType>& token, edm::Handle<ProductType>& handle) {

            bool obtained = consumer.getByToken(token, handle);
            if (!obtained) {
                edm::Exception exception(edm::errors::ProductNotFound);

                edm::ProductLabels labels;
                consumer.labelsForToken(token, labels);

                exception << "Found zero products matching all criteria: " << std::endl;
                exception << "    module = " << labels.module << std::endl;
                exception << "    productInstance = " << labels.productInstance << std::endl;
                exception << "    process = " << labels.process << std::endl;
                throw exception;
            }

        }

        /**
         * Retrieve the ParameterSet used to configure a Process in the given
         * ProcessHistory.
         */
        inline const edm::ParameterSet& getProcessParameterSetFromHistory(
            const edm::ProcessHistory& processHistory,
            const std::string& processName) {

            // retrieve the process configuration from the process history
            edm::ProcessConfiguration processConfig;
            processHistory.getConfigurationForProcess(processName, processConfig);

            // retrieve the parameter set from the process configuration
            const edm::ParameterSetID& processPSetID = processConfig.parameterSetID();
            const edm::ParameterSet* processPSet = edm::pset::Registry::instance()->getMapped(processPSetID);
            if (!processPSet) {
                edm::Exception exception(edm::errors::NotFound);

                exception << "Cannot retrieve process configuration from history for process: " << processName;
                throw exception;
            }

            return *processPSet;
        }

        /**
         * Retrieve a parameter from the configuration of a process in the process
         * history of a consumer.
         * 'consumer' can be e.g. an edm::Event or an edm::Run;
         * 'processName' is the name of the CMSSW process;
         * 'moduleName' is the name of the module from whose config to retrieve the parameter;
         * 'parameterName' is the name of the parameter to retrieve.
         */
        template<typename ParameterType, typename ConsumerType>
        const ParameterType getModuleParameterFromHistory(
            const ConsumerType& consumer,
            const std::string& processName,
            const std::string& moduleName,
            const std::string& parameterName) {

            // retrieve the consumer process history
            const edm::ProcessHistory& processHistory = consumer.processHistory();

            const edm::ParameterSet& processPSet = karma::util::getProcessParameterSetFromHistory(
                processHistory, processName);

            // retrieve the module configuration ParameterSet from the process configuration
            const edm::ParameterSet& pSet = processPSet.getParameterSet(moduleName);

            // retrieve the parameter from the module configuration
            return pSet.getParameter<ParameterType>(parameterName);
        }
    }
}
