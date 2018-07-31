#pragma once

#include <Math/LorentzVector.h>
#include <Math/PtEtaPhiM4D.h>

#define UNDEFINED_DOUBLE -999;

namespace dijet {
    typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double> > LorentzVector;
}

