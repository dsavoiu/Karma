#pragma once

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"



//
// class declaration
//
namespace dijet {

    // -- main producer

    /**
     * Template for a collection producer.
     * This producer reads an input collection and calls a user-defined
     * method for each element to produce an output collection.
     *
     * The two template arguments 'TInputCollection' and 'TOutputCollection'
     * specify the type of the input and output collections, respectively.
     *
     * Multithreading extensions can be used together with this template
     * by adding the respective template arguments after the first two.
     */
    template<typename TInputCollection, typename TOutputCollection, typename... ExtensionTypes>
    class CollectionProducerBase : public edm::stream::EDProducer<ExtensionTypes...> {

      public:
        typedef typename TInputCollection::value_type TInputSingle;
        typedef typename TOutputCollection::value_type TOutputSingle;

        explicit CollectionProducerBase(const edm::ParameterSet& pSet) : m_configPSet(pSet) {
            // -- register product
            this->template produces<TOutputCollection>();

            // -- declare which collections are consumed and create tokens
            inputCollectionToken_ = this->template consumes<TInputCollection>(this->m_configPSet.template getParameter<edm::InputTag>("inputCollection"));
        };
        ~CollectionProducerBase() {};


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
        virtual void produce(edm::Event& event, const edm::EventSetup& setup) {
            bool obtained = event.getByToken(this->inputCollectionToken_, this->inputCollectionHandle_);
            assert(obtained);

            // create output collection
            std::unique_ptr<TOutputCollection> outputJetCollection(new TOutputCollection());

            // call produceSingle() for every element of the input collection
            for (size_t i = 0; i < this->inputCollectionHandle_->size(); ++i) {
                // skip elements rejected by `acceptSingle()`
                if (!this->acceptSingle(this->inputCollectionHandle_->at(i))) {
                    continue;
                }
                // default-construct an output object in-place in the output collection
                outputJetCollection->emplace_back();
                this->produceSingle(this->inputCollectionHandle_->at(i), outputJetCollection->back());
            }

            event.put(std::move(outputJetCollection));
        };

        virtual void produceSingle(const TInputSingle& in, TOutputSingle& out) = 0;
        inline virtual bool acceptSingle(const TInputSingle& in) {
            return true;  // accept all by default
        };


        // ----------member data ---------------------------

      protected:

        const edm::ParameterSet& m_configPSet;

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
