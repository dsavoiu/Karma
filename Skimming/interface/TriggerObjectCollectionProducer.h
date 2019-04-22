#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"

// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include "Karma/SkimmingFormats/interface/Run.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"

namespace karma {

    class TriggerObjectCollectionProducer :
        public karma::CollectionProducerBase<
            /* TInputType =*/ pat::TriggerObjectStandAloneCollection,
            /* TOutputType =*/ karma::TriggerObjectCollection> {

      public:
        explicit TriggerObjectCollectionProducer(const edm::ParameterSet& config) :
            karma::CollectionProducerBase<pat::TriggerObjectStandAloneCollection, karma::TriggerObjectCollection>(config) {

            // this producer needs a karma::Run product so that it can access
            // the active trigger path names
            karmaRunToken_ = this->template consumes<karma::Run, edm::InRun>(
                this->m_configPSet.template getParameter<edm::InputTag>("karmaRunSrc")
            );
            triggerResultsToken_ = this->template consumes<edm::TriggerResults>(
                this->m_configPSet.template getParameter<edm::InputTag>("triggerResultsSrc")
            );
        };
        ~TriggerObjectCollectionProducer() {};


        // need to override produce function to update karmaRun handle
        virtual void produce(edm::Event& event, const edm::EventSetup& setup) {
            // get additional event/run data
            bool obtained = true;
            obtained &= event.getRun().getByToken(this->karmaRunToken_, this->karmaRunHandle_);  // can this be optimized?
            obtained &= event.getByToken(this->triggerResultsToken_, this->triggerResultsHandle_);
            assert(obtained);

            // call "parent" produce function
            karma::CollectionProducerBase<pat::TriggerObjectStandAloneCollection, karma::TriggerObjectCollection>::produce(event, setup);
        };

        virtual void produceSingle(const pat::TriggerObjectStandAlone&, karma::TriggerObject&, const edm::Event&, const edm::EventSetup&);

        inline virtual bool acceptSingle(const pat::TriggerObjectStandAlone& in, const edm::Event& event, const edm::EventSetup& setup) override {
            // // -- check trigger object type (disabled, for now)
            // bool typeAccepted = false;
            // for (const auto& objType : in.triggerObjectTypes()) {
            //     for (const auto& allowedObjType : m_configPSet.getParameter<std::vector<int>>("allowedTriggerObjectTypes")) {
            //         if (objType == allowedObjType) {
            //             typeAccepted = true;  // accept objects with at least one allowed type
            //             break;
            //         }
            //     }
            //     if (typeAccepted) break;
            // }
            //
            // if (!typeAccepted) return false;

            // -- check trigger object path names

            // need to unpack beforehand
            const_cast<pat::TriggerObjectStandAlone&>(in).unpackPathNames(event.triggerNames(*this->triggerResultsHandle_));

            bool pathAccepted = false;
            for (const auto& triggeredPathName : in.pathNames()) {
                for (const auto& pathInfo : this->karmaRunHandle_->triggerPathInfos) {
                    if (pathInfo.name_ == triggeredPathName) {
                        pathAccepted = true;
                        break;
                    }
                }
                if (pathAccepted) break;
            }

            if (!pathAccepted) return false;

            return true;  // accept all not explicitly rejected

        };

      private:
        // -- extra handle and token for karmaRun
        typename edm::Handle<karma::Run> karmaRunHandle_;
        edm::EDGetTokenT<karma::Run> karmaRunToken_;

        // -- extra handle and token for TriggerResults
        typename edm::Handle<edm::TriggerResults> triggerResultsHandle_;
        edm::EDGetTokenT<edm::TriggerResults> triggerResultsToken_;

    };

}  // end namespace
