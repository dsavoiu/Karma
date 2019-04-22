#include "Karma/Skimming/interface/TriggerObjectCollectionProducer.h"


void karma::TriggerObjectCollectionProducer::produceSingle(const pat::TriggerObjectStandAlone& in, karma::TriggerObject& out, const edm::Event& event, const edm::EventSetup& setup) {

    // populate the output object
    out.p4 = in.p4();
    out.types = in.triggerObjectTypes();

    // unpack trigger path information in input trigger object
    const_cast<pat::TriggerObjectStandAlone&>(in).unpackPathNames(event.triggerNames(*this->triggerResultsHandle_));

    // use trigger path information in karmaEvent
    // and 'pathL3FilterAccepted'
    for (const auto& triggeredPathName : in.pathNames()) {
        for (size_t iPath = 0; iPath < this->karmaRunHandle_->triggerPathInfos.size(); ++iPath) {
            const auto& pathInfo = this->karmaRunHandle_->triggerPathInfos[iPath];
            if (pathInfo.name_ == triggeredPathName) {
                out.assignedPathIndices.emplace_back(iPath);
                break;
            }
        }
    }

    // // use trigger filter information in karmaEvent
    // for (const auto& triggeredFilterName : in.filterLabels()) {
    //     for (size_t iPath = 0; iPath < this->karmaRunHandle_->triggerPathInfos.size(); ++iPath) {
    //         const auto& pathInfo = this->karmaRunHandle_->triggerPathInfos[iPath];
    //         for (const auto& filterName : pathInfo.filterNames_) {
    //             if (filterName == triggeredFilterName) {
    //                 out.filterNames.emplace_back(filterName);
    //             }
    //         }
    //     }
    // }
}


//define this as a plug-in
using karma::TriggerObjectCollectionProducer;
DEFINE_FWK_MODULE(TriggerObjectCollectionProducer);
