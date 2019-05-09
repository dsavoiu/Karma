// system include files
#include <iostream>

#include "Karma/DijetAnalysis/interface/JetGenJetMatchingProducer.h"

// -- constructor
dijet::JetGenJetMatchingProducer::JetGenJetMatchingProducer(const edm::ParameterSet& config) : m_configPSet(config) {
    // -- register products
    produces<karma::JetGenJetMap>();

    // -- process configuration

    // -- declare which collections are consumed and create tokens
    karmaEventToken = consumes<karma::Event>(m_configPSet.getParameter<edm::InputTag>("karmaEventSrc"));
    karmaJetCollectionToken = consumes<karma::JetCollection>(m_configPSet.getParameter<edm::InputTag>("karmaJetCollectionSrc"));
    karmaGenJetCollectionToken = consumes<karma::LVCollection>(m_configPSet.getParameter<edm::InputTag>("karmaGenJetCollectionSrc"));

    maxDeltaR_ = m_configPSet.getParameter<double>("maxDeltaR");

}


// -- destructor
dijet::JetGenJetMatchingProducer::~JetGenJetMatchingProducer() {
}


// -- member functions

void dijet::JetGenJetMatchingProducer::produce(edm::Event& event, const edm::EventSetup& setup) {

    // -- get object collections for event

    // pileup density
    karma::util::getByTokenOrThrow(event, this->karmaEventToken, this->karmaEventHandle);
    // jet collection
    karma::util::getByTokenOrThrow(event, this->karmaJetCollectionToken, this->karmaJetCollectionHandle);
    // jet collection
    karma::util::getByTokenOrThrow(event, this->karmaGenJetCollectionToken, this->karmaGenJetCollectionHandle);

    // create new AssociationMap (note: need to specify RefProds explicitly here!)
    std::unique_ptr<karma::JetGenJetMap> jetGenJetMap(new karma::JetGenJetMap(
        edm::RefProd<karma::JetCollection>(this->karmaJetCollectionHandle),
        edm::RefProd<karma::LVCollection>(this->karmaGenJetCollectionHandle)
    ));

    // do matching only if collections are not empty
    if ((this->karmaJetCollectionHandle->size() != 0) && (this->karmaGenJetCollectionHandle->size() != 0)) {

        // -- compute delta-R for all recoJet-genJet pairs
        double matDeltaR[this->karmaJetCollectionHandle->size()][this->karmaGenJetCollectionHandle->size()];
        for (size_t iJet = 0; iJet < this->karmaJetCollectionHandle->size(); ++iJet) {
            const auto& recoJet = this->karmaJetCollectionHandle->at(iJet);
            for (size_t iGenJet = 0; iGenJet < this->karmaGenJetCollectionHandle->size(); ++iGenJet) {
                const auto& genJet = this->karmaGenJetCollectionHandle->at(iGenJet);
                const double deltaR = ROOT::Math::VectorUtil::DeltaR(genJet.p4, recoJet.p4);
                if (deltaR <= maxDeltaR_) {
                    matDeltaR[iJet][iGenJet] = deltaR;
                }
                else {
                    matDeltaR[iJet][iGenJet] = std::numeric_limits<double>::quiet_NaN();
                }
            } // end for (genJets)
        } // end for (recoJets)


        // -- do jet-to-trigger-object matching
        for (size_t iIteration = 0; iIteration < this->karmaJetCollectionHandle->size(); ++iIteration) {

            // identify pair of reco and gen indices with best match (lowest overall delta-R)
            int bestMatchRecoJetIndex = -1;
            int bestMatchGenJetIndex = -1;
            double bestMatchDeltaR = std::numeric_limits<double>::quiet_NaN();
            for (size_t iGenJet = 0; iGenJet < this->karmaGenJetCollectionHandle->size(); ++iGenJet) {
                for (size_t iRecoJet = 0; iRecoJet < this->karmaJetCollectionHandle->size(); ++iRecoJet) {

                    // update best match value and indices if better match is found
                    const double& deltaR = matDeltaR[iRecoJet][iGenJet];
                    if (!std::isnan(deltaR)) {
                        if ((deltaR < bestMatchDeltaR) || (std::isnan(bestMatchDeltaR))) {
                            bestMatchRecoJetIndex = iRecoJet;
                            bestMatchGenJetIndex = iGenJet;
                            bestMatchDeltaR = deltaR;
                        }
                    }

                } // end for (recoJets)
            } // end for (genJets)

            // if no best match is found, all reco jets have been matched -> exit
            if (std::isnan(bestMatchDeltaR))
                break;

            // new best match found! -> add to output
            jetGenJetMap->insert(
                edm::Ref<karma::JetCollection>(this->karmaJetCollectionHandle, bestMatchRecoJetIndex),
                edm::Ref<karma::LVCollection>(this->karmaGenJetCollectionHandle, bestMatchGenJetIndex)
            );

            // disallow further matches invoving these indices
            for (size_t iRecoJet = 0; iRecoJet < this->karmaJetCollectionHandle->size(); ++iRecoJet) {
                matDeltaR[iRecoJet][bestMatchGenJetIndex] = std::numeric_limits<double>::quiet_NaN();
            }
            for (size_t iGenJet = 0; iGenJet < this->karmaGenJetCollectionHandle->size(); ++iGenJet) {
                matDeltaR[bestMatchRecoJetIndex][iGenJet] = std::numeric_limits<double>::quiet_NaN();
            }

        } // end for (iterations)
    } // end if (empty)

    // move outputs to event tree
    event.put(std::move(jetGenJetMap));
}


void dijet::JetGenJetMatchingProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using dijet::JetGenJetMatchingProducer;
DEFINE_FWK_MODULE(JetGenJetMatchingProducer);
