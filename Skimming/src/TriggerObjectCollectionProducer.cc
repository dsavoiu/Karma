#include "DijetAnalysis/Skimming/interface/TriggerObjectCollectionProducer.h"


void dijet::TriggerObjectCollectionProducer::produceSingle(const pat::TriggerObjectStandAlone& in, dijet::TriggerObject& out, const edm::Event& event, const edm::EventSetup& setup) {

    // populate the output object
    out.p4 = in.p4();
    out.types = in.triggerObjectTypes();

    // unpack trigger path information in input trigger object
    const_cast<pat::TriggerObjectStandAlone&>(in).unpackPathNames(event.triggerNames(*this->triggerResultsHandle_));

    // use trigger path information in dijetEvent
    // and 'pathL3FilterAccepted'
    for (const auto& triggeredPathName : in.pathNames()) {
        for (size_t iPath = 0; iPath < this->dijetRunHandle_->triggerPathInfos.size(); ++iPath) {
            const auto& pathInfo = this->dijetRunHandle_->triggerPathInfos[iPath];
            if (pathInfo.name_ == triggeredPathName) {
                out.assignedPathIndices.emplace_back(iPath);
                break;
            }
        }
    }

    // // use trigger filter information in dijetEvent
    // for (const auto& triggeredFilterName : in.filterLabels()) {
    //     for (size_t iPath = 0; iPath < this->dijetRunHandle_->triggerPathInfos.size(); ++iPath) {
    //         const auto& pathInfo = this->dijetRunHandle_->triggerPathInfos[iPath];
    //         for (const auto& filterName : pathInfo.filterNames_) {
    //             if (filterName == triggeredFilterName) {
    //                 out.filterNames.emplace_back(filterName);
    //             }
    //         }
    //     }
    // }
}


//define this as a plug-in
using dijet::TriggerObjectCollectionProducer;
DEFINE_FWK_MODULE(TriggerObjectCollectionProducer);
