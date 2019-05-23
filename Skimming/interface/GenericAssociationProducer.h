#pragma once

// system include files
#include <memory>
#include <stdexcept>

// user include files
#include "Karma/Common/interface/EDMTools/Util.h"
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

    // -- base producer class

    /**
     * Template for a generic producer of "Associations", i.e. collections
     * that reference other collections in the same file. Examples of
     * association objects are `edm::ValueMap` and `edm::AssociationVector`.
     *
     * This producer reads an collection of Karma objects (of type
     * TInputCollection) and fills one or more Association objects
     * (of type TAssociation) from the transient map stored for each
     * object in the collection.
     *
     * The transient maps (part of the data formats) must be filled by
     * another producer beforehand.
     *
     * Multithreading extensions can be used together with this template
     * by adding the respective template arguments after the first two.
     */
    template<typename TInputCollection, typename TAssociation, typename... ExtensionTypes>
    class GenericAssociationProducer : public edm::stream::EDProducer<ExtensionTypes...> {

      public:
        typedef typename TInputCollection::value_type TInputSingle;

        explicit GenericAssociationProducer(const edm::ParameterSet& pSet) : m_configPSet(pSet) {

            // -- register products
            const auto& associationSpecs = pSet.getParameter<std::vector<edm::ParameterSet>>("associationSpec");
            for (size_t iSpec = 0; iSpec < associationSpecs.size(); ++iSpec) {
                const auto& associationSpec = associationSpecs[iSpec];

                this->template produces<TAssociation>(associationSpec.getParameter<std::string>("name"));
                m_mapNameToTransientKey[associationSpec.getParameter<std::string>("name")] = associationSpec.getParameter<std::string>("transientMapKey");
            }

            // -- declare which collections are consumed and create tokens
            inputCollectionToken_ = this->template consumes<TInputCollection>(this->m_configPSet.template getParameter<edm::InputTag>("inputCollection"));
        };
        ~GenericAssociationProducer() {};


        // -- pSet descriptions for CMSSW help info and validation
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
            // The following says we do not know what parameters are allowed so do no validation
            // Please change this to state exactly what you do use, even if it is no parameters
            edm::ParameterSetDescription desc;
            desc.setUnknown();
            descriptions.addDefault(desc);
            // TODO: fill this in
        };

        // -- "regular" per-Event 'produce' method
        void produce(edm::Event& event, const edm::EventSetup& setup) {
            karma::util::getByTokenOrThrow(event, this->inputCollectionToken_, this->inputCollectionHandle_);

            for (const auto& mapNameAndTransientKey : m_mapNameToTransientKey) {

                std::unique_ptr<TAssociation> outputAssociation = std::move(
                    this->makeAssociation(this->inputCollectionHandle_, mapNameAndTransientKey.second)
                );

                // store the value map under <mapName> spec parameter
                event.put(std::move(outputAssociation), mapNameAndTransientKey.first);
            }
        };

        /**
         * Called by 'produce'. Contains the implementation to create
         * and fill the output association object.
         *
         * Must be implemented by derived classes.
         */
        virtual std::unique_ptr<TAssociation> makeAssociation(
            const edm::Handle<TInputCollection>& referencedCollection,
            const std::string& transientMapKey) = 0;

        // ----------member data ---------------------------

      protected:

        const edm::ParameterSet& m_configPSet;
        std::map<std::string, std::string> m_mapNameToTransientKey;

      private:
        // -- handles and tokens
        typename edm::Handle<TInputCollection> inputCollectionHandle_;
        edm::EDGetTokenT<TInputCollection> inputCollectionToken_;

    };

    //
    // constants, enums and typedefs
    //


    //
    // static data member definitions
    //

}  // end namespace
