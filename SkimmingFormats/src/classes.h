//#pragma once

#include "DataFormats/Common/interface/Wrapper.h"
#include "Karma/SkimmingFormats/interface/Event.h"
#include "Karma/SkimmingFormats/interface/Lumi.h"
#include "Karma/SkimmingFormats/interface/Run.h"

#include "DataFormats/Common/interface/ValueMap.h"
#include "DataFormats/Common/interface/AssociationVector.h"

#include <utility>

namespace {
    struct dictionary {
        // event
        karma::Event dict_karmaEvent;
        edm::Wrapper<karma::Event> dict_edmWrapperDijetEvent;
        karma::EventCollection dict_karmaEventCollection;
        edm::Wrapper<karma::EventCollection> dict_edmWrapperDijetEventCollection;

        // generator information
        karma::Event dict_karmaGeneratorQCDInfo;
        edm::Wrapper<karma::GeneratorQCDInfo> dict_edmWrapperDijetGeneratorQCDInfo;
        karma::GeneratorQCDInfoCollection dict_karmaGeneratorQCDInfoCollection;
        edm::Wrapper<karma::GeneratorQCDInfoCollection> dict_edmWrapperDijetGeneratorQCDInfoCollection;

        // luminosity block
        karma::Lumi dict_karmaLumi;
        edm::Wrapper<karma::Lumi> dict_edmWrapperDijetLumi;
        karma::LumiCollection dict_karmaLumiCollection;
        edm::Wrapper<karma::LumiCollection> dict_edmWrapperDijetLumiCollection;

        // run
        karma::Run dict_karmaRun;
        edm::Wrapper<karma::Run> dict_edmWrapperDijetRun;
        karma::RunCollection dict_karmaRunCollection;
        edm::Wrapper<karma::RunCollection> dict_edmWrapperDijetRunCollection;

        // HLT infos
        karma::HLTPathInfo dict_karmaHLTPathInfo;
        edm::Wrapper<karma::HLTPathInfo> dict_edmWrapperDijetHLTPathInfo;
        karma::HLTPathInfos dict_karmaHLTPathInfos;
        edm::Wrapper<karma::HLTPathInfos> dict_edmWrapperDijetHLTPathInfos;

        // -- event objects

        // lvs
        karma::LV dict_karmaLV;
        edm::Wrapper<karma::LV> dict_edmWrapperDijetLV;
        karma::LVCollection dict_karmaLVCollection;
        edm::Wrapper<karma::LVCollection> dict_edmWrapperDijetLVCollection;
        edm::RefProd<karma::LVCollection> dict_edmRefProdDijetLVCollection;

        // LV association vectors
        edm::AssociationVector<edm::RefProd<karma::LVCollection>, std::vector<int>> dict_karmaAssociationVectorLVToInt;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::LVCollection>, std::vector<int>>> dict_edmWrapperDijetAssociationVectorLVToInt;
        std::pair<edm::Ref<karma::LVCollection>, int> dict_karmaAssociationVectorPairLVToInt;
        std::vector<std::pair<edm::Ref<karma::LVCollection>, int>> dict_karmaAssociationVectorPairVectorLVToInt;

        edm::AssociationVector<edm::RefProd<karma::LVCollection>, std::vector<double>> dict_karmaAssociationVectorLVToDouble;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::LVCollection>, std::vector<double>>> dict_edmWrapperDijetAssociationVectorLVToDouble;
        std::pair<edm::Ref<karma::LVCollection>, double> dict_karmaAssociationVectorPairLVToDouble;
        std::vector<std::pair<edm::Ref<karma::LVCollection>, double>> dict_karmaAssociationVectorPairVectorLVToDouble;

        edm::AssociationVector<edm::RefProd<karma::LVCollection>, std::vector<bool>> dict_karmaAssociationVectorLVToBool;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::LVCollection>, std::vector<bool>>> dict_edmWrapperDijetAssociationVectorLVToBool;
        std::pair<edm::Ref<karma::LVCollection>, bool> dict_karmaAssociationVectorPairLVToBool;
        std::vector<std::pair<edm::Ref<karma::LVCollection>, bool>> dict_karmaAssociationVectorPairVectorLVToBool;

        edm::AssociationVector<edm::RefProd<karma::LVCollection>, std::vector<karma::LorentzVector>> dict_karmaAssociationVectorLVToLV;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::LVCollection>, std::vector<karma::LorentzVector>>> dict_edmWrapperDijetAssociationVectorLVToLV;
        std::pair<edm::Ref<karma::LVCollection>, karma::LorentzVector> dict_karmaAssociationVectorPairLVToLV;
        std::vector<std::pair<edm::Ref<karma::LVCollection>, karma::LorentzVector>> dict_karmaAssociationVectorPairVectorLVToLV;

