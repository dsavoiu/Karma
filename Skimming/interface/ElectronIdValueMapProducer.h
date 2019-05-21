#pragma once

#include "ValueMapProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"

// -- input data formats
#include <Karma/SkimmingFormats/interface/Event.h>


namespace karma {

    typedef typename karma::IntValueMapProducer<karma::ElectronCollection> ElectronIdValueMapProducer;

}  // end namespace
