#include "Karma/Common/interface/JetIDProvider.h"


dijet::JetIDProvider::JetIDProvider(std::string jetIDSpec, std::string jetIDWorkingPoint) {
    boost::algorithm::to_lower(jetIDSpec);  // make lowercase
    if (jetIDSpec == "2016")
        jetID_ = std::unique_ptr<dijet::JetID2016>(new dijet::JetID2016(jetIDWorkingPoint));
    else
        throw std::invalid_argument("Unknown JetID: " + jetIDSpec);

    std::cout << "[JetIDProvider] Succesful init. JetID = '" << jetIDSpec << "', WorkingPoint = '" << jetIDWorkingPoint << "'" << std::endl;
}


bool dijet::JetIDProvider::getJetID(const dijet::Jet& jet) {
    return jetID_->getJetID(jet);
}