        // particles
        karma::Particle dict_karmaParticle;
        edm::Wrapper<karma::Particle> dict_edmWrapperDijetParticle;
        karma::ParticleCollection dict_karmaParticleCollection;
        edm::Wrapper<karma::ParticleCollection> dict_edmWrapperDijetParticleCollection;

        // leptons
        karma::Lepton dict_karmaLepton;
        edm::Wrapper<karma::Lepton> dict_edmWrapperDijetLepton;
        karma::LeptonCollection dict_karmaLeptonCollection;
        edm::Wrapper<karma::LeptonCollection> dict_edmWrapperDijetLeptonCollection;

        // electrons
        karma::Electron dict_karmaElectron;
        edm::Wrapper<karma::Electron> dict_edmWrapperDijetElectron;
        karma::ElectronCollection dict_karmaElectronCollection;
        edm::Wrapper<karma::ElectronCollection> dict_edmWrapperDijetElectronCollection;
        edm::RefProd<karma::ElectronCollection> dict_edmRefProdDijetElectronCollection;

        // electron association vectors
        edm::AssociationVector<edm::RefProd<karma::ElectronCollection>, std::vector<int>> dict_karmaAssociationVectorElectronToInt;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::ElectronCollection>, std::vector<int>>> dict_edmWrapperDijetAssociationVectorElectronToInt;
        std::pair<edm::Ref<karma::ElectronCollection>, int> dict_karmaAssociationVectorPairElectronToInt;
        std::vector<std::pair<edm::Ref<karma::ElectronCollection>, int>> dict_karmaAssociationVectorPairVectorElectronToInt;

        edm::AssociationVector<edm::RefProd<karma::ElectronCollection>, std::vector<double>> dict_karmaAssociationVectorElectronToDouble;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::ElectronCollection>, std::vector<double>>> dict_edmWrapperDijetAssociationVectorElectronToDouble;
        std::pair<edm::Ref<karma::ElectronCollection>, double> dict_karmaAssociationVectorPairElectronToDouble;
        std::vector<std::pair<edm::Ref<karma::ElectronCollection>, double>> dict_karmaAssociationVectorPairVectorElectronToDouble;

        edm::AssociationVector<edm::RefProd<karma::ElectronCollection>, std::vector<bool>> dict_karmaAssociationVectorElectronToBool;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::ElectronCollection>, std::vector<bool>>> dict_edmWrapperDijetAssociationVectorElectronToBool;
        std::pair<edm::Ref<karma::ElectronCollection>, bool> dict_karmaAssociationVectorPairElectronToBool;
        std::vector<std::pair<edm::Ref<karma::ElectronCollection>, bool>> dict_karmaAssociationVectorPairVectorElectronToBool;

        edm::AssociationVector<edm::RefProd<karma::ElectronCollection>, std::vector<karma::LorentzVector>> dict_karmaAssociationVectorElectronToLV;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::ElectronCollection>, std::vector<karma::LorentzVector>>> dict_edmWrapperDijetAssociationVectorElectronToLV;
        std::pair<edm::Ref<karma::ElectronCollection>, karma::LorentzVector> dict_karmaAssociationVectorPairElectronToLV;
        std::vector<std::pair<edm::Ref<karma::ElectronCollection>, karma::LorentzVector>> dict_karmaAssociationVectorPairVectorElectronToLV;

        // muons
        karma::Muon dict_karmaMuon;
        edm::Wrapper<karma::Muon> dict_edmWrapperDijetMuon;
        karma::MuonCollection dict_karmaMuonCollection;
        edm::Wrapper<karma::MuonCollection> dict_edmWrapperDijetMuonCollection;
        edm::RefProd<karma::MuonCollection> dict_edmRefProdDijetMuonCollection;

        // muon association vectors
        edm::AssociationVector<edm::RefProd<karma::MuonCollection>, std::vector<int>> dict_karmaAssociationVectorMuonToInt;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::MuonCollection>, std::vector<int>>> dict_edmWrapperDijetAssociationVectorMuonToInt;
        std::pair<edm::Ref<karma::MuonCollection>, int> dict_karmaAssociationVectorPairMuonToInt;
        std::vector<std::pair<edm::Ref<karma::MuonCollection>, int>> dict_karmaAssociationVectorPairVectorMuonToInt;

