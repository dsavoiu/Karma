#pragma once

// system include files
#include <memory>

#include "Math/VectorUtil.h"

#include "Karma/SkimmingFormats/interface/Defaults.h"  // for karma::LorentzVector


namespace karma {

    /**
     * GenericMatcher
     *   - abstract class (only for specifying interface)
     */
    template<typename TPrimaryCollection,
             typename TSecondaryCollection>
    class GenericMatcher {
      public:
        GenericMatcher(size_t maxMatches = 0, bool allowIdenticalIndices = true) :
            maxMatches_(maxMatches),
            allowIdenticalIndices_(allowIdenticalIndices) {};
        virtual ~GenericMatcher() {};

        virtual std::vector<std::pair<int, int>> match(
            const TPrimaryCollection& primaryCollection, const TSecondaryCollection& secondaryCollection) = 0;

      protected:
          const size_t maxMatches_;
          const bool allowIdenticalIndices_;
    };

    /**
     * LowestMetricMatcher
     *   - finds matches among all possible pairs of objects in primary and secondary collections
     *   - pairs are matched depending on the metric function, from _best_ to _worst_
     *   - a match is _better_ the _lower_ the metric function
     *   - if a metric value is 'nan', that match is vetoed
     *   - matching is injective (a secondary object is matched to at most one primary object)
     */
    template<typename TPrimaryCollection, typename TSecondaryCollection, typename MetricFunctor>
    class LowestMetricMatcher : public GenericMatcher<TPrimaryCollection, TSecondaryCollection> {

      public:
        LowestMetricMatcher(double maxMetricValue, size_t maxMatches = 0, bool allowIdenticalIndices = true) :
            GenericMatcher<TPrimaryCollection, TSecondaryCollection>(maxMatches, allowIdenticalIndices),
            maxMetricValue_(maxMetricValue),
            metricFunctor_(MetricFunctor()) {};

        LowestMetricMatcher(const MetricFunctor metricFunctor, double maxMetricValue, size_t maxMatches = 0, bool allowIdenticalIndices = true) :
            GenericMatcher<TPrimaryCollection, TSecondaryCollection>(maxMatches, allowIdenticalIndices),
            maxMetricValue_(maxMetricValue),
            metricFunctor_(metricFunctor) {};

