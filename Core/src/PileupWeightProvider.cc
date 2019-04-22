#include "DijetAnalysis/Core/interface/PileupWeightProvider.h"

#include "TFile.h"

#include <exception>
#include <fstream>
#include <iostream>


dijet::PileupWeightProvider::PileupWeightProvider(std::string rootFileName, std::string pileupWeightHistogramName) {

    TFile file(rootFileName.c_str());

    TObject* histObj;
    file.GetObject(pileupWeightHistogramName.c_str(), histObj);
    TH1D* hist = dynamic_cast<TH1D*>(histObj);

    // dynamic cast successful if object is of type TH1D
    if (hist) {
        // clone object and store in map
        pileupWeightHistogram_ = std::unique_ptr<TH1D>(static_cast<TH1D*>(hist->Clone()));
    }
    else {
        // error
        std::invalid_argument("No object '" + pileupWeightHistogramName + "' of type TH1D found in file " + rootFileName);
    }

    file.Close();
}


const double dijet::PileupWeightProvider::getPileupWeight(const double nPUMean) {

    int binIdx = pileupWeightHistogram_->FindFixBin(nPUMean);
    if ((binIdx < 1) || (binIdx > pileupWeightHistogram_->GetNbinsX()))
        return 0.0;
    return pileupWeightHistogram_->GetBinContent(binIdx);
}
