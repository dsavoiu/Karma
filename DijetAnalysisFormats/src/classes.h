//#pragma once

#include "DataFormats/Common/interface/Wrapper.h"
#include "Karma/DijetAnalysisFormats/interface/Ntuple.h"
#include "Karma/DijetAnalysisFormats/interface/NtupleV2.h"

namespace {
    struct dictionaryAnalysis {
        // ntuple
        dijet::NtupleEntry dict_dijetNtupleEntry;
        edm::Wrapper<dijet::NtupleEntry> dict_edmWrapperDijetNtupleEntry;
        dijet::Ntuple dict_dijetNtuple;
        edm::Wrapper<dijet::Ntuple> dict_edmWrapperDijetNtuple;

        // ntuple
        dijet::NtupleV2Entry dict_dijetNtupleV2Entry;
        edm::Wrapper<dijet::NtupleV2Entry> dict_edmWrapperDijetNtupleV2Entry;
        dijet::NtupleV2 dict_dijetNtupleV2;
        edm::Wrapper<dijet::NtupleV2> dict_edmWrapperDijetNtupleV2;

    };
}