        virtual std::vector<std::pair<int, int>> match(
                const TPrimaryCollection& primaryCollection, const TSecondaryCollection& secondaryCollection) {

            std::vector<std::pair<int, int>> matchResult;

            // do matching only if collections are not empty
            if ((primaryCollection.size() != 0) && (secondaryCollection.size() != 0)) {

                // -- compute delta-R for all primary-secondary pairs
                double metricMatrix[primaryCollection.size()][secondaryCollection.size()];
                for (size_t iPrimary = 0; iPrimary < primaryCollection.size(); ++iPrimary) {
                    const auto& primaryElement = primaryCollection.at(iPrimary);

                    for (size_t iSecondary = 0; iSecondary < secondaryCollection.size(); ++iSecondary) {
                        // make this pairing impossible if indices are the same and matching them is not allowed
                        if ((!this->allowIdenticalIndices_) && (iPrimary == iSecondary)) {
                            metricMatrix[iPrimary][iSecondary] = std::numeric_limits<double>::quiet_NaN();
                            continue;
                        }

                        const auto& secondaryElement = secondaryCollection.at(iSecondary);

                        const double metricValue = metricFunctor_(secondaryElement.p4, primaryElement.p4);
                        if (metricValue <= maxMetricValue_) {
                            metricMatrix[iPrimary][iSecondary] = metricValue;
                        }
                        else {
                            metricMatrix[iPrimary][iSecondary] = std::numeric_limits<double>::quiet_NaN();
                        }

                    } // end for (secondaryElements)

                } // end for (primaryElements)

                // -- do actual matching
                for (size_t iIteration = 0; iIteration < primaryCollection.size(); ++iIteration) {

                    // identify pair of indices with best match (lowest overall metric value)
                    int bestMatchPrimaryIndex = -1;
                    int bestMatchSecondaryIndex = -1;
                    double bestMatchMetricValue = std::numeric_limits<double>::quiet_NaN();
                    for (size_t iSecondary = 0; iSecondary < secondaryCollection.size(); ++iSecondary) {
                        for (size_t iRecoJet = 0; iRecoJet < primaryCollection.size(); ++iRecoJet) {

                            // update best match value and indices if better match is found
                            const double& metricValue = metricMatrix[iRecoJet][iSecondary];

                            if (!std::isnan(metricValue)) {
                                if ((metricValue < bestMatchMetricValue) || (std::isnan(bestMatchMetricValue))) {
                                    bestMatchPrimaryIndex = iRecoJet;
                                    bestMatchSecondaryIndex = iSecondary;
                                    bestMatchMetricValue = metricValue;
                                }
                            }

                        } // end for (primaryElements)
                    } // end for (secondaryElements)

                    // if no best match is found, all primary elements have been matched -> exit
                    if (std::isnan(bestMatchMetricValue))
                        break;

                    matchResult.emplace_back(bestMatchPrimaryIndex, bestMatchSecondaryIndex);

                    // return early if we reached the maximum number of allowed matched
                    if ((this->maxMatches_ > 0) && (matchResult.size() >= this->maxMatches_)) {
                        return matchResult;
                    }

                    // disallow further matches invoving these indices
                    for (size_t iPrimary = 0; iPrimary < primaryCollection.size(); ++iPrimary) {
                        metricMatrix[iPrimary][bestMatchSecondaryIndex] = std::numeric_limits<double>::quiet_NaN();
                    }
                    for (size_t iSecondary = 0; iSecondary < secondaryCollection.size(); ++iSecondary) {
                        metricMatrix[bestMatchPrimaryIndex][iSecondary] = std::numeric_limits<double>::quiet_NaN();
                    }

                } // end for (iterations)

            } // end if (empty)

            return matchResult;

        };

        const double maxMetricValue_;
        const MetricFunctor metricFunctor_;
    };


    /**
     * MetricThresholdMatcher
     *   - finds matches among all possible pairs of objects in primary and secondary collections
     *   - pairs are matched if the metric value is _below_ a configured threshold
     *   - if a metric value is 'nan', that match is vetoed
     *   - matching is not injective (a primary object will be matched to _all_ secondary objects
     *     for which the metric is below threshold)
     */
    template<typename TPrimaryCollection, typename TSecondaryCollection, typename MetricFunctor>
    class MetricThresholdMatcher : public GenericMatcher<TPrimaryCollection, TSecondaryCollection> {

      public:
        MetricThresholdMatcher(double maxMetricValue, size_t maxMatches = 0, bool allowIdenticalIndices = true) :
            GenericMatcher<TPrimaryCollection, TSecondaryCollection>(maxMatches, allowIdenticalIndices),
            maxMetricValue_(maxMetricValue),
            metricFunctor_(MetricFunctor()) {};
        MetricThresholdMatcher(const MetricFunctor metricFunctor, double maxMetricValue, size_t maxMatches = 0, bool allowIdenticalIndices = true) :
            GenericMatcher<TPrimaryCollection, TSecondaryCollection>(maxMatches, allowIdenticalIndices),
            maxMetricValue_(maxMetricValue),
            metricFunctor_(metricFunctor) {};

