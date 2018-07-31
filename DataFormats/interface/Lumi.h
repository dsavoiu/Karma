#pragma once

#include <vector>

#include "Defaults.h"

namespace dijet {
    class Lumi {
      public:
        // -- Lumi metadata
        long run = -1;
        int lumi = -1;

    };

    typedef std::vector<dijet::Lumi> LumiCollection;
}
