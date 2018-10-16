#pragma once

#include <memory>

#include <TH1.h>
#include <TFile.h>

#include "FWCore/Concurrency/interface/SerialTaskQueue.h"


namespace dijet {

    // -- declare global caches accessible by the processing streams

    /** Base class for a cache
     */
    class CacheBase {

      public:
        CacheBase() : pSet_(edm::ParameterSet()) {};  // use dummy PSet
        CacheBase(const edm::ParameterSet& pSet) : pSet_(pSet) {};

        const edm::ParameterSet& pSet_;

    };


    /** Global Cache containing an output file
     */
    class GlobalCacheWithOutputFile : public CacheBase {

      public:
        GlobalCacheWithOutputFile(const edm::ParameterSet& pSet, const std::string& outputFileName) :
            CacheBase(pSet),
            outputFile_(new TFile(outputFileName.c_str(), "RECREATE")) {

            // -- user code here: initialize cache

            // -- user code here: create output histograms/objects
            //makeHist1D("Reference", "Reference", triggerEfficiencyBinning_);

        };

        std::shared_ptr<TH1D> makeHist1D(const std::string& name, const std::string& title, const std::vector<double>& bins) {
            // serialized creation of histogram in file
            queue_.pushAndWait(
                [&]() {
                    edm::LogInfo("GlobalCacheWithOutputFile") << "Creating histogram '" << name << "' in output file...";
                    outputHistograms_[name] = std::make_shared<TH1D>(name.c_str(), title.c_str(), bins.size() - 1, &bins[0]);
                    outputHistograms_[name]->SetDirectory(0);
                }
            );
            return outputHistograms_[name];
        };

        std::shared_ptr<TH1D> getHist1D(const std::string& name) const {
            return outputHistograms_[name];
        };

        void addToHist1D(const std::string& name, const std::shared_ptr<TH1D>& hist2) const {
            // serialized addition to file
            queue_.pushAndWait(
                [&]() {
                    edm::LogInfo("GlobalCacheWithOutputFile") << "Adding to histogram '" << name << "' in output file...";
                    outputHistograms_[name]->Add(&(*hist2));
                }
            );
        };

        void writeAllAndCloseFile() {
            // writing of all histograms to file
            outputFile_->cd();
            for (const auto& nameAndHist : outputHistograms_) {
                edm::LogInfo("GlobalCacheWithOutputFile") << "Associating histogram '" << nameAndHist.first << "' with output file...";
                nameAndHist.second->SetDirectory(&(*outputFile_));
                edm::LogInfo("GlobalCacheWithOutputFile") << "Writing histogram '" << nameAndHist.first << "' to output file...";
                nameAndHist.second->Write();
            }
            outputFile_->Close();
        }

        // -- user code here: immmutable (config) cache entries


        // -- user code here: mutable cache entries


        // -- output file, memory histogram storage and control structures
        mutable std::unique_ptr<TFile> outputFile_;
        mutable edm::SerialTaskQueue queue_;
        mutable std::map<std::string, std::shared_ptr<TH1D>> outputHistograms_;

    };
}
