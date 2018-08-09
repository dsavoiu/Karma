//#pragma once

#include "DataFormats/Common/interface/Wrapper.h"
#include "DijetAnalysis/AnalysisFormats/interface/Ntuple.h"

namespace {
    struct dictionaryAnalysis {
        // ntuple
        dijet::NtupleEntry dict_dijetNtupleEntry;
        edm::Wrapper<dijet::NtupleEntry> dict_edmWrapperDijetNtupleEntry;
        dijet::Ntuple dict_dijetNtuple;
        edm::Wrapper<dijet::Ntuple> dict_edmWrapperDijetNtuple;

    };
}
