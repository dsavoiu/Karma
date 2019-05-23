#pragma once

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Utilities/interface/EDMException.h"
#include "FWCore/Utilities/interface/ProductLabels.h"


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

    }
}
