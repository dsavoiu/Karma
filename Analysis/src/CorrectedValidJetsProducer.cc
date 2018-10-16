#include "DijetAnalysis/Analysis/interface/CorrectedValidJetsProducer.h"

// -- constructor
dijet::CorrectedValidJetsProducer::CorrectedValidJetsProducer(const edm::ParameterSet& config, const dijet::CorrectedValidJetsProducerGlobalCache*) : m_configPSet(config) {
    // -- register products
    produces<dijet::JetCollection>();

    // -- process configuration

    // -- declare which collections are consumed and create tokens
    dijetEventToken = consumes<dijet::Event>(m_configPSet.getParameter<edm::InputTag>("dijetEventSrc"));
    dijetJetCollectionToken = consumes<dijet::JetCollection>(m_configPSet.getParameter<edm::InputTag>("dijetJetCollectionSrc"));

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

    // set up a JetCorrectionUncertainty (one per stream)
    m_jecUncertaintyShift = m_configPSet.getParameter<double>("jecUncertaintyShift");
    m_jetCorrectionUncertainty = std::unique_ptr<JetCorrectionUncertainty>(new JetCorrectionUncertainty(
        jec + "_Uncertainty_" + jecAlgoName + ".txt"
    ));
}


// -- destructor
dijet::CorrectedValidJetsProducer::~CorrectedValidJetsProducer() {
}


// -- static member functions

/*static*/ std::unique_ptr<dijet::CorrectedValidJetsProducerGlobalCache> dijet::CorrectedValidJetsProducer::initializeGlobalCache(const edm::ParameterSet& pSet) {
    // -- create the GlobalCache
    return std::unique_ptr<dijet::CorrectedValidJetsProducerGlobalCache>(new dijet::CorrectedValidJetsProducerGlobalCache(pSet));
}


// -- member functions

void dijet::CorrectedValidJetsProducer::produce(edm::Event& event, const edm::EventSetup& setup) {
    std::unique_ptr<dijet::JetCollection> outputJetCollection(new dijet::JetCollection());

    // -- get object collections for event
    bool obtained = true;
    // pileup density
    obtained &= event.getByToken(this->dijetEventToken, this->dijetEventHandle);
    // jet collection
    obtained &= event.getByToken(this->dijetJetCollectionToken, this->dijetJetCollectionHandle);

    assert(obtained);  // raise if one collection could not be obtained

    // -- populate outputs

    for (const auto& inputJet : (*this->dijetJetCollectionHandle)) {
        // reject jets which do not pass JetID (if requested)
        if (globalCache()->jetIDProvider_ && !globalCache()->jetIDProvider_->getJetID(inputJet))
            continue;

        // setup of FactorizedJetCorrector and JetCorrectionUncertainty
        setupFactorizedJetCorrector(*m_jetCorrector, *this->dijetEventHandle, inputJet);
        setupFactorizedJetCorrector(*m_jetCorrector_L1, *this->dijetEventHandle, inputJet);
        setupFactorProvider(*m_jetCorrectionUncertainty, inputJet);

        // copy jet to output
        outputJetCollection->push_back(inputJet);

        // write out L1-corrected p4 explicitly
        outputJetCollection->back().p4CorrL1 = outputJetCollection->back().p4 * m_jetCorrector_L1->getCorrection();

        // apply correction and uncertainty shift to output jet
        outputJetCollection->back().p4 *= m_jetCorrector->getCorrection();
        outputJetCollection->back().p4 *= (1.0 + m_jecUncertaintyShift * m_jetCorrectionUncertainty->getUncertainty(/*bool direction = */ m_jecUncertaintyShift > 0.0));

    }

    // re-sort jets by pT
    std::sort(
        (*outputJetCollection).begin(),
        (*outputJetCollection).end(),
        [](const dijet::Jet& jet1, const dijet::Jet& jet2) {
            return (jet1.p4.pt() > jet2.p4.pt());
        }
    );

    // move outputs to event tree
    event.put(std::move(outputJetCollection));
}


void dijet::CorrectedValidJetsProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using dijet::CorrectedValidJetsProducer;
DEFINE_FWK_MODULE(CorrectedValidJetsProducer);