        edm::AssociationVector<edm::RefProd<karma::MuonCollection>, std::vector<double>> dict_karmaAssociationVectorMuonToDouble;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::MuonCollection>, std::vector<double>>> dict_edmWrapperDijetAssociationVectorMuonToDouble;
        std::pair<edm::Ref<karma::MuonCollection>, double> dict_karmaAssociationVectorPairMuonToDouble;
        std::vector<std::pair<edm::Ref<karma::MuonCollection>, double>> dict_karmaAssociationVectorPairVectorMuonToDouble;

        edm::AssociationVector<edm::RefProd<karma::MuonCollection>, std::vector<bool>> dict_karmaAssociationVectorMuonToBool;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::MuonCollection>, std::vector<bool>>> dict_edmWrapperDijetAssociationVectorMuonToBool;
        std::pair<edm::Ref<karma::MuonCollection>, bool> dict_karmaAssociationVectorPairMuonToBool;
        std::vector<std::pair<edm::Ref<karma::MuonCollection>, bool>> dict_karmaAssociationVectorPairVectorMuonToBool;

        edm::AssociationVector<edm::RefProd<karma::MuonCollection>, std::vector<karma::LorentzVector>> dict_karmaAssociationVectorMuonToLV;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::MuonCollection>, std::vector<karma::LorentzVector>>> dict_edmWrapperDijetAssociationVectorMuonToLV;
        std::pair<edm::Ref<karma::MuonCollection>, karma::LorentzVector> dict_karmaAssociationVectorPairMuonToLV;
        std::vector<std::pair<edm::Ref<karma::MuonCollection>, karma::LorentzVector>> dict_karmaAssociationVectorPairVectorMuonToLV;

        // gen-particles
        karma::GenParticle dict_karmaGenParticle;
        edm::Wrapper<karma::GenParticle> dict_edmWrapperDijetGenParticle;
        karma::GenParticleCollection dict_karmaGenParticleCollection;
        edm::Wrapper<karma::GenParticleCollection> dict_edmWrapperDijetGenParticleCollection;

        // jets
        karma::Jet dict_karmaJet;
        edm::Wrapper<karma::Jet> dict_edmWrapperDijetJet;
        karma::JetCollection dict_karmaJetCollection;
        edm::Wrapper<karma::JetCollection> dict_edmWrapperDijetJetCollection;
        edm::RefProd<karma::JetCollection> dict_edmRefProdDijetJetCollection;

        // jet association vectors
        edm::AssociationVector<edm::RefProd<karma::JetCollection>, std::vector<int>> dict_karmaAssociationVectorJetToInt;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::JetCollection>, std::vector<int>>> dict_edmWrapperDijetAssociationVectorJetToInt;
        std::pair<edm::Ref<karma::JetCollection>, int> dict_karmaAssociationVectorPairJetToInt;
        std::vector<std::pair<edm::Ref<karma::JetCollection>, int>> dict_karmaAssociationVectorPairVectorJetToInt;

        edm::AssociationVector<edm::RefProd<karma::JetCollection>, std::vector<double>> dict_karmaAssociationVectorJetToDouble;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::JetCollection>, std::vector<double>>> dict_edmWrapperDijetAssociationVectorJetToDouble;
        std::pair<edm::Ref<karma::JetCollection>, double> dict_karmaAssociationVectorPairJetToDouble;
        std::vector<std::pair<edm::Ref<karma::JetCollection>, double>> dict_karmaAssociationVectorPairVectorJetToDouble;

        edm::AssociationVector<edm::RefProd<karma::JetCollection>, std::vector<bool>> dict_karmaAssociationVectorJetToBool;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::JetCollection>, std::vector<bool>>> dict_edmWrapperDijetAssociationVectorJetToBool;
        std::pair<edm::Ref<karma::JetCollection>, bool> dict_karmaAssociationVectorPairJetToBool;
        std::vector<std::pair<edm::Ref<karma::JetCollection>, bool>> dict_karmaAssociationVectorPairVectorJetToBool;

        edm::AssociationVector<edm::RefProd<karma::JetCollection>, std::vector<karma::LorentzVector>> dict_karmaAssociationVectorJetToLV;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::JetCollection>, std::vector<karma::LorentzVector>>> dict_edmWrapperDijetAssociationVectorJetToLV;
        std::pair<edm::Ref<karma::JetCollection>, karma::LorentzVector> dict_karmaAssociationVectorPairJetToLV;
        std::vector<std::pair<edm::Ref<karma::JetCollection>, karma::LorentzVector>> dict_karmaAssociationVectorPairVectorJetToLV;

