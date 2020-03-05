#pragma once

#include <stdexcept>

#include "CollectionProducer.h"

#include "FWCore/Utilities/interface/EDMException.h"

#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include "DataFormats/PatCandidates/interface/MET.h"


namespace karma {

    class METCollectionProducer : public karma::CollectionProducerBase<edm::View<pat::MET>, karma::METCollection> {

      public:
        explicit METCollectionProducer(const edm::ParameterSet& config) :
            karma::CollectionProducerBase<edm::View<pat::MET>, karma::METCollection>(config),
            mainCorrectionLevel_(toCorrectionLevel(config.getParameter<std::string>("mainCorrectionLevel"))) {};
        ~METCollectionProducer() {};

        virtual void produceSingle(const pat::MET&, karma::MET&, const edm::Event&, const edm::EventSetup&);

      private:

        // should be static but cannot (see below)
        pat::MET::METCorrectionLevel toCorrectionLevel(const std::string& correctionLevelSpec) {
            try {
                return _toCorrectionLevelMap.at(correctionLevelSpec);
            }
            catch (std::out_of_range&) {
                edm::Exception exception(edm::errors::Configuration);
                exception << "Invalid MET correction level specification '" << correctionLevelSpec
                          << "' Available specifications are: " << std::endl;
                for (const auto& keyValuePair : _toCorrectionLevelMap) {
                    exception << keyValuePair.first << std::endl;
                }
                throw exception;
            }
        };

        // this would ideally be 'static constexpr', but C++11 does not support this
        const std::map<std::string, pat::MET::METCorrectionLevel> _toCorrectionLevelMap = {
            {"Raw",            pat::MET::METCorrectionLevel::Raw},
            {"Type1",          pat::MET::METCorrectionLevel::Type1},
            {"Type01",         pat::MET::METCorrectionLevel::Type01},
            {"TypeXY",         pat::MET::METCorrectionLevel::TypeXY},
            {"Type1XY",        pat::MET::METCorrectionLevel::Type1XY},
            {"Type01XY",       pat::MET::METCorrectionLevel::Type01XY},
            {"Type1Smear",     pat::MET::METCorrectionLevel::Type1Smear},
            {"Type01Smear",    pat::MET::METCorrectionLevel::Type01Smear},
            {"Type1SmearXY",   pat::MET::METCorrectionLevel::Type1SmearXY},
            {"Type01SmearXY",  pat::MET::METCorrectionLevel::Type01SmearXY},
            {"RawCalo",        pat::MET::METCorrectionLevel::RawCalo},
            {"RawChs",         pat::MET::METCorrectionLevel::RawChs},
            {"RawTrk",         pat::MET::METCorrectionLevel::RawTrk}
        };

        pat::MET::METCorrectionLevel mainCorrectionLevel_;

    };

}  // end namespace
