#include "DijetAnalysis/Analysis/interface/CorrectedMETsProducer.h"

// -- constructor
dijet::CorrectedMETsProducer::CorrectedMETsProducer(const edm::ParameterSet& config) :
    m_configPSet(config),
    typeICorrectionMinJetPt_(m_configPSet.getParameter<double>("typeICorrectionMinJetPt")) {

    // -- register products
    produces<dijet::METCollection>();

    // -- process configuration

    // -- declare which collections are consumed and create tokens
    dijetEventToken = consumes<dijet::Event>(m_configPSet.getParameter<edm::InputTag>("dijetEventSrc"));
    dijetMETCollectionToken = consumes<dijet::METCollection>(m_configPSet.getParameter<edm::InputTag>("dijetMETCollectionSrc"));
    dijetCorrectedJetCollectionToken = consumes<dijet::JetCollection>(m_configPSet.getParameter<edm::InputTag>("dijetCorrectedJetCollectionSrc"));
}


// -- destructor
dijet::CorrectedMETsProducer::~CorrectedMETsProducer() {
}


// -- member functions

void dijet::CorrectedMETsProducer::produce(edm::Event& event, const edm::EventSetup& setup) {
    std::unique_ptr<dijet::METCollection> outputMETCollection(new dijet::METCollection());

    // -- get object collections for event
    bool obtained = true;
    // pileup density
    obtained &= event.getByToken(this->dijetEventToken, this->dijetEventHandle);
    // MET collection
    obtained &= event.getByToken(this->dijetMETCollectionToken, this->dijetMETCollectionHandle);
    // jet collection
    obtained &= event.getByToken(this->dijetCorrectedJetCollectionToken, this->dijetCorrectedJetCollectionHandle);

    assert(obtained);  // raise if one collection could not be obtained
    assert(this->dijetMETCollectionHandle->size() == 1);  // only allow MET collections containing a single MET object

    // calculate Type-I correction (https://twiki.cern.ch/twiki/bin/view/CMS/METType1Type2Formulae#3_The_Type_I_correction)
    double sumEtCorrectionTypeI = 0;
    dijet::LorentzVector metCorrectionTypeI;
    for (const auto& jet : (*this->dijetCorrectedJetCollectionHandle)) {
        // skip jets with corrected pT below configured threshold
        if (jet.p4.Pt() < typeICorrectionMinJetPt_)
            continue;

        // apply Type-I correction to MET and scalar ET sum
        metCorrectionTypeI += (jet.p4CorrL1 - jet.p4);
        sumEtCorrectionTypeI += metCorrectionTypeI.Pt();
    }

    // -- populate outputs

    // copy uncorrected MET to output
    outputMETCollection->push_back(this->dijetMETCollectionHandle->at(0));
    dijet::MET& outputMET = outputMETCollection->back();

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
