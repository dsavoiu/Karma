#pragma once

#include <algorithm>
#include <vector>
#include <numeric>
#include <exception>

#include "yaml-cpp/yaml.h"


class FlexNode {
    /**
     * A node of the bin tree created by `FlexGrid`.
     */
  public:
    /**
     * Main constructor (from YAML node)
     */
    explicit FlexNode(const YAML::Node& node) {
        if (!node["bins"]) {
            throw std::runtime_error("Mandatory key 'bins' not provided!");
        }
        bins_ = node["bins"].as<std::vector<double>>();
        if (node["substructure"]) {
            int i = 0;
            for (const auto& subnode : node["substructure"]) {
                substructure_.emplace_back(subnode);
                ++i;
            }
        }
    };

    /**
     * Helper constructor (from YAML file)
     */
    explicit FlexNode(const std::string& yamlFile) : FlexNode(YAML::LoadFile(yamlFile)) {};

    /**
     * "Manual" constructor (from bins and substructure)
     */
    FlexNode(const std::vector<double> bins, const std::vector<FlexNode> substructure) :
        bins_(bins), substructure_(substructure) {
    };

    /** Retrieve bin edges for this node */
    const std::vector<double>& getBins() const { return bins_; }

    /** Get child nodes */
    std::vector<FlexNode>& getSubstructure() { return substructure_; }

    /** Get child node with given index */
    const FlexNode& getSubnode(int idx) const { return substructure_.at(idx); }

    /** Get global index assigned to bin */
    const int getGlobalBinIndex(int localIndex) const { return globalBinIndices_[localIndex]; }

    /** Assign a global index to each bin */
    void setGlobalBinIndices(const std::vector<int> globalBinIndices) { globalBinIndices_ = globalBinIndices; }

    /** True if bin has child nodes */
    bool hasSubstructure() const { return (substructure_.size() > 0); }

  private:

    std::vector<double> bins_;
    std::vector<FlexNode> substructure_;
    std::vector<int> globalBinIndices_;
};

class FlexGrid {
    /**
     * Class for representing a nested structure of bins with
     * varying binning structure. Establishes contiguous indexing
     * of bins and provides methods to retrieve the global bin index
     * from a tuple of (unbinned) values.
     */
  public:
    explicit FlexGrid(const std::string& yamlFile) : _rootFlexNode(yamlFile) {
        _indexBins(_rootFlexNode, 0);
    };

  private:

    static int _indexBins(FlexNode& node, int idxOffset=0) {
        if (node.hasSubstructure()) {
            auto& substructure = node.getSubstructure();
            if (substructure.size() != node.getBins().size() - 1) {
                throw std::runtime_error(
                    "Number of bins ("+std::to_string(node.getBins().size()-1)+") "
                    "does not match number of substructure nodes "
                    "("+std::to_string(node.getBins().size()-1)+")!");
            }
            for (auto& subnode : substructure) {
                idxOffset = FlexGrid::_indexBins(subnode, idxOffset);
            }
        }
        else {
            std::vector<int> tmpVec(node.getBins().size() - 1);
            std::iota(tmpVec.begin(), tmpVec.end(), idxOffset + 1);
            node.setGlobalBinIndices(tmpVec);
            idxOffset += node.getBins().size() - 1;
        }
        return idxOffset;
    }

    /** Given a `FlexNode`, bin `values` successively and identify index of global bin */
    static int _findIndex(const FlexNode& node, std::vector<double>::const_iterator val, const std::vector<double>::const_iterator& values_end) {

        const auto& bins = node.getBins();  // convenience

        auto nextIter = std::upper_bound(bins.begin(), bins.end(), (*val));
        if ((nextIter == bins.begin()) || (nextIter == bins.end())) {
            return -1;
        }
        else {
            const int nextIdx = std::distance(bins.begin(), nextIter) - 1;
            // need successor to check if value iterator matches bin structure
            auto nextVal = std::next(val);

            if (node.hasSubstructure()) {
                if (nextVal == values_end) {
                    throw std::runtime_error("Insufficient number of values");
                }
                return FlexGrid::_findIndex(node.getSubnode(nextIdx), nextVal, values_end);
            }
            else {
                if (nextVal != values_end) {
                    throw std::runtime_error("Number of values exceeds number of defined binning levels");
                }
                return node.getGlobalBinIndex(nextIdx);
            }
        }
    }

  public:
    /** Find global index of bin which corresponds to sequence of `values` */
    int findIndex(const std::vector<double>& values) const {
        return FlexGrid::_findIndex(_rootFlexNode, values.begin(), values.end());
    }

    FlexNode _rootFlexNode;
};


namespace dijet {
    class FlexGridBinProvider {
      public:

        explicit FlexGridBinProvider(const std::string& yamlFile) : 
            _flexGrid(new FlexGrid(yamlFile)) {};
        ~FlexGridBinProvider() {};

        int getFlexGridBin(const std::vector<double>& values) {
            return _flexGrid->findIndex(values);
        };

      private:

        std::unique_ptr<FlexGrid> _flexGrid;

    };
}
