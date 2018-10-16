// system include files
#include <iostream>

#include "DijetAnalysis/Analysis/interface/JetGenJetMatchingProducer.h"

// -- constructor
dijet::JetGenJetMatchingProducer::JetGenJetMatchingProducer(const edm::ParameterSet& config) : m_configPSet(config) {
    // -- register products
    produces<dijet::JetGenJetMap>();

    // -- process configuration

    // -- declare which collections are consumed and create tokens
    dijetEventToken = consumes<dijet::Event>(m_configPSet.getParameter<edm::InputTag>("dijetEventSrc"));
    dijetJetCollectionToken = consumes<dijet::JetCollection>(m_configPSet.getParameter<edm::InputTag>("dijetJetCollectionSrc"));
    dijetGenJetCollectionToken = consumes<dijet::LVCollection>(m_configPSet.getParameter<edm::InputTag>("dijetGenJetCollectionSrc"));

    maxDeltaR_ = m_configPSet.getParameter<double>("maxDeltaR");

}


// -- destructor
dijet::JetGenJetMatchingProducer::~JetGenJetMatchingProducer() {
}


// -- member functions

void dijet::JetGenJetMatchingProducer::produce(edm::Event& event, const edm::EventSetup& setup) {

    // -- get object collections for event
    bool obtained = true;
    // pileup density
    obtained &= event.getByToken(this->dijetEventToken, this->dijetEventHandle);
    // jet collection
    obtained &= event.getByToken(this->dijetJetCollectionToken, this->dijetJetCollectionHandle);
    // jet collection
    obtained &= event.getByToken(this->dijetGenJetCollectionToken, this->dijetGenJetCollectionHandle);

    assert(obtained);  // raise if one collection could not be obtained

    // create new AssociationMap (note: need to specify RefProds explicitly here!)
    std::unique_ptr<dijet::JetGenJetMap> jetGenJetMap(new dijet::JetGenJetMap(
        edm::RefProd<dijet::JetCollection>(this->dijetJetCollectionHandle),
        edm::RefProd<dijet::LVCollection>(this->dijetGenJetCollectionHandle)
    ));

    // do matching only if collections are not empty
    if ((this->dijetJetCollectionHandle->size() != 0) && (this->dijetGenJetCollectionHandle->size() != 0)) {

        // -- compute delta-R for all recoJet-genJet pairs
        double matDeltaR[this->dijetJetCollectionHandle->size()][this->dijetGenJetCollectionHandle->size()];
        for (size_t iJet = 0; iJet < this->dijetJetCollectionHandle->size(); ++iJet) {
            const auto& recoJet = this->dijetJetCollectionHandle->at(iJet);
            for (size_t iGenJet = 0; iGenJet < this->dijetGenJetCollectionHandle->size(); ++iGenJet) {
                const auto& genJet = this->dijetGenJetCollectionHandle->at(iGenJet);
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
        for (size_t iIteration = 0; iIteration < this->dijetJetCollectionHandle->size(); ++iIteration) {

            // identify pair of reco and gen indices with best match (lowest overall delta-R)
            int bestMatchRecoJetIndex = -1;
            int bestMatchGenJetIndex = -1;
            double bestMatchDeltaR = std::numeric_limits<double>::quiet_NaN();
            for (size_t iGenJet = 0; iGenJet < this->dijetGenJetCollectionHandle->size(); ++iGenJet) {
                for (size_t iRecoJet = 0; iRecoJet < this->dijetJetCollectionHandle->size(); ++iRecoJet) {

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
                edm::Ref<dijet::JetCollection>(this->dijetJetCollectionHandle, bestMatchRecoJetIndex),
                edm::Ref<dijet::LVCollection>(this->dijetGenJetCollectionHandle, bestMatchGenJetIndex)
            );

            // disallow further matches invoving these indices
            for (size_t iRecoJet = 0; iRecoJet < this->dijetJetCollectionHandle->size(); ++iRecoJet) {
                matDeltaR[iRecoJet][bestMatchGenJetIndex] = std::numeric_limits<double>::quiet_NaN();
            }
            for (size_t iGenJet = 0; iGenJet < this->dijetGenJetCollectionHandle->size(); ++iGenJet) {
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