        virtual std::vector<std::pair<int, int>> match(
                const TPrimaryCollection& primaryCollection, const TSecondaryCollection& secondaryCollection) {

            std::vector<std::pair<int, int>> matchResult;

            // do matching only if collections are not empty
            if ((primaryCollection.size() != 0) && (secondaryCollection.size() != 0)) {

                for (size_t iPrimary = 0; iPrimary < primaryCollection.size(); ++iPrimary) {
                    for (size_t iSecondary = 0; iSecondary < secondaryCollection.size(); ++iSecondary) {

                        // skip this pairing if indices are the same and matching them is not allowed
                        if ((!this->allowIdenticalIndices_) && (iPrimary == iSecondary)) {
                            continue;
                        }

                        double metricValue = metricFunctor_(
                            primaryCollection.at(iPrimary).p4,
                            secondaryCollection.at(iSecondary).p4
                        );

                        // match *every* object within configured max metric value
                        if (metricValue <= maxMetricValue_) {
                            matchResult.emplace_back(iPrimary, iSecondary);
                        }

                        // return early if we reached the maximum number of allowed matched
                        if ((this->maxMatches_ > 0) && (matchResult.size() >= this->maxMatches_)) {
                            return matchResult;
                        }

                    } // end for (secondaryElements)

                } // end for (primaryElements)

            } // end if (empty)

            return matchResult;

        };

        const double maxMetricValue_;
        const MetricFunctor metricFunctor_;
    };

    // -- metric functors

    /**
     * Functor operates on LVs and returns DeltaR
     */
    struct DeltaRFunctor {
        double operator()(const karma::LorentzVector& v1, const karma::LorentzVector& v2) const {
            return ROOT::Math::VectorUtil::DeltaR(v1, v2);
        }
    };

    /**
     * Functor operates on LVs and returns the absolute value of the difference
     * between the invariant mass of the LVs and a reference invariant mass
     * value. The reference mass is a parameter of the functor.
     */
    struct AbsDeltaInvariantMassFunctor {
        AbsDeltaInvariantMassFunctor(double targetInvariantMass) : targetInvariantMass_(targetInvariantMass) {};
        double targetInvariantMass_;
        double operator()(const karma::LorentzVector& v1, const karma::LorentzVector& v2) const {
            return std::abs(targetInvariantMass_ - ROOT::Math::VectorUtil::InvariantMass(v1, v2));
        }
    };

    // -- specializations

    template<typename TPrimaryCollection, typename TSecondaryCollection = TPrimaryCollection>
    class LowestDeltaRMatcher : public LowestMetricMatcher<
        TPrimaryCollection, TSecondaryCollection,
        DeltaRFunctor> {

      public:

        LowestDeltaRMatcher(double maxDeltaR, size_t maxMatches = 0, bool allowIdenticalIndices = true) :
            LowestMetricMatcher<TPrimaryCollection,
                                TSecondaryCollection,
                                DeltaRFunctor>(maxDeltaR, maxMatches, allowIdenticalIndices) {};

    };

    template<typename TPrimaryCollection, typename TSecondaryCollection = TPrimaryCollection>
    class DeltaRThresholdMatcher : public MetricThresholdMatcher<
        TPrimaryCollection, TSecondaryCollection,
        DeltaRFunctor> {

      public:

        DeltaRThresholdMatcher(double maxDeltaR, size_t maxMatches = 0, bool allowIdenticalIndices = true) :
            MetricThresholdMatcher<TPrimaryCollection,
                                   TSecondaryCollection,
                                   DeltaRFunctor>(maxDeltaR, maxMatches, allowIdenticalIndices) {};

    };

    template<typename TPrimaryCollection, typename TSecondaryCollection = TPrimaryCollection>
    class LowestAbsDeltaInvariantMassMatcher : public LowestMetricMatcher<
        TPrimaryCollection, TSecondaryCollection,
        AbsDeltaInvariantMassFunctor> {

      public:

        LowestAbsDeltaInvariantMassMatcher(double targetInvariantMass, double maxDeltaInvariantMass, size_t maxMatches = 0, bool allowIdenticalIndices = true) :
            LowestMetricMatcher<TPrimaryCollection,
                                TSecondaryCollection,
                                AbsDeltaInvariantMassFunctor>(AbsDeltaInvariantMassFunctor(targetInvariantMass), maxDeltaInvariantMass, maxMatches, allowIdenticalIndices) {};

    };


}  // end namespace
