#pragma once

#include <Math/LorentzVector.h>
#include <Math/PtEtaPhiM4D.h>
#include <Math/PositionVector3D.h>
#include <Math/Cartesian3D.h>

#define UNDEFINED_DOUBLE -999;

namespace karma {
    // Lorentz four-vector
    typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double> > LorentzVector;
    // point in space with cartesian internal representation
    typedef ROOT::Math::PositionVector3D<ROOT::Math::Cartesian3D<double> > PositionVector3D;
}

