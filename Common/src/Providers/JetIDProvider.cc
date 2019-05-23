#include "Karma/Common/interface/Providers/JetIDProvider.h"


karma::JetIDProvider::JetIDProvider(std::string jetIDSpec, std::string jetIDWorkingPoint) {
    boost::algorithm::to_lower(jetIDSpec);  // make lowercase
    if (jetIDSpec == "2016")
        jetID_ = std::unique_ptr<karma::JetID2016>(new karma::JetID2016(jetIDWorkingPoint));
    else
        throw std::invalid_argument("Unknown JetID: " + jetIDSpec);

    std::cout << "[JetIDProvider] Succesful init. JetID = '" << jetIDSpec << "', WorkingPoint = '" << jetIDWorkingPoint << "'" << std::endl;
}


bool karma::JetIDProvider::getJetID(const karma::Jet& jet) {
    return jetID_->getJetID(jet);
}
