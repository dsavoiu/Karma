#pragma once

#include <vector>
#include <algorithm>
#include <functional>

#include <boost/algorithm/string/join.hpp>

#include "Defaults.h"

#include "DataFormats/Common/interface/AssociationMap.h"

namespace dijet {
    class Event {
      public:
        // -- event metadata
        double rho = UNDEFINED_DOUBLE;  // pileup density
        double npv = -1;                // number of primary vertices
        double npvGood = -1;                // number of 'good' primary vertices

        // -- trigger decisions
        std::vector<bool> hltBits;

        // it's easier to store these once per event rather than once per lumi-section
        std::vector<int> triggerPathHLTPrescales;
        std::vector<int> triggerPathL1Prescales;

    };
    typedef std::vector<dijet::Event> EventCollection;

    class GeneratorQCDInfo {
      public:

        // -- generator information
        double weight = UNDEFINED_DOUBLE;
        double weightProduct = UNDEFINED_DOUBLE;
        std::vector<double> binningValues;

        // -- QCD subprocess information
        int parton1PdgId = -999;
        int parton2PdgId = -999;

        double parton1x = UNDEFINED_DOUBLE;
        double parton2x = UNDEFINED_DOUBLE;

        double parton1xPDF = UNDEFINED_DOUBLE;
        double parton2xPDF = UNDEFINED_DOUBLE;

        double scalePDF = UNDEFINED_DOUBLE;
        double alphaQCD = UNDEFINED_DOUBLE;

    };
    typedef std::vector<dijet::GeneratorQCDInfo> GeneratorQCDInfoCollection;

    /**
     * Simple lorentz vector class
     */
    class LV {
      public:

        // -- kinematics
        dijet::LorentzVector p4;

        size_t ptHash() {
            return std::hash<double>()(p4.pt());
        }

    };
    typedef std::vector<dijet::LV> LVCollection;

    /**
     * Generator Particle class
     */
    class GenParticle : public dijet::LV {
      public:
        int pdgId = -999;

        int nDaughters = -1;
        int status = -999;

        bool isPrompt = 0;
        bool isDecayedLeptonHadron = 0;
        bool isTauDecayProduct = 0;
        bool isPromptTauDecayProduct = 0;
        bool isDirectTauDecayProduct = 0;
        bool isDirectPromptTauDecayProduct = 0;
        bool isDirectHadronDecayProduct = 0;
        bool isHardProcess = 0;
        bool fromHardProcess = 0;
        bool isHardProcessTauDecayProduct = 0;
        bool isDirectHardProcessTauDecayProduct = 0;
        bool isLastCopy = 0;

        int index = -1;
        std::vector<int> daughterIndices;

    };
    typedef std::vector<dijet::GenParticle> GenParticleCollection;

    /**
     * Jet class
     */
    class Jet : public dijet::LV {
      public:
        double area = UNDEFINED_DOUBLE

        int nConstituents = -1;
        int nCharged = -1;

        int hadronFlavor = -999;
        int partonFlavor = -999;

        double neutralHadronFraction = UNDEFINED_DOUBLE;
        double chargedHadronFraction = UNDEFINED_DOUBLE;
        double muonFraction = UNDEFINED_DOUBLE;
        double photonFraction = UNDEFINED_DOUBLE;
        double electronFraction = UNDEFINED_DOUBLE;
        double hfHadronFraction = UNDEFINED_DOUBLE;
        double hfEMFraction = UNDEFINED_DOUBLE;

        // pileup-corrected p4 (JEC L1), needed for Type-I MET correction
        dijet::LorentzVector p4CorrL1;

    };
    typedef std::vector<dijet::Jet> JetCollection;

    /**
     * MET class
     */
    class MET : public dijet::LV {
      public:
        double significance = UNDEFINED_DOUBLE;
        double sumEt = UNDEFINED_DOUBLE;

        double neutralHadronFraction = UNDEFINED_DOUBLE;
        double chargedHadronFraction = UNDEFINED_DOUBLE;
        double muonFraction = UNDEFINED_DOUBLE;
        double photonFraction = UNDEFINED_DOUBLE;
        double electronFraction = UNDEFINED_DOUBLE;
        double hfHadronFraction = UNDEFINED_DOUBLE;
        double hfEMFraction = UNDEFINED_DOUBLE;
    };
    typedef std::vector<dijet::MET> METCollection;

    /**
     * Trigger Object class
     */
    class TriggerObject : public dijet::LV {
      public:

        std::vector<int> types;
        std::vector<int> assignedPathIndices;
        std::vector<std::string> filterNames;

        size_t numFilters() const { return filterNames.size(); };

        std::string filterString() const {
            return boost::algorithm::join(filterNames, "+");
        };

        std::string pathIndicesString() const {
            std::vector<std::string> assignedPathIndexStrings;
            std::transform(
                assignedPathIndices.begin(),
                assignedPathIndices.end(),
                std::back_inserter(assignedPathIndexStrings),
                [](int index){return std::to_string(index);}
            );
            return boost::algorithm::join(assignedPathIndexStrings, ",");
        };

        bool isL1() const {
            if (std::all_of(types.cbegin(), types.cend(), [](int i){ return i <= 0; })) {
                return true;
            }
            return false;

        }

        bool isHLT() const {
            if (std::all_of(types.cbegin(), types.cend(), [](int i){ return i >= 0; })) {
                return true;
            }
            return false;
        }

        int unambiguousType() const {
            int foundType = 0;
            for (const auto& type : types) {
                // skip trivial type '0'
                if (type != 0) {
                    // assign type
                    if (foundType == -1) {
                        foundType = type;
                    }
                    // type already assigned -> ignore if equal
                    else if (foundType != type) {
                        // found more than one nontrivial type
                        return 0;
                    }
                }
            }
            // no types stored or all trivial ('0')
            return foundType;
        }

    };
    typedef std::vector<dijet::TriggerObject> TriggerObjectCollection;

    /**
     * reconstruted vertex class
     */
    class Vertex {
      public:
        dijet::PositionVector3D position;
        double time = UNDEFINED_DOUBLE;

        double chi2 = 0;
        double ndof = 0;
        size_t nTracks = 0;

        bool validity = false;

        bool isFake() const {
            return (chi2==0 && ndof==0 && nTracks==0);
        }

        bool isGoodOfflineVertex() const {
            return (!isFake() && ndof >= 4.0 && std::abs(position.Z()) <= 24.0 && std::abs(position.Rho()) <= 2.0);
        }

    };
    typedef std::vector<dijet::Vertex> VertexCollection;

    // -- association maps
    typedef edm::AssociationMap<edm::OneToMany<dijet::JetCollection, dijet::TriggerObjectCollection>> JetTriggerObjectsMap;
    typedef std::vector<dijet::JetTriggerObjectsMap> JetTriggerObjectsMaps;

    typedef edm::AssociationMap<edm::OneToOne<dijet::JetCollection, dijet::LVCollection>> JetGenJetMap;
    typedef std::vector<dijet::JetGenJetMap> JetGenJetMaps;
}
