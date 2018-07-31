//#pragma once

#include "DataFormats/Common/interface/Wrapper.h"
#include "DijetAnalysis/DataFormats/interface/Event.h"
#include "DijetAnalysis/DataFormats/interface/Lumi.h"
#include "DijetAnalysis/DataFormats/interface/Run.h"

namespace {
    struct dictionary {
        // event
        dijet::Event dict_dijetEvent;
        edm::Wrapper<dijet::Event> dict_edmWrapperDijetEvent;
        dijet::EventCollection dict_dijetEventCollection;
        edm::Wrapper<dijet::EventCollection> dict_edmWrapperDijetEventCollection;

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
        
        // jets
        dijet::Jet dict_dijetJet;
        edm::Wrapper<dijet::Jet> dict_edmWrapperDijetJet;
        dijet::JetCollection dict_dijetJetCollection;
        edm::Wrapper<dijet::JetCollection> dict_edmWrapperDijetJetCollection;
        
        // trigger objects
        dijet::TriggerObject dict_dijetTriggerObject;
        edm::Wrapper<dijet::TriggerObject> dict_edmWrapperDijetTriggerObject;
        dijet::TriggerObjectCollection dict_dijetTriggerObjectCollection;
        edm::Wrapper<dijet::TriggerObjectCollection> dict_edmWrapperDijetTriggerObjectCollection;

    };
}
