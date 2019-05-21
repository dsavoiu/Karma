#pragma once

// system include files
#include <memory>
#include <stdexcept>

// user include files
#include "Karma/Skimming/interface/GenericAssociationProducer.h"
#include "Karma/SkimmingFormats/interface/Defaults.h"  // for karma::LorentzVector
#include "FWCore/Utilities/interface/EDMException.h"

#include "DataFormats/Common/interface/ValueMap.h"

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"

//
// class declaration
//
namespace karma {

    /**
     * Template for a producer of `edm::ValueMaps`.
     *
     * Partial specialization of `GenericAssociationProducer`
     */
    template<typename TInputCollection, typename TValue, typename... ExtensionTypes>
    class ValueMapProducerBase : public GenericAssociationProducer<
        TInputCollection,
        edm::ValueMap<TValue>,
        ExtensionTypes...> {

      public:
        typedef typename edm::ValueMap<TValue> TAssociation;
        typedef typename GenericAssociationProducer<TInputCollection, TAssociation, ExtensionTypes...>::TInputSingle TInputSingle;

        explicit ValueMapProducerBase(const edm::ParameterSet& pSet) :  GenericAssociationProducer<TInputCollection, TAssociation, ExtensionTypes...>(pSet) {};
        ~ValueMapProducerBase() {};

        // -- pSet descriptions for CMSSW help info and validation
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
            GenericAssociationProducer<TInputCollection, edm::ValueMap<TValue>, ExtensionTypes...>::fillDescriptions(descriptions);
        };

        /**
         * Called by 'produce'. Contains the implementation to fill
         * the output association object.
         *
         * Specialization for filling `edm::ValueMaps`.
         *
         * Calls 'produceValue' for each object in the input collection
         * to produce the associated value.
         */
        virtual std::unique_ptr<TAssociation> makeAssociation(
            const edm::Handle<TInputCollection>& referencedCollection,
            const std::string& transientMapKey) {

            // create output value map
            std::unique_ptr<TAssociation> outputAssociation(new TAssociation());

            typename TAssociation::Filler filler(*outputAssociation);
            std::vector<TValue> values(referencedCollection->size());
            
            // call produceSingle() for every element of the input collection
            for (size_t i = 0; i < referencedCollection->size(); ++i) {
                try {
                    // call `produceValue()` to obtain the associated value
                    values[i] = this->produceValue(
                        referencedCollection->at(i),
                        // use <transientMapKey> spec parameter for lookup in original object
                        transientMapKey
                    );
                }
                catch (std::out_of_range& e) {
                    edm::Exception exception(edm::errors::NotFound);
                    exception << "Could not find value for key '" << transientMapKey << "' "
                              << "in transient maps of product '"
                              << referencedCollection.provenance()->branchName()
                              <<  "', but it is needed to create the ValueMap. Aborting!";
                    throw exception;
                }
            }
            
            filler.insert(referencedCollection, values.begin(), values.end());
            filler.fill();

            return outputAssociation;
        };

        /**
         * Called by 'produce'. Returns the value associated to an
         * object `in` in the input collection and a key in ?one of?
         * the transient map contained in the data format.
         *
         * Should be implemented by all derived classes.
         */
        virtual TValue produceValue(const TInputSingle& in, const std::string& transientMapKey) = 0;

    };




    // -- partial template specialization for common value types

    // Note: C++11 does not support explicit partial specializations of
    // members of class templates, so we use inheritance instead

    // bool
    template<typename TInputCollection, typename... ExtensionTypes>
    class BoolValueMapProducer : public ValueMapProducerBase<TInputCollection, bool, ExtensionTypes...> {

        // inherit all constructors from base class (only C++11)
        using ValueMapProducerBase<TInputCollection, bool, ExtensionTypes...>::ValueMapProducerBase;

        virtual bool produceValue(
            const typename TInputCollection::value_type& in,
            const std::string& transientMapKey) {

            return in.transientBools_.at(transientMapKey);
        }
    };

    // int
    template<typename TInputCollection, typename... ExtensionTypes>
    class IntValueMapProducer : public ValueMapProducerBase<TInputCollection, int, ExtensionTypes...> {

        // inherit all constructors from base class (only C++11)
        using ValueMapProducerBase<TInputCollection, int, ExtensionTypes...>::ValueMapProducerBase;

        virtual int produceValue(
            const typename TInputCollection::value_type& in,
            const std::string& transientMapKey) {

            return in.transientInts_.at(transientMapKey);
        }
    };

    // double
    template<typename TInputCollection, typename... ExtensionTypes>
    class DoubleValueMapProducer : public ValueMapProducerBase<TInputCollection, double, ExtensionTypes...> {

        // inherit all constructors from base class (only C++11)
        using ValueMapProducerBase<TInputCollection, double, ExtensionTypes...>::ValueMapProducerBase;

        virtual double produceValue(
            const typename TInputCollection::value_type& in,
            const std::string& transientMapKey) {

            return in.transientDoubles_.at(transientMapKey);
        }
    };

    // karma::LorentzVector
    template<typename TInputCollection, typename... ExtensionTypes>
    class LVValueMapProducer : public ValueMapProducerBase<TInputCollection, karma::LorentzVector, ExtensionTypes...> {

        // inherit all constructors from base class (only C++11)
        using ValueMapProducerBase<TInputCollection, karma::LorentzVector, ExtensionTypes...>::ValueMapProducerBase;

        virtual karma::LorentzVector produceValue(
            const typename TInputCollection::value_type& in,
            const std::string& transientMapKey) {

            return in.transientLVs_.at(transientMapKey);
        }
    };

    //
    // constants, enums and typedefs
    //


    //
    // static data member definitions
    //

}  // end namespace
