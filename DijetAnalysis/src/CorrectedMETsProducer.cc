#include "Karma/DijetAnalysis/interface/CorrectedMETsProducer.h"

// -- constructor
dijet::CorrectedMETsProducer::CorrectedMETsProducer(const edm::ParameterSet& config) :
    m_configPSet(config),
    typeICorrectionMinJetPt_(m_configPSet.getParameter<double>("typeICorrectionMinJetPt")) {

    // -- register products
    produces<karma::METCollection>();

    // -- process configuration

    // -- declare which collections are consumed and create tokens
    karmaEventToken = consumes<karma::Event>(m_configPSet.getParameter<edm::InputTag>("karmaEventSrc"));
    karmaMETCollectionToken = consumes<karma::METCollection>(m_configPSet.getParameter<edm::InputTag>("karmaMETCollectionSrc"));
    karmaCorrectedJetCollectionToken = consumes<karma::JetCollection>(m_configPSet.getParameter<edm::InputTag>("karmaCorrectedJetCollectionSrc"));
}


// -- destructor
dijet::CorrectedMETsProducer::~CorrectedMETsProducer() {
}


// -- member functions

void dijet::CorrectedMETsProducer::produce(edm::Event& event, const edm::EventSetup& setup) {
    std::unique_ptr<karma::METCollection> outputMETCollection(new karma::METCollection());

    // -- get object collections for event

    // pileup density
    karma::util::getByTokenOrThrow(event, this->karmaEventToken, this->karmaEventHandle);
    // MET collection
    karma::util::getByTokenOrThrow(event, this->karmaMETCollectionToken, this->karmaMETCollectionHandle);
    // jet collection
    karma::util::getByTokenOrThrow(event, this->karmaCorrectedJetCollectionToken, this->karmaCorrectedJetCollectionHandle);

    assert(this->karmaMETCollectionHandle->size() == 1);  // only allow MET collections containing a single MET object

    // calculate Type-I correction (https://twiki.cern.ch/twiki/bin/view/CMS/METType1Type2Formulae#3_The_Type_I_correction)
    double sumEtCorrectionTypeI = 0;
    karma::LorentzVector metCorrectionTypeI;
    for (const auto& jet : (*this->karmaCorrectedJetCollectionHandle)) {
        // skip jets with corrected pT below configured threshold
        if (jet.p4.Pt() < typeICorrectionMinJetPt_)
            continue;

        // apply Type-I correction to MET and scalar ET sum
        metCorrectionTypeI += (jet.p4CorrL1 - jet.p4);
        sumEtCorrectionTypeI += metCorrectionTypeI.Pt();
    }

    // -- populate outputs

    // copy uncorrected MET to output
    outputMETCollection->push_back(this->karmaMETCollectionHandle->at(0));
    karma::MET& outputMET = outputMETCollection->back();

    // apply type-I MET correction
    outputMET.p4 += metCorrectionTypeI;
    outputMET.sumEt += sumEtCorrectionTypeI;

    // move outputs to event tree
    event.put(std::move(outputMETCollection));
}


void dijet::CorrectedMETsProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using dijet::CorrectedMETsProducer;
DEFINE_FWK_MODULE(CorrectedMETsProducer);
