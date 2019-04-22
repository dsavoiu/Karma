#pragma once

#include <vector>

#include "Defaults.h"

namespace karma {
    class Lumi {
      public:
        // -- Lumi metadata
        long run = -1;
        int lumi = -1;

    };

    typedef std::vector<karma::Lumi> LumiCollection;
}
