#include "DijetAnalysis/Core/interface/NPUMeanProvider.h"

#include <exception>
#include <fstream>
#include <iostream>

dijet::NPUMeanProvider::NPUMeanProvider(std::string fileName, double minBiasCrossSection) {

    unsigned long run(0), luminosityBlock(0);
    double luminosity(0), xsAverage(0), xsRMS(0);

    std::cout << "[NPUMeanProvider] Reading file '" << fileName << "'..." << std::endl;
    std::ifstream inputFile(fileName.c_str(), std::ios::in);
    if (!inputFile.is_open()) {
        throw std::ios_base::failure("[NPUMeanProvider] Could not open file '" + fileName + "'!");
    }
    while (inputFile >> run >> luminosityBlock >> luminosity >> xsRMS >> xsAverage) {
        /*
        std::cout << run << " "
                  << luminosityBlock << " "
                  << luminosity << " "
                  << xsAverage << " "
                  << xsRMS << ": "
                  << (xsAverage * minBiasCrossSection * 1000.0f) << " +/- " << (xsRMS * minBiasCrossSection * 1000.0f) << std::endl;
        */

        if (xsRMS < 0) {
            throw std::domain_error("[NPUMeanProvider] Negative 'xsRMS' value encountered in file '" + fileName + "'! Aborting...");
        }

        mapRunLumiBlockToNPUMean_[run][luminosityBlock] = xsAverage * minBiasCrossSection * 1000.0f;
    }
}


const double dijet::NPUMeanProvider::getNPUMean(const unsigned long run, const unsigned long luminosityBlock) {
    try {
        return mapRunLumiBlockToNPUMean_.at(run).at(luminosityBlock);
    } catch (const std::out_of_range& err) {
        //TODO
        return -1;
    }
}
