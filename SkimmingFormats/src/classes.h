//#pragma once

#include "DataFormats/Common/interface/Wrapper.h"
#include "Karma/SkimmingFormats/interface/Event.h"
#include "Karma/SkimmingFormats/interface/Lumi.h"
#include "Karma/SkimmingFormats/interface/Run.h"

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

        // muons
        karma::Muon dict_karmaMuon;
        edm::Wrapper<karma::Muon> dict_edmWrapperDijetMuon;
        karma::MuonCollection dict_karmaMuonCollection;
        edm::Wrapper<karma::MuonCollection> dict_edmWrapperDijetMuonCollection;

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

        // MET
        karma::MET dict_karmaMET;
        edm::Wrapper<karma::MET> dict_edmWrapperDijetMET;
        karma::METCollection dict_karmaMETCollection;
        edm::Wrapper<karma::METCollection> dict_edmWrapperDijetMETCollection;

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

    };
}
