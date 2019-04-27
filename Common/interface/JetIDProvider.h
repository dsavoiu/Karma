#pragma once

#include <boost/algorithm/string/case_conv.hpp>

#include "Karma/SkimmingFormats/interface/Event.h"

namespace dijet {

    class JetIDBaseUntemplated {
      public:
        JetIDBaseUntemplated() {};
        virtual ~JetIDBaseUntemplated() {};
        virtual bool getJetID(const dijet::Jet& jet) = 0;
    };

    template<typename TWorkingPoint>
    class JetIDBase : public JetIDBaseUntemplated {
      public:

        typedef TWorkingPoint WorkingPoint;

        JetIDBase() : JetIDBaseUntemplated() {};
        virtual ~JetIDBase() {};

        WorkingPoint getWorkingPoint() const {return workingPoint_;};
        //void setWorkingPoint(std::string) = 0;

      protected:
        virtual WorkingPoint toWorkingPoint(std::string workingPoint) = 0;

        WorkingPoint workingPoint_;
    };


    enum class JetID2016WorkingPoint {
        Loose,
        Tight,
        TightLepVeto,
    };

    class JetID2016 : public JetIDBase<JetID2016WorkingPoint> {
      public:

        virtual WorkingPoint toWorkingPoint(std::string workingPoint) {
            boost::algorithm::to_lower(workingPoint);  // make lowercase
            if (workingPoint == "loose") return WorkingPoint::Loose;
            else if (workingPoint == "tight") return WorkingPoint::Tight;
            else if (workingPoint == "tightlepveto") return WorkingPoint::TightLepVeto;
            else throw std::invalid_argument("Unknown JetID working point: " + workingPoint);
        };

        JetID2016(std::string workingPoint) {
            workingPoint_ = toWorkingPoint(workingPoint);
        };
        ~JetID2016() {};

        virtual bool getJetID(const dijet::Jet& jet) override {
            const double absEta = std::abs(jet.p4.eta());
            if (absEta <= 2.7) {
                return (
                    (jet.neutralHadronFraction < (workingPoint_ == WorkingPoint::Loose ? 0.99 : 0.90)) &&
                    (jet.photonFraction < (workingPoint_ == WorkingPoint::Loose ? 0.99 : 0.90)) &&
                    (jet.nConstituents > 1) &&
                    (workingPoint_ == WorkingPoint::TightLepVeto ? (jet.muonFraction < 0.8) : true) &&
                    (absEta <= 2.4 ? (
                            (jet.chargedHadronFraction > 0) &&
                            (jet.nCharged > 0) &&
                            (jet.electronFraction < (workingPoint_ == WorkingPoint::TightLepVeto ? 0.90 : 0.99))
                        ) : true
                    )
                );
            }
            else if (absEta <= 3.0) {
                return (
                    (jet.neutralHadronFraction < 0.98) &&
                    (jet.photonFraction > 0.01) &&
                    ((jet.nConstituents - jet.nCharged) > 2)  // # of neutral constituents
                );
            }
            else /*absEta > 3.0 */{
                return (
                    (jet.photonFraction < 0.90) &&
                    ((jet.nConstituents - jet.nCharged) > 10)  // # of neutral constituents
                );
            }
        };

    };

    class JetIDProvider {
      public:

        JetIDProvider(std::string jetIDSpec, std::string jetIDWorkingPoint);
        ~JetIDProvider() {};

        bool getJetID(const dijet::Jet& jet);

      private:

        std::unique_ptr<JetIDBaseUntemplated> jetID_;

    };
}
