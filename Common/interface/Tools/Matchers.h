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
        virtual ~GenericMatcher() {};

        virtual std::vector<std::pair<int, int>> match(
            const TPrimaryCollection& primaryCollection, const TSecondaryCollection& secondaryCollection) = 0;
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
        LowestMetricMatcher(double maxMetricValue) :
            maxMetricValue_(maxMetricValue),
            metricFunctor_(MetricFunctor()) {};

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
        MetricThresholdMatcher(double maxMetricValue) :
            maxMetricValue_(maxMetricValue),
            metricFunctor_(MetricFunctor()) {};

        virtual std::vector<std::pair<int, int>> match(
                const TPrimaryCollection& primaryCollection, const TSecondaryCollection& secondaryCollection) {

            std::vector<std::pair<int, int>> matchResult;

            // do matching only if collections are not empty
            if ((primaryCollection.size() != 0) && (secondaryCollection.size() != 0)) {

                for (size_t iPrimary = 0; iPrimary < primaryCollection.size(); ++iPrimary) {
                    for (size_t iSecondary = 0; iSecondary < secondaryCollection.size(); ++iSecondary) {

                        double metricValue = metricFunctor_(
                            primaryCollection.at(iPrimary).p4,
                            secondaryCollection.at(iSecondary).p4
                        );

                        // match *every* object within configured max metric value
                        if (metricValue <= maxMetricValue_) {
                            matchResult.emplace_back(iPrimary, iSecondary);
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

    struct DeltaRFunctor {
        double operator()(const karma::LorentzVector& v1, const karma::LorentzVector& v2) const {
            return ROOT::Math::VectorUtil::DeltaR(v1, v2);
        }
    };

    // -- specializations

    template<typename TPrimaryCollection, typename TSecondaryCollection>
    class LowestDeltaRMatcher : public LowestMetricMatcher<
        TPrimaryCollection, TSecondaryCollection,
        DeltaRFunctor> {

      public:

        LowestDeltaRMatcher(double maxDeltaR) : 
            LowestMetricMatcher<TPrimaryCollection,
                                TSecondaryCollection,
                                DeltaRFunctor>(maxDeltaR) {};

    };

    template<typename TPrimaryCollection, typename TSecondaryCollection>
    class DeltaRThresholdMatcher : public MetricThresholdMatcher<
        TPrimaryCollection, TSecondaryCollection,
        DeltaRFunctor> {

      public:

        DeltaRThresholdMatcher(double maxDeltaR) : 
            MetricThresholdMatcher<TPrimaryCollection,
                                   TSecondaryCollection,
                                   DeltaRFunctor>(maxDeltaR) {};

    };

}  // end namespace
