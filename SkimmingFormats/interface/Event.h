#pragma once

#include <vector>
#include <algorithm>
#include <functional>

#include <boost/algorithm/string/join.hpp>

#include "Defaults.h"

// some tools from the EDM data formats
#include "DataFormats/METReco/interface/CorrMETData.h"
#include "DataFormats/METReco/interface/MET.h"
#include "DataFormats/MuonReco/interface/MuonSelectors.h"
#include "DataFormats/Common/interface/AssociationMap.h"
#include "DataFormats/Common/interface/ValueMap.h"


namespace karma {

    class Event {
      public:
        // -- event metadata
        double rho = UNDEFINED_DOUBLE;  // pileup density
        double npv = -1;                // number of primary vertices
        double npvGood = -1;            // number of 'good' primary vertices

        // -- pileup-related
        int nPU = -1;                       // # of interactions in event (including pile-up mixing)
        double nPUTrue = UNDEFINED_DOUBLE;  // mean of Poisson distribution from which nPU is sampled

        // -- trigger decisions
        std::vector<bool> hltBits;

        // -- met filter bits
        std::vector<bool> metFilterBits;

        // it's easier to store these once per event rather than once per lumi-section
        std::vector<int> triggerPathHLTPrescales;
        std::vector<int> triggerPathL1Prescales;
        // define if ever needed
        //std::vector<int> triggerPathL1PrescalesMax;

    };
    typedef std::vector<karma::Event> EventCollection;

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
    typedef std::vector<karma::GeneratorQCDInfo> GeneratorQCDInfoCollection;

    /**
     * Simple lorentz vector class
     */
    class LV {
      public:

        // -- kinematics
        karma::LorentzVector p4;

        // transient maps for temporarily storing data while processing
        std::map<std::string, double> transientDoubles_;
        std::map<std::string, bool> transientBools_;
        std::map<std::string, int> transientInts_;
        std::map<std::string, karma::LorentzVector> transientLVs_;

        size_t ptHash() {
            return std::hash<double>()(p4.pt());
        }

    };
    typedef std::vector<karma::LV> LVCollection;

    /**
     * Particle class
     */
    class Particle : public karma::LV {
      public:
        int pdgId = -999;
        int status = -999;

        int charge = -999;

    };
    typedef std::vector<karma::Particle> ParticleCollection;

    /**
     * Generator Particle class
     */
    class GenParticle : public karma::Particle {
      public:
        int nDaughters = -1;

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
    typedef std::vector<karma::GenParticle> GenParticleCollection;

    /**
     * Lepton class
     */
    class Lepton : public karma::Particle {
      public:
        double trackIso = UNDEFINED_DOUBLE;
        double caloIso = UNDEFINED_DOUBLE;
        double ecalIso = UNDEFINED_DOUBLE;
        double hcalIso = UNDEFINED_DOUBLE;

        double particleIso = UNDEFINED_DOUBLE;
        double chargedHadronIso = UNDEFINED_DOUBLE;
        double neutralHadronIso = UNDEFINED_DOUBLE;
        double photonIso = UNDEFINED_DOUBLE;
        double puChargedHadronIso = UNDEFINED_DOUBLE;

    };
    typedef std::vector<karma::Lepton> LeptonCollection;

    /**
     * Photon class
     */
    class Photon : public karma::LV {
      public:
        /* no additional properties (yet) */
    };
    typedef std::vector<karma::Photon> PhotonCollection;

    /**
     * Muon class
     */
    class Muon : public karma::Lepton {
      public:
        /* no further quantities yet */
        uint64_t recoSelectors;

        bool passedSelection(reco::Muon::Selector selection) const {
            return passedSelection(static_cast<unsigned int>(selection));
        }

      private:
        bool passedSelection(uint64_t selection) const {
            return (recoSelectors & selection)==selection;
        }

    };
    typedef std::vector<karma::Muon> MuonCollection;

