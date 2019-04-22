// system include files
#include <iostream>

#include "Karma/Skimming/interface/GeneratorQCDInfoProducer.h"

// -- constructor
karma::GeneratorQCDInfoProducer::GeneratorQCDInfoProducer(const edm::ParameterSet& config) : m_configPSet(config) {
    // -- register products
    produces<karma::GeneratorQCDInfo>();

    // -- process configuration

    // -- declare which collections are consumed and create tokens
    genEventInfoProductToken = consumes<GenEventInfoProduct>(m_configPSet.getParameter<edm::InputTag>("genEventInfoProductSrc"));

}


// -- destructor
karma::GeneratorQCDInfoProducer::~GeneratorQCDInfoProducer() {
}



// -- member functions

void karma::GeneratorQCDInfoProducer::produce(edm::Event& event, const edm::EventSetup& setup) {
    //std::unique_ptr<karma::Event> karmaEvent(new karma::Event());
    std::unique_ptr<karma::GeneratorQCDInfo> outputGeneratorQCDInfo(new karma::GeneratorQCDInfo());

    // -- get object collections for event
    bool obtained = true;
    // pileup density
    obtained &= event.getByToken(this->genEventInfoProductToken, this->genEventInfoProductHandle);

    assert(obtained);  // raise if one collection could not be obtained

    // -- populate outputs

    outputGeneratorQCDInfo->weight = this->genEventInfoProductHandle->weight();
    outputGeneratorQCDInfo->weightProduct = this->genEventInfoProductHandle->weightProduct();
    outputGeneratorQCDInfo->binningValues = this->genEventInfoProductHandle->binningValues();

    if (this->genEventInfoProductHandle->hasPDF()) {
        // parton flavors (PDG IDs)
        outputGeneratorQCDInfo->parton1PdgId = this->genEventInfoProductHandle->pdf()->id.first;
        outputGeneratorQCDInfo->parton2PdgId = this->genEventInfoProductHandle->pdf()->id.second;

        // parton Bjorken-X
        outputGeneratorQCDInfo->parton1x = this->genEventInfoProductHandle->pdf()->x.first;
        outputGeneratorQCDInfo->parton2x = this->genEventInfoProductHandle->pdf()->x.second;

        // parton Bjorken-X * PDF value
        outputGeneratorQCDInfo->parton1xPDF = this->genEventInfoProductHandle->pdf()->xPDF.first;
        outputGeneratorQCDInfo->parton2xPDF = this->genEventInfoProductHandle->pdf()->xPDF.second;

        // scale information
        outputGeneratorQCDInfo->scalePDF = this->genEventInfoProductHandle->pdf()->scalePDF;  // Q value used in PDF evolution.
    }
    outputGeneratorQCDInfo->alphaQCD = this->genEventInfoProductHandle->alphaQCD();

    // move outputs to event tree
    event.put(std::move(outputGeneratorQCDInfo));
}


void karma::GeneratorQCDInfoProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using karma::GeneratorQCDInfoProducer;
DEFINE_FWK_MODULE(GeneratorQCDInfoProducer);
