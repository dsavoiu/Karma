#pragma once

// system include files
#include <memory>
#include <iostream>

// user include files
#include "Karma/Common/interface/Util.h"

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"
//#include "FWCore/Utilities/interface/Transition.h"  // CMSSW 9+

// -- base classes for caches
#include "Karma/Common/interface/Caches.h"

// -- input data formats
#include "DataFormats/PatCandidates/interface/Jet.h"


//
// class declaration
//
namespace karma {

    // -- declare global caches accessible by the processing streams

    /** Cache containing resources which do not change
     *  for the entire duration of the skiming job.
     */
    class ExampleGlobalCache : public karma::GlobalCacheWithOutputFile {

      public:
        ExampleGlobalCache(const edm::ParameterSet& pSet) :
            karma::GlobalCacheWithOutputFile(pSet, "outputFile") {

            // -- user code here: initialize cache

            // -- user code here: create output histograms/objects
            //makeHist1D("Reference", "Reference", triggerEfficiencyBinning_);

        };

        // -- user code here: immmutable (config) cache entries


        // -- user code here: mutable cache entries


        // -- output file, memory histogram storage and control structures
        mutable std::unique_ptr<TFile> outputFile_;
        mutable edm::SerialTaskQueue queue_;
        mutable std::map<std::string, std::shared_ptr<TH1D>> outputHistograms_;

    };

    /** Cache containing resources which do not change
     *  for the entire duration of a luminosity block
     */
    class ExampleLumiCache : public karma::CacheBase {

      public:
        ExampleLumiCache(const edm::ParameterSet& pSet) : karma::CacheBase(pSet) {

            // -- user code here: initialize cache

        };

        // -- user code here: immmutable (config) cache entries


        // -- user code here: mutable cache entries


    };


    /** Cache containing resources which do not change
     *  for the entire duration of a run
     */
    class ExampleRunCache : public karma::CacheBase {

      public:
        ExampleRunCache(const edm::ParameterSet& pSet) : karma::CacheBase(pSet) {

            // -- user code here: initialize cache

        };

        // -- user code here: immmutable (config) cache entries


        // -- user code here: mutable cache entries


    };


    /** Cache containing resources which accumulate during a run.
     */
    class ExampleRunSummaryCache : public karma::CacheBase {

      public:
        ExampleRunSummaryCache(const edm::ParameterSet& pSet) : karma::CacheBase(pSet) {

            // -- user code here: initialize cache

        };

        // -- user code here: immmutable (config) cache entries


        // -- user code here: mutable cache entries

    };


    // -- the main EDAnalyzer

    class ExampleAnalyzer : public edm::stream::EDAnalyzer<
        // declare which extensions (e.g. caches) are used
        edm::GlobalCache<karma::ExampleGlobalCache>,
        edm::RunCache<karma::ExampleRunCache>,
        edm::RunSummaryCache<karma::ExampleRunSummaryCache>> {

      public:
        explicit ExampleAnalyzer(const edm::ParameterSet&, const karma::ExampleGlobalCache*);
        ~ExampleAnalyzer();

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        // -- initialization at beginning of stream
        void beginStream(edm::StreamID);

        // -- global cache extension methods
        static std::unique_ptr<karma::ExampleGlobalCache> initializeGlobalCache(const edm::ParameterSet& pSet);
        static void globalEndJob(karma::ExampleGlobalCache*);

        // -- run cache extension methods
        static std::shared_ptr<karma::ExampleRunCache> globalBeginRun(const edm::Run&, const edm::EventSetup&, const GlobalCache*);
        static void globalEndRun(const edm::Run&, const edm::EventSetup&, const RunContext*) {/* noop */};

        // -- run summary cache extension methods
        static std::shared_ptr<karma::ExampleRunSummaryCache> globalBeginRunSummary(const edm::Run&, const edm::EventSetup&, const RunContext*);
        void endRunSummary(const edm::Run&, const edm::EventSetup&, karma::ExampleRunSummaryCache*) const;
        static void globalEndRunSummary(const edm::Run&, const edm::EventSetup&, const RunContext*, karma::ExampleRunSummaryCache*);

        // -- "regular" per-Event 'analyze' method
        virtual void analyze(const edm::Event&, const edm::EventSetup&);

        // -- wrap-up at end of stream
        void endStream();


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        // -- handles and tokens
        typename edm::Handle<edm::View<pat::Jet>> jetCollectionHandle;
        edm::EDGetTokenT<edm::View<pat::Jet>> jetCollectionToken;


        // -- per-stream "scratch space"
        //int m_mySratchVariable = 42;

    };

    //
    // constants, enums and typedefs
    //


    //
    // static data member definitions
    //

}  // end namespace