    /**
     * Electron class
     */
    class Electron : public karma::Lepton {
      public:
        double ecalTrkEnergyPreCorr = UNDEFINED_DOUBLE;
        double ecalTrkEnergyPostCorr = UNDEFINED_DOUBLE;

    };
    typedef std::vector<karma::Electron> ElectronCollection;

    /**
     * Jet class
     */
    class Jet : public karma::LV {
      public:
        karma::LorentzVector uncorP4;

        double area = UNDEFINED_DOUBLE

        int nConstituents = -1;
        int nCharged = -1;
        int nElectrons = -1;
        int nMuons = -1;
        int nPhotons = -1;

        int hadronFlavor = -999;
        int partonFlavor = -999;

        double neutralHadronFraction = UNDEFINED_DOUBLE;
        double chargedHadronFraction = UNDEFINED_DOUBLE;
        double chargedEMFraction = UNDEFINED_DOUBLE;
        double neutralEMFraction = UNDEFINED_DOUBLE;
        double muonFraction = UNDEFINED_DOUBLE;
        double electronFraction = UNDEFINED_DOUBLE;
        double photonFraction = UNDEFINED_DOUBLE;
        double hfHadronFraction = UNDEFINED_DOUBLE;
        double hfEMFraction = UNDEFINED_DOUBLE;

    };
    typedef std::vector<karma::Jet> JetCollection;

    /**
     * MET class
     */
    class MET : public karma::LV {
      public:
        karma::LorentzVector uncorP4;

        double sumEt = UNDEFINED_DOUBLE;
        double uncorSumEt = UNDEFINED_DOUBLE;

        double significance = UNDEFINED_DOUBLE;

        double neutralHadronFraction = UNDEFINED_DOUBLE;
        double chargedHadronFraction = UNDEFINED_DOUBLE;
        double muonFraction = UNDEFINED_DOUBLE;
        double photonFraction = UNDEFINED_DOUBLE;
        double electronFraction = UNDEFINED_DOUBLE;
        double hfHadronFraction = UNDEFINED_DOUBLE;
        double hfEMFraction = UNDEFINED_DOUBLE;

        //! apply met correction and return corrected lorentz vector
        karma::LorentzVector getCorrectedP4(const CorrMETData& correction) {
          // copied from 'DataFormats/METReco/interface/CorrMETData.h'
          double px = uncorP4.Px() + correction.mex;
          double py = uncorP4.Py() + correction.mey;
          double pt = sqrt(px*px + py*py);
          return karma::LorentzVector(ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> >(px, py, 0., pt));
        }

    };
    typedef std::vector<karma::MET> METCollection;

    /**
     * Trigger Object class
     */
    class TriggerObject : public karma::LV {
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
    typedef std::vector<karma::TriggerObject> TriggerObjectCollection;

    /**
     * reconstruted vertex class
     */
    class Vertex {
      public:
        karma::PositionVector3D position;
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
    typedef std::vector<karma::Vertex> VertexCollection;

    // -- association maps
    typedef edm::AssociationMap<edm::OneToMany<karma::JetCollection, karma::TriggerObjectCollection>> JetTriggerObjectsMap;
    typedef std::vector<karma::JetTriggerObjectsMap> JetTriggerObjectsMaps;

    typedef edm::AssociationMap<edm::OneToMany<karma::JetCollection, karma::MuonCollection>> JetMuonsMap;
    typedef std::vector<karma::JetMuonsMap> JetMuonsMaps;

    typedef edm::AssociationMap<edm::OneToMany<karma::JetCollection, karma::ElectronCollection>> JetElectronsMap;
    typedef std::vector<karma::JetElectronsMap> JetElectronsMaps;

    typedef edm::AssociationMap<edm::OneToOne<karma::JetCollection, karma::LVCollection>> JetGenJetMap;
    typedef std::vector<karma::JetGenJetMap> JetGenJetMaps;
}
