#include "Karma/Common/interface/Producers/SmearedJetsProducer.h"

// -- constructor
karma::SmearedJetsProducer::SmearedJetsProducer(const edm::ParameterSet& config) : m_configPSet(config) {
    // -- register products
    produces<karma::JetCollection>();

    // -- process configuration

    // JER-smearing-related options
    const auto& jer = m_configPSet.getParameter<std::string>("jerVersion");
    const auto& jetAlgoName = m_configPSet.getParameter<std::string>("jetAlgoName");
    if (!jer.empty()) {
        std::cout << "[SmearedJetsProducer] Reading JER information from file: " <<
                     jer << "_Uncertainty_" << jetAlgoName << ".txt" << "'" << std::endl;
        m_jetResolutionProvider = std::unique_ptr<JME::JetResolution>(
            new JME::JetResolution(jer + "_PtResolution_" + jetAlgoName + ".txt")
        );
        std::cout << "[SmearedJetsProducer] Reading JER scale factor information from file: " <<
                     jer << "_SF_" << jetAlgoName << ".txt" << "'" << std::endl;
        m_jetResolutionScaleFactorProvider = std::unique_ptr<JME::JetResolutionScaleFactor>(
            new JME::JetResolutionScaleFactor(jer + "_SF_" + jetAlgoName + ".txt")
        );

        int variation = m_configPSet.getParameter<int>("jerVariation");
        if (variation == 0)
            m_jerVariation = Variation::NOMINAL;
        else if (variation == 1)
            m_jerVariation = Variation::UP;
        else if (variation == -1)
            m_jerVariation = Variation::DOWN;
        else
            throw edm::Exception(
                edm::errors::ConfigFileReadError,
                "[SmearedJetsProducer] Invalid value for 'variation' parameter. Only -1, 0 or 1 are supported."
            );

        const auto& jerMethod = m_configPSet.getParameter<std::string>("jerMethod");
        if (jerMethod == "stochastic") m_stochasticOnly = true;
        else if (jerMethod == "hybrid") m_stochasticOnly = false;
        else
            throw edm::Exception(
                edm::errors::ConfigFileReadError,
                "[SmearedJetsProducer] Invalid value for 'jerMethod' parameter. Expected one of: 'hybrid', 'stochastic'."
            );

    }

    // -- declare which collections are consumed and create tokens
    karmaEventToken = consumes<karma::Event>(m_configPSet.getParameter<edm::InputTag>("karmaEventSrc"));
    karmaJetCollectionToken = consumes<karma::JetCollection>(m_configPSet.getParameter<edm::InputTag>("karmaJetCollectionSrc"));
    if (!m_stochasticOnly) {
        karmaJetGenJetMapToken = consumes<karma::JetGenJetMap>(m_configPSet.getParameter<edm::InputTag>("karmaJetGenJetMapSrc"));
    }
}


// -- destructor
karma::SmearedJetsProducer::~SmearedJetsProducer() {
}


// -- member functions

void karma::SmearedJetsProducer::produce(edm::Event& event, const edm::EventSetup& setup) {
    std::unique_ptr<karma::JetCollection> outputJetCollection(new karma::JetCollection());

    // -- get object collections for event

    // pileup density
    karma::util::getByTokenOrThrow(event, this->karmaEventToken, this->karmaEventHandle);
    // jet collection
    karma::util::getByTokenOrThrow(event, this->karmaJetCollectionToken, this->karmaJetCollectionHandle);
    if (!m_stochasticOnly) {
        // jet-genJet match collection
        karma::util::getByTokenOrThrow(event, this->karmaJetGenJetMapToken, this->karmaJetGenJetMapHandle);
    }

    // get random number generator engine
    edm::Service<edm::RandomNumberGenerator> rng;
    CLHEP::HepRandomEngine& rngEngine = rng->getEngine(event.streamID());

    // -- populate outputs

    for (size_t iJet = 0; iJet < this->karmaJetCollectionHandle->size(); ++iJet) {
        // ref to current jet (convenience)
        const auto& inputJet = this->karmaJetCollectionHandle->at(iJet);

        // copy jet to output
        outputJetCollection->push_back(inputJet);

        // retrieve resolution and resolution scale factor
        double resolution = m_jetResolutionProvider->getResolution({
            {JME::Binning::JetPt,  outputJetCollection->back().p4.Pt()},
            {JME::Binning::JetEta, outputJetCollection->back().p4.Eta()},
            {JME::Binning::Rho,    this->karmaEventHandle->rho}
        });
        double resolutionSF = m_jetResolutionScaleFactorProvider->getScaleFactor({
            {JME::Binning::JetEta, outputJetCollection->back().p4.Eta()}
        }, m_jerVariation);

        // poiter to store matched gen jet
        const karma::LV* matchedGenJet = nullptr;

        // if not purely stochastic smearing, try to get matched gen-jet
        if (!m_stochasticOnly) {
            // retrieve matched gen jet (if any)
            matchedGenJet = getMatchedGenJet(iJet);
        }

        // additional matching criterion: pT less than 3-sigma away
        if (matchedGenJet) {
            double ptDiff = outputJetCollection->back().p4.Pt() - matchedGenJet->p4.Pt();
            if (std::abs(ptDiff) > 3 * resolution * outputJetCollection->back().p4.Pt()) {
                matchedGenJet = nullptr;
            }
        }

        // check for valid matched gen jet
        if (matchedGenJet) {
            // matched gen jet valid for JER -> use SCALING smearing
            double ptDiff = outputJetCollection->back().p4.Pt() - matchedGenJet->p4.Pt();
            outputJetCollection->back().p4 *= 1 + (resolutionSF - 1) * ptDiff/outputJetCollection->back().p4.Pt();
        }
        else {
            // matched gen jet invalid for JER -> use STOCHASTIC smearing
            outputJetCollection->back().p4 *= (
                1 + (
                    CLHEP::RandGaussT::shoot(&rngEngine, 0, resolution) *
                    std::sqrt(std::max(resolutionSF * resolutionSF - 1, 0.0))
                )
            );
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


void karma::SmearedJetsProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

/**
 * Helper function to determine which gen jet (if any) can be assigned
 * to a reconstructed jet with a particular index.
 */
const karma::LV* karma::SmearedJetsProducer::getMatchedGenJet(unsigned int jetIndex) {

    const auto& jetMatchedGenJet = this->karmaJetGenJetMapHandle->find(
        edm::Ref<karma::JetCollection>(this->karmaJetCollectionHandle, jetIndex)
    );

    // if there is a gen jet match, return it
    if (jetMatchedGenJet != this->karmaJetGenJetMapHandle->end()) {
        return &(*jetMatchedGenJet->val);
    }

    // if no match, a nullptr is returned
    return nullptr;
}

//define this as a plug-in
using KarmaSmearedJetsProducer = karma::SmearedJetsProducer;
DEFINE_FWK_MODULE(KarmaSmearedJetsProducer);
