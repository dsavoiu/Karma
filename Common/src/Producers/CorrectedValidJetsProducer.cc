#include "Karma/Common/interface/Producers/CorrectedValidJetsProducer.h"

// -- constructor
karma::CorrectedValidJetsProducer::CorrectedValidJetsProducer(const edm::ParameterSet& config, const karma::CorrectedValidJetsProducerGlobalCache*) : m_configPSet(config) {
    // -- register products
    produces<karma::JetCollection>();

    // -- process configuration

    // -- declare which collections are consumed and create tokens
    karmaEventToken = consumes<karma::Event>(m_configPSet.getParameter<edm::InputTag>("karmaEventSrc"));
    karmaJetCollectionToken = consumes<karma::JetCollection>(m_configPSet.getParameter<edm::InputTag>("karmaJetCollectionSrc"));

    // set up a FactorizedJetCorrector (one per stream)
    const auto& jec = m_configPSet.getParameter<std::string>("jecVersion");
    const auto& jecAlgoName = m_configPSet.getParameter<std::string>("jecAlgoName");
    const auto& jecLevels = m_configPSet.getParameter<std::vector<std::string>>("jecLevels");

    std::vector<JetCorrectorParameters> jecParameters;
    for (const auto& jecLevel : jecLevels) {
        jecParameters.push_back(
            JetCorrectorParameters(
                jec + "_" + jecLevel + "_" + jecAlgoName + ".txt"
            )
        );
        std::cout << "[CorrectedValidJetsProducer] Loaded JEC file '" <<
                     jec << "_" << jecLevel << "_" << jecAlgoName << ".txt" << "'" << std::endl;
    }
    m_jetCorrector = std::unique_ptr<FactorizedJetCorrector>(new FactorizedJetCorrector(jecParameters));

    // set up a separate L1 corrector (needed for type-I MET)
    m_jetCorrector_L1 = std::unique_ptr<FactorizedJetCorrector>(
        new FactorizedJetCorrector({
            JetCorrectorParameters(
                jec + "_L1FastJet_" + jecAlgoName + ".txt"
            )
        })
    );
    // set up a separate L1RC corrector (needed for type-I MET)
    m_jetCorrector_L1RC = std::unique_ptr<FactorizedJetCorrector>(
        new FactorizedJetCorrector({
            JetCorrectorParameters(
                jec + "_L1RC_" + jecAlgoName + ".txt"
            )
        })
    );

    // set up a JetCorrectionUncertainty (one per stream)
    m_jecUncertaintyShift = m_configPSet.getParameter<double>("jecUncertaintyShift");
    m_jetCorrectionUncertainty = std::unique_ptr<JetCorrectionUncertainty>(new JetCorrectionUncertainty(
        jec + "_Uncertainty_" + jecAlgoName + ".txt"
    ));
    std::cout << "[CorrectedValidJetsProducer] Loaded JEU file '" <<
                 jec << "_Uncertainty_" << jecAlgoName << ".txt" << "'" << std::endl;
}


// -- destructor
karma::CorrectedValidJetsProducer::~CorrectedValidJetsProducer() {
}


// -- static member functions

/*static*/ std::unique_ptr<karma::CorrectedValidJetsProducerGlobalCache> karma::CorrectedValidJetsProducer::initializeGlobalCache(const edm::ParameterSet& pSet) {
    // -- create the GlobalCache
    return std::unique_ptr<karma::CorrectedValidJetsProducerGlobalCache>(new karma::CorrectedValidJetsProducerGlobalCache(pSet));
}


// -- member functions

void karma::CorrectedValidJetsProducer::produce(edm::Event& event, const edm::EventSetup& setup) {
    std::unique_ptr<karma::JetCollection> outputJetCollection(new karma::JetCollection());

    // -- get object collections for event

    // pileup density
    karma::util::getByTokenOrThrow(event, this->karmaEventToken, this->karmaEventHandle);
    // jet collection
    karma::util::getByTokenOrThrow(event, this->karmaJetCollectionToken, this->karmaJetCollectionHandle);

    // -- populate outputs

    for (const auto& inputJet : (*this->karmaJetCollectionHandle)) {
        // reject jets which do not pass JetID (if requested)
        if (globalCache()->jetIDProvider_ && !globalCache()->jetIDProvider_->getJetID(inputJet))
            continue;

        // setup of FactorizedJetCorrector and JetCorrectionUncertainty
        setupFactorizedJetCorrector(*m_jetCorrector, *this->karmaEventHandle, inputJet);
        setupFactorizedJetCorrector(*m_jetCorrector_L1, *this->karmaEventHandle, inputJet);
        setupFactorizedJetCorrector(*m_jetCorrector_L1RC, *this->karmaEventHandle, inputJet);
        setupFactorProvider(*m_jetCorrectionUncertainty, inputJet);

        // copy jet to output
        outputJetCollection->push_back(inputJet);

        // write out L1-corrected p4 explicitly
        outputJetCollection->back().transientLVs_["L1"] = outputJetCollection->back().uncorP4 * m_jetCorrector_L1->getCorrection();
        outputJetCollection->back().transientLVs_["L1RC"] = outputJetCollection->back().uncorP4 * m_jetCorrector_L1RC->getCorrection();

        // apply correction and uncertainty shift to output jet
        outputJetCollection->back().p4 = outputJetCollection->back().uncorP4 * m_jetCorrector->getCorrection();
        outputJetCollection->back().p4 *= (1.0 + m_jecUncertaintyShift * m_jetCorrectionUncertainty->getUncertainty(/*bool direction = */ m_jecUncertaintyShift > 0.0));

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


void karma::CorrectedValidJetsProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using KarmaCorrectedValidJetsProducer = karma::CorrectedValidJetsProducer;
DEFINE_FWK_MODULE(KarmaCorrectedValidJetsProducer);
