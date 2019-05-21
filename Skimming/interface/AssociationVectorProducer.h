#pragma once

// system include files
#include <memory>
#include <stdexcept>

// user include files
#include "Karma/Skimming/interface/GenericAssociationProducer.h"
#include "Karma/SkimmingFormats/interface/Defaults.h"  // for karma::LorentzVector
#include "FWCore/Utilities/interface/EDMException.h"

#include "DataFormats/Common/interface/AssociationVector.h"

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
     * Template for a producer of `edm::AssociationVectors`.
     *
     * Partial specialization of `GenericAssociationProducer`
     */
    template<typename TInputCollection, typename TValue, typename... ExtensionTypes>
    class AssociationVectorProducerBase : public GenericAssociationProducer<
        TInputCollection,
        edm::AssociationVector<edm::RefProd<TInputCollection>, std::vector<TValue>>,
        ExtensionTypes...> {

      public:
        typedef typename edm::AssociationVector<edm::RefProd<TInputCollection>, std::vector<TValue>> TAssociation;
        typedef typename GenericAssociationProducer<TInputCollection, TAssociation, ExtensionTypes...>::TInputSingle TInputSingle;

        explicit AssociationVectorProducerBase(const edm::ParameterSet& pSet) :  GenericAssociationProducer<TInputCollection, TAssociation, ExtensionTypes...>(pSet) {};
        ~AssociationVectorProducerBase() {};

        // -- pSet descriptions for CMSSW help info and validation
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
            GenericAssociationProducer<TInputCollection, edm::ValueMap<TValue>, ExtensionTypes...>::fillDescriptions(descriptions);
        };

        /**
         * Called by 'produce'. Contains the implementation to fill
         * the output association object.
         *
         * Specialization for filling `edm::AssociationVectors`.
         *
         * Calls 'produceValue' for each object in the input collection
         * to produce the associated value.
         */
        virtual std::unique_ptr<TAssociation> makeAssociation(
            const edm::Handle<TInputCollection>& referencedCollection,
            const std::string& transientMapKey) {

            // create output association vector
            std::unique_ptr<TAssociation> outputAssociation(new TAssociation(
                edm::RefProd<TInputCollection>(referencedCollection)
            ));

            // call produceSingle() for every element of the input collection
            for (size_t i = 0; i < referencedCollection->size(); ++i) {
                try {
                    // call `produceValue()` to obtain the associated value
                    (*outputAssociation)[edm::Ref<TInputCollection>(referencedCollection, i)] =
                        this->produceValue(
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
                              <<  "', but it is needed to create the AssociationVector. Aborting!";
                    throw exception;
                }
            }

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
    class BoolAssociationVectorProducer : public AssociationVectorProducerBase<TInputCollection, bool, ExtensionTypes...> {

        // inherit all constructors from base class (only C++11)
        using AssociationVectorProducerBase<TInputCollection, bool, ExtensionTypes...>::AssociationVectorProducerBase;

        virtual bool produceValue(
            const typename TInputCollection::value_type& in,
            const std::string& transientMapKey) {

            return in.transientBools_.at(transientMapKey);
        }
    };

    // int
    template<typename TInputCollection, typename... ExtensionTypes>
    class IntAssociationVectorProducer : public AssociationVectorProducerBase<TInputCollection, int, ExtensionTypes...> {

        // inherit all constructors from base class (only C++11)
        using AssociationVectorProducerBase<TInputCollection, int, ExtensionTypes...>::AssociationVectorProducerBase;

        virtual int produceValue(
            const typename TInputCollection::value_type& in,
            const std::string& transientMapKey) {

            return in.transientInts_.at(transientMapKey);
        }
    };

    // double
    template<typename TInputCollection, typename... ExtensionTypes>
    class DoubleAssociationVectorProducer : public AssociationVectorProducerBase<TInputCollection, double, ExtensionTypes...> {

        // inherit all constructors from base class (only C++11)
        using AssociationVectorProducerBase<TInputCollection, double, ExtensionTypes...>::AssociationVectorProducerBase;

        virtual double produceValue(
            const typename TInputCollection::value_type& in,
            const std::string& transientMapKey) {

            return in.transientDoubles_.at(transientMapKey);
        }
    };

    // karma::LorentzVector
    template<typename TInputCollection, typename... ExtensionTypes>
    class LVAssociationVectorProducer : public AssociationVectorProducerBase<TInputCollection, karma::LorentzVector, ExtensionTypes...> {

        // inherit all constructors from base class (only C++11)
        using AssociationVectorProducerBase<TInputCollection, karma::LorentzVector, ExtensionTypes...>::AssociationVectorProducerBase;

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
