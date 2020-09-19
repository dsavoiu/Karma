#include "Karma/Common/interface/Producers/JetUncertaintySourceApplier.h"

// -- constructor
karma::JetUncertaintySourceApplier::JetUncertaintySourceApplier(const edm::ParameterSet& config) : m_configPSet(config) {
    // -- register products
    produces<karma::JetCollection>();

    // -- process configuration

    // retrieve the uncertainty names
    m_jetUncertaintySourceNames = m_configPSet.getParameter<std::vector<std::string>>("jetUncertaintySources");

    // -- declare which collections are consumed and create tokens
    karmaJetCollectionToken = consumes<karma::JetCollection>(m_configPSet.getParameter<edm::InputTag>("karmaJetCollectionSrc"));
}


// -- destructor
karma::JetUncertaintySourceApplier::~JetUncertaintySourceApplier() {
}


// -- member functions

void karma::JetUncertaintySourceApplier::produce(edm::Event& event, const edm::EventSetup& setup) {
    std::unique_ptr<karma::JetCollection> outputJetCollection(new karma::JetCollection());

    // -- get object collections for event

    // jet collection
    karma::util::getByTokenOrThrow(event, this->karmaJetCollectionToken, this->karmaJetCollectionHandle);

    // -- populate outputs

    for (size_t iJet = 0; iJet < this->karmaJetCollectionHandle->size(); ++iJet) {
        // ref to current jet (convenience)
        const auto& inputJet = this->karmaJetCollectionHandle->at(iJet);

        // copy jet to output
        outputJetCollection->push_back(inputJet);

        // potentially reverse the shift by the "Total" JEU (always safe to do this; if not applied factor is 1.0)
        outputJetCollection->back().p4 /= outputJetCollection->back().transientDoubles_["Total"];

        // apply the requested JES uncertainty source shift(s)
        for (const auto& jetUncertaintySourceName : m_jetUncertaintySourceNames) {
            outputJetCollection->back().p4 *= outputJetCollection->back().transientDoubles_[jetUncertaintySourceName];
        }
    }

    // re-sort jets by pT
    std::sort(
        (*outputJetCollection).begin(),
        (*outputJetCollection).end(),
        [](const karma::Jet& jet1, const karma::Jet& jet2) {
            return (jet1.p4.pt() > jet2.p4.pt());
        }
    );

    // move outputs to event tree
    event.put(std::move(outputJetCollection));
}


void karma::JetUncertaintySourceApplier::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
using KarmaJetUncertaintySourceApplier = karma::JetUncertaintySourceApplier;
DEFINE_FWK_MODULE(KarmaJetUncertaintySourceApplier);
