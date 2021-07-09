#include "Karma/Common/interface/Providers/PileupWeightProviderV2.h"

#include "TFile.h"
#include "TROOT.h"
#include "TError.h"
#include "TMath.h"

#include <exception>
#include <fstream>
#include <iostream>

#include <boost/uuid/uuid.hpp>
#include <boost/uuid/uuid_generators.hpp>
#include <boost/uuid/uuid_io.hpp>


karma::PileupWeightProviderV2::PileupWeightProviderV2(
    std::string numeratorRootFileName, std::string denominatorRootFileName, std::string pileupHistogramName) {

    // == retrieve histograms

    // open ROOT files
    TFile fileNum(numeratorRootFileName.c_str());
    TFile fileDen(denominatorRootFileName.c_str());

    // suffix to append to hist name for systematic PU variations
    std::map<PileupVariation, std::string> histNameSuffixes {
        {PileupVariation::central, ""},
        {PileupVariation::up,      "Up"},
        {PileupVariation::down,    "Down"}
    };

    // -- retrieve denominator PU profile
    TObject* histObjDen;
    fileDen.GetObject(pileupHistogramName.c_str(), histObjDen);
    TH1D* histDen = dynamic_cast<TH1D*>(histObjDen);
    // dynamic cast fails if object does not exist or is not of type TH1D -> throw
    if (!histDen) {
        throw std::invalid_argument("No object '" + pileupHistogramName + "' of type TH1D found in denominator file: " + denominatorRootFileName);
    }

    // -- retrieve numerator PU profiles (one for each systematic variation)
    for (const auto var : {PileupVariation::central, PileupVariation::up, PileupVariation::down}) {

        // unique string to use as hist name suffix
        std::string unique_id = boost::uuids::to_string(boost::uuids::random_generator()());

        // get histogram according to naming conventions
        TObject* histObjNum;
        fileNum.GetObject((pileupHistogramName + histNameSuffixes.at(var)).c_str(), histObjNum);
        TH1D* histNum = dynamic_cast<TH1D*>(histObjNum);
        // dynamic cast fails if object does not exist or is not of type TH1D -> throw
        if (!histNum) {
            throw std::invalid_argument("No object '" + pileupHistogramName + histNameSuffixes.at(var) + "' of type TH1D found in numerator file: " + numeratorRootFileName);
        }

        // clone PU profile histograms and normalize to unity
        histNum = static_cast<TH1D*>(histNum->Clone(("histNum_"+unique_id).c_str()));
        histDen = static_cast<TH1D*>(histDen->Clone(("histDen_"+unique_id).c_str()));
        histNum->Scale(1.0/histNum->Integral());
        histDen->Scale(1.0/histDen->Integral());

        // == divide histograms
        // NOTE: not using TH1D::Divide here due to buggy implementation
        //       (throws a ROOT fatal error due to incompatible bin limits if one of the
        //       numerator/denominator histograms was created using an equidistant binning
        //       and the other with explicit bin edges, even if the resulting binnings are
        //       identical!)

        // -- verify numerator/denominator compatibility manually
        // check number of bins
        int nBins = histNum->GetNbinsX();
        if (nBins != histDen->GetNbinsX()) {
            throw std::invalid_argument(
                "[PileupWeightProviderV2] Numerator and denominator PU profiles have different number of bins (" +
                std::to_string(nBins) + " != " + std::to_string(histDen->GetNbinsX()) + "). Aborting.");
        }
        // check bin edges
        for (int iBin = 1; iBin <= nBins+1; ++iBin) {
            if (std::abs(histNum->GetBinLowEdge(iBin) - histDen->GetBinLowEdge(iBin)) > 1e-6 * histNum->GetBinWidth(iBin)) {
                throw std::invalid_argument("[PileupWeightProviderV2] Numerator and denominator PU profiles have different bin edges. Aborting.");
            }
        }

        // -- do the divison
        auto& histRatio = pileupWeightHistograms_[var];
        histRatio = std::unique_ptr<TH1D>(static_cast<TH1D*>(histNum->Clone(("pileupWeight_"+unique_id).c_str()))); 
        for (int iBin = 1; iBin <= nBins; ++iBin) {
            if (std::abs(histDen->GetBinContent(iBin)) < 1e-10) {
                // if undefined, set to zero
                histRatio->SetBinContent(iBin, 0);
            }
            else {
                histRatio->SetBinContent(iBin, histNum->GetBinContent(iBin) / histDen->GetBinContent(iBin));
            }
            histRatio->SetBinError(iBin, 0);
        }
    }

    fileNum.Close();
    fileDen.Close();
}


const double karma::PileupWeightProviderV2::getPileupWeight(const double nPUMean, PileupVariation var) {

    const auto& puWeightHist = pileupWeightHistograms_.at(var);
    int binIdx = puWeightHist->FindFixBin(nPUMean);
    if ((binIdx < 1) || (binIdx > puWeightHist->GetNbinsX()))
        return 0.0;
    return puWeightHist->GetBinContent(binIdx);
}
