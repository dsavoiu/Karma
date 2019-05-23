#pragma once

#include "ValueMapProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"

// -- input data formats
#include <Karma/SkimmingFormats/interface/Event.h>


namespace karma {

    typedef typename karma::BoolValueMapProducer<karma::JetCollection> JetIdValueMapProducer;
    typedef typename karma::IntValueMapProducer<karma::JetCollection> JetPileupIdValueMapProducer;
    typedef typename karma::DoubleValueMapProducer<karma::JetCollection> JetPileupIdDiscriminantValueMapProducer;

}  // end namespace
