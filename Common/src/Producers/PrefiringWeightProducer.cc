#include "Karma/Common/interface/Producers/PrefiringWeightProducer.h"

#include "Karma/SkimmingFormats/interface/Event.h"

// -- constructor
karma::PrefiringWeightProducer::PrefiringWeightProducer(const edm::ParameterSet& config) : m_configPSet(config) {
    // -- register products
    produces<double>("nonPrefiringProb").setBranchAlias("nonPrefiringProb");
    produces<double>("nonPrefiringProbUp").setBranchAlias("nonPrefiringProbUp");
    produces<double>("nonPrefiringProbDown").setBranchAlias("nonPrefiringProbDown");

    // -- process configuration

    // -- declare which collections are consumed and create tokens
    karmaJetCollectionToken = consumes<karma::JetCollection>(m_configPSet.getParameter<edm::InputTag>("karmaJetCollectionSrc"));

    const auto& prefiringWeightFilePath = m_configPSet.getParameter<std::string>("prefiringWeightFilePath");
    const auto& prefiringWeightHistName = m_configPSet.getParameter<std::string>("prefiringWeightHistName");
    m_prefiringRateSysUnc = m_configPSet.getParameter<double>("prefiringRateSysUnc");

    // open file containing prefiring weight maps
    TFile* prefiringWeightFile = new TFile(prefiringWeightFilePath.c_str(), "READ");

    // read in the weight maps
    m_prefiringWeightHist = (TH2F*) prefiringWeightFile->Get(prefiringWeightHistName.c_str());

    // check if read successful and throw if not
    if (!m_prefiringWeightHist) {
        throw edm::Exception(
            edm::errors::ConfigFileReadError,
            "[PrefiringWeightProducer] File '" + prefiringWeightFilePath +
            "' does not contain histogram '" + prefiringWeightHistName + "'!"
        );
    }

    // detach ownership of object and close file
    m_prefiringWeightHist->SetDirectory(0);
    prefiringWeightFile->Close();

    m_maxPt = m_prefiringWeightHist->GetYaxis()->GetBinLowEdge(m_prefiringWeightHist->GetNbinsY() + 1);

}


// -- destructor
karma::PrefiringWeightProducer::~PrefiringWeightProducer() {
}


// -- member functions

void karma::PrefiringWeightProducer::produce(edm::Event& event, const edm::EventSetup& setup) {

    // -- get object collections for event

    // jet collection
    karma::util::getByTokenOrThrow(event, this->karmaJetCollectionToken, this->karmaJetCollectionHandle);

    // -- populate outputs

    double nonPrefiringProbability[3] = {1., 1., 1.};  //0: central, 1: up, 2: down

    // logic taken from: https://github.com/cms-sw/cmssw/blob/8706dbe8a09e7e1314f2127288cfc39051851eea/PhysicsTools/PatUtils/plugins/L1ECALPrefiringWeightProducer.cc
    for (const auto var : {PrefiringVariation::central, PrefiringVariation::up, PrefiringVariation::down}) {
        for (const auto& inputJet : (*this->karmaJetCollectionHandle)) {
            if ((inputJet.p4.Pt()  < 20.) ||
                (std::abs(inputJet.p4.Eta()) < 2.0) ||
                (std::abs(inputJet.p4.Eta()) > 3.0)) {

                continue;
            }

            nonPrefiringProbability[var] *= (1. - getPrefiringRate(inputJet.p4.Eta(), inputJet.p4.Pt(), var));

        }
    }

    // move outputs to event tree

    auto nonPrefiringProb       = std::make_unique<double>(nonPrefiringProbability[0]);
    auto nonPrefiringProbUp     = std::make_unique<double>(nonPrefiringProbability[1]);
    auto nonPrefiringProbDown   = std::make_unique<double>(nonPrefiringProbability[2]);

    event.put(std::move(nonPrefiringProb), "nonPrefiringProb");
    event.put(std::move(nonPrefiringProbUp), "nonPrefiringProbUp");
    event.put(std::move(nonPrefiringProbDown), "nonPrefiringProbDown");
}

double karma::PrefiringWeightProducer::getPrefiringRate(double eta, double pt, PrefiringVariation var) {

    // use highest pT bin weight if pT exceeds range
    if (pt >= m_maxPt) {
        pt = m_maxPt - 0.01;
    }

    // find bin for weight
    int thebin = m_prefiringWeightHist->FindBin(eta, pt);

    double prefiringRate = m_prefiringWeightHist->GetBinContent(thebin);
    double prefiringRateStatUnc = m_prefiringWeightHist->GetBinError(thebin);
    double prefiringRateSystUnc = m_prefiringRateSysUnc * prefiringRate;

    if (var == PrefiringVariation::up) {
        prefiringRate = std::min(1., prefiringRate + sqrt(pow(prefiringRateStatUnc, 2) + pow(prefiringRateSystUnc, 2)));
    }
    else if (var == PrefiringVariation::down) {
        prefiringRate = std::max(0., prefiringRate - sqrt(pow(prefiringRateStatUnc, 2) + pow(prefiringRateSystUnc, 2)));
    }

    return prefiringRate;
}

void karma::PrefiringWeightProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
using KarmaPrefiringWeightProducer = karma::PrefiringWeightProducer;
DEFINE_FWK_MODULE(KarmaPrefiringWeightProducer);