        // MET
        karma::MET dict_karmaMET;
        edm::Wrapper<karma::MET> dict_edmWrapperDijetMET;
        karma::METCollection dict_karmaMETCollection;
        edm::Wrapper<karma::METCollection> dict_edmWrapperDijetMETCollection;
        edm::RefProd<karma::METCollection> dict_edmRefProdDijetMETCollection;

        // MET association vectors
        edm::AssociationVector<edm::RefProd<karma::METCollection>, std::vector<int>> dict_karmaAssociationVectorMETToInt;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::METCollection>, std::vector<int>>> dict_edmWrapperDijetAssociationVectorMETToInt;
        std::pair<edm::Ref<karma::METCollection>, int> dict_karmaAssociationVectorPairMETToInt;
        std::vector<std::pair<edm::Ref<karma::METCollection>, int>> dict_karmaAssociationVectorPairVectorMETToInt;

        edm::AssociationVector<edm::RefProd<karma::METCollection>, std::vector<double>> dict_karmaAssociationVectorMETToDouble;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::METCollection>, std::vector<double>>> dict_edmWrapperDijetAssociationVectorMETToDouble;
        std::pair<edm::Ref<karma::METCollection>, double> dict_karmaAssociationVectorPairMETToDouble;
        std::vector<std::pair<edm::Ref<karma::METCollection>, double>> dict_karmaAssociationVectorPairVectorMETToDouble;

        edm::AssociationVector<edm::RefProd<karma::METCollection>, std::vector<bool>> dict_karmaAssociationVectorMETToBool;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::METCollection>, std::vector<bool>>> dict_edmWrapperDijetAssociationVectorMETToBool;
        std::pair<edm::Ref<karma::METCollection>, bool> dict_karmaAssociationVectorPairMETToBool;
        std::vector<std::pair<edm::Ref<karma::METCollection>, bool>> dict_karmaAssociationVectorPairVectorMETToBool;

        edm::AssociationVector<edm::RefProd<karma::METCollection>, std::vector<karma::LorentzVector>> dict_karmaAssociationVectorMETToLV;
        edm::Wrapper<edm::AssociationVector<edm::RefProd<karma::METCollection>, std::vector<karma::LorentzVector>>> dict_edmWrapperDijetAssociationVectorMETToLV;
        std::pair<edm::Ref<karma::METCollection>, karma::LorentzVector> dict_karmaAssociationVectorPairMETToLV;
        std::vector<std::pair<edm::Ref<karma::METCollection>, karma::LorentzVector>> dict_karmaAssociationVectorPairVectorMETToLV;

        // trigger objects
        karma::TriggerObject dict_karmaTriggerObject;
        edm::Wrapper<karma::TriggerObject> dict_edmWrapperDijetTriggerObject;
        karma::TriggerObjectCollection dict_karmaTriggerObjectCollection;
        edm::Wrapper<karma::TriggerObjectCollection> dict_edmWrapperDijetTriggerObjectCollection;

        // primary vertices
        karma::Vertex dict_karmaVertex;
        edm::Wrapper<karma::Vertex> dict_edmWrapperDijetVertex;
        karma::VertexCollection dict_karmaVertexCollection;
        edm::Wrapper<karma::VertexCollection> dict_edmWrapperDijetVertexCollection;

        // jet-trigger association map
        karma::JetTriggerObjectsMap dict_karmaJetTriggerObjectsMap;
        edm::Wrapper<karma::JetTriggerObjectsMap> dict_edmWrapperDijetJetTriggerObjectsMap;
        karma::JetTriggerObjectsMaps dict_karmaJetTriggerObjectsMaps;
        edm::Wrapper<karma::JetTriggerObjectsMaps> dict_edmWrapperDijetJetTriggerObjectsMaps;

        // jet-genJet association map
        karma::JetGenJetMap dict_karmaJetGenJetMap;
        edm::Wrapper<karma::JetGenJetMap> dict_edmWrapperDijetJetGenJetMap;
        karma::JetGenJetMaps dict_karmaJetGenJetMaps;
        edm::Wrapper<karma::JetGenJetMaps> dict_edmWrapperDijetJetGenJetMaps;

        // value maps to LV
        edm::ValueMap<karma::LorentzVector> dict_karmaLVValueMap;
        edm::Wrapper<edm::ValueMap<karma::LorentzVector>> dict_edmWrapperDijetLVValueMap;

    };
}
