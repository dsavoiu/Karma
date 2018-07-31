#pragma once

#include <vector>

#include "Defaults.h"


namespace dijet {
    /**
     * Helper data structure to store information about a particular HLT path
     *
     */
    struct HLTPathInfo {
        HLTPathInfo() {};

        HLTPathInfo(std::string name, unsigned int indexInMenu, int filtersStartIndex, const std::vector<std::string>& filterNames) :
            name_(name),
            indexInMenu_(indexInMenu),
            filtersStartIndex_(filtersStartIndex),
            filterNames_(filterNames) {};

        size_t numFilters() const { return filterNames_.size(); };

        std::string name_;
        unsigned int indexInMenu_;
        int filtersStartIndex_;
        std::vector<std::string> filterNames_;
    };
    typedef std::vector<dijet::HLTPathInfo> HLTPathInfos;


    class Run {
      public:
        // -- event metadata
        long run = -1;

        // -- kinematics of the two leading jets
        std::string triggerMenuName;
        HLTPathInfos triggerPathInfos;

    };
    typedef std::vector<dijet::Run> RunCollection;

}
