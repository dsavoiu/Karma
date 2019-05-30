//#pragma once

#include "DataFormats/Common/interface/Wrapper.h"
#include "Karma/ZJetAnalysisFormats/interface/Ntuple.h"

namespace {
    struct dictionaryAnalysis {
        // ntuple
        zjet::NtupleEntry dict_zJetNtupleEntry;
        edm::Wrapper<zjet::NtupleEntry> dict_edmWrapperZJetNtupleEntry;
        zjet::Ntuple dict_zJetNtuple;
        edm::Wrapper<zjet::Ntuple> dict_edmWrapperZJetNtuple;

    };
}
