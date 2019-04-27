//#pragma once

#include "DataFormats/Common/interface/Wrapper.h"
#include "Karma/SkimmingFormats/interface/Event.h"
#include "Karma/SkimmingFormats/interface/Lumi.h"
#include "Karma/SkimmingFormats/interface/Run.h"

namespace {
    struct dictionary {
        // event
        dijet::Event dict_dijetEvent;
        edm::Wrapper<dijet::Event> dict_edmWrapperDijetEvent;
        dijet::EventCollection dict_dijetEventCollection;
        edm::Wrapper<dijet::EventCollection> dict_edmWrapperDijetEventCollection;

        // generator information
        dijet::Event dict_dijetGeneratorQCDInfo;
        edm::Wrapper<dijet::GeneratorQCDInfo> dict_edmWrapperDijetGeneratorQCDInfo;
        dijet::GeneratorQCDInfoCollection dict_dijetGeneratorQCDInfoCollection;
        edm::Wrapper<dijet::GeneratorQCDInfoCollection> dict_edmWrapperDijetGeneratorQCDInfoCollection;

        // luminosity block
        dijet::Lumi dict_dijetLumi;
        edm::Wrapper<dijet::Lumi> dict_edmWrapperDijetLumi;
        dijet::LumiCollection dict_dijetLumiCollection;
        edm::Wrapper<dijet::LumiCollection> dict_edmWrapperDijetLumiCollection;

        // run
        dijet::Run dict_dijetRun;
        edm::Wrapper<dijet::Run> dict_edmWrapperDijetRun;
        dijet::RunCollection dict_dijetRunCollection;
        edm::Wrapper<dijet::RunCollection> dict_edmWrapperDijetRunCollection;

        // HLT infos
        dijet::HLTPathInfo dict_dijetHLTPathInfo;
        edm::Wrapper<dijet::HLTPathInfo> dict_edmWrapperDijetHLTPathInfo;
        dijet::HLTPathInfos dict_dijetHLTPathInfos;
        edm::Wrapper<dijet::HLTPathInfos> dict_edmWrapperDijetHLTPathInfos;

        // -- event objects

        // lvs
        dijet::LV dict_dijetLV;
        edm::Wrapper<dijet::LV> dict_edmWrapperDijetLV;
        dijet::LVCollection dict_dijetLVCollection;
        edm::Wrapper<dijet::LVCollection> dict_edmWrapperDijetLVCollection;

        // lvs
        dijet::GenParticle dict_dijetGenParticle;
        edm::Wrapper<dijet::GenParticle> dict_edmWrapperDijetGenParticle;
        dijet::GenParticleCollection dict_dijetGenParticleCollection;
        edm::Wrapper<dijet::GenParticleCollection> dict_edmWrapperDijetGenParticleCollection;

        // jets
        dijet::Jet dict_dijetJet;
        edm::Wrapper<dijet::Jet> dict_edmWrapperDijetJet;
        dijet::JetCollection dict_dijetJetCollection;
        edm::Wrapper<dijet::JetCollection> dict_edmWrapperDijetJetCollection;

        // MET
        dijet::MET dict_dijetMET;
        edm::Wrapper<dijet::MET> dict_edmWrapperDijetMET;
        dijet::METCollection dict_dijetMETCollection;
        edm::Wrapper<dijet::METCollection> dict_edmWrapperDijetMETCollection;

        // trigger objects
        dijet::TriggerObject dict_dijetTriggerObject;
        edm::Wrapper<dijet::TriggerObject> dict_edmWrapperDijetTriggerObject;
        dijet::TriggerObjectCollection dict_dijetTriggerObjectCollection;
        edm::Wrapper<dijet::TriggerObjectCollection> dict_edmWrapperDijetTriggerObjectCollection;

        // primary vertices
        dijet::Vertex dict_dijetVertex;
        edm::Wrapper<dijet::Vertex> dict_edmWrapperDijetVertex;
        dijet::VertexCollection dict_dijetVertexCollection;
        edm::Wrapper<dijet::VertexCollection> dict_edmWrapperDijetVertexCollection;

        // jet-trigger association map
        dijet::JetTriggerObjectsMap dict_dijetJetTriggerObjectsMap;
        edm::Wrapper<dijet::JetTriggerObjectsMap> dict_edmWrapperDijetJetTriggerObjectsMap;
        dijet::JetTriggerObjectsMaps dict_dijetJetTriggerObjectsMaps;
        edm::Wrapper<dijet::JetTriggerObjectsMaps> dict_edmWrapperDijetJetTriggerObjectsMaps;

        // jet-genJet association map
        dijet::JetGenJetMap dict_dijetJetGenJetMap;
        edm::Wrapper<dijet::JetGenJetMap> dict_edmWrapperDijetJetGenJetMap;
        dijet::JetGenJetMaps dict_dijetJetGenJetMaps;
        edm::Wrapper<dijet::JetGenJetMaps> dict_edmWrapperDijetJetGenJetMaps;

    };
}
