#pragma once

#include <vector>

#include "Defaults.h"

namespace dijet {
    class Event {
      public:
        // -- event metadata
        long run = -1;
        int lumi = -1;
        long event = -1;
        int bx = -1;

        // -- trigger decisions
        std::vector<bool> hltBits;

        // it's easier to store these once per event rather than once per lumi-section
        std::vector<int> triggerPathHLTPrescales;
        std::vector<int> triggerPathL1Prescales;

    };
    typedef std::vector<dijet::Event> EventCollection;

    /**
     * Simple lorentz vector class
     */
    class LV {
      public:

        // -- kinematics
        dijet::LorentzVector p4;

    };
    typedef std::vector<dijet::LV> LVCollection;

    /**
     * Jet class
     */
    class Jet : public dijet::LV {
      public:


    };
    typedef std::vector<dijet::Jet> JetCollection;

    /**
     * Trigger Object class
     */
    class TriggerObject : public dijet::LV {
      public:

        std::vector<int> types;

    };
    typedef std::vector<dijet::TriggerObject> TriggerObjectCollection;
}
