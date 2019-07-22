#pragma once

#include <algorithm>
#include <vector>
#include <numeric>
#include <exception>

#include "yaml-cpp/yaml.h"

#include <boost/algorithm/string.hpp>  // for boost::split
#include <boost/algorithm/string/join.hpp>

template <typename TIterator>
static YAML::Node subkeyLookup(YAML::Node node, TIterator keySequenceIterStart, TIterator keySequenceIterEnd) {
  // when the final key is reached, return the node
  if (keySequenceIterStart == keySequenceIterEnd) {
      return node;
  }
  // otherwise repeat lookup in child node
  return subkeyLookup(node[*keySequenceIterStart], std::next(keySequenceIterStart), keySequenceIterEnd);
}

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
        // read in substructure
        if (node["substructure"]) {
            int i = 0;
            for (const auto& subnode : node["substructure"]) {
                substructure_.emplace_back(subnode);
                ++i;
            }
        }
        // read in optional metadata
        if (node["metadata"]) {
          metadata_ = node["metadata"];
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

    /** Get node metadata */
    YAML::Node& getMetadata() const { return metadata_; }

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
    mutable YAML::Node metadata_;
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

    /** Given a `FlexNode`, bin `values` successively and retrieve metadata for key 'key' */
    static YAML::Node _findBinMetadata(const FlexNode& node, const std::vector<std::string>& keySequence, std::vector<double>::const_iterator val, const std::vector<double>::const_iterator& values_end) {

        const auto& bins = node.getBins();  // convenience

        auto nextIter = std::upper_bound(bins.begin(), bins.end(), (*val));
        if ((nextIter == bins.begin()) || (nextIter == bins.end())) {
            throw std::out_of_range("Failed to retrieve bin metadata: bin values out of bounds!");
        }
        else {
            const int nextIdx = std::distance(bins.begin(), nextIter) - 1;
            // need successor to check if value iterator matches bin structure
            auto nextVal = std::next(val);

            if (node.hasSubstructure()) {
                if (nextVal == values_end) {
                    throw std::runtime_error("Insufficient number of values");
                }
                return FlexGrid::_findBinMetadata(node.getSubnode(nextIdx), keySequence, nextVal, values_end);
            }
            else {
                if (nextVal != values_end) {
                    throw std::runtime_error("Number of values exceeds number of defined binning levels");
                }
                // iteratively retrieve metadata nodes according to 'keySequence'
                YAML::Node binMetadataNode = subkeyLookup(node.getMetadata(), keySequence.begin(), keySequence.end());
                // check if node exists
                if (binMetadataNode.IsNull()) {
                    throw std::runtime_error("Failed to retrieve bin metadata: key '" + boost::algorithm::join(keySequence, ".") + "' not found");
                }
                // check if final value is a sequence
                if (!binMetadataNode.IsSequence()) {
                    throw std::runtime_error("Failed to retrieve bin metadata: key '" + boost::algorithm::join(keySequence, ".") + "' not a sequence");
                }
                // check if sequence length corresponds to number of bins
                if (binMetadataNode.size() != bins.size() - 1) {
                    throw std::runtime_error(
                      "Failed to retrieve bin metadata: size of metadata vector for key "
                      "'" + boost::algorithm::join(keySequence, ".") + "' does not match bin structure!");
                }
                return binMetadataNode[nextIdx];
            }
        }
    }

  public:
    /** Find global index of bin which corresponds to sequence of `values` */
    int findIndex(const std::vector<double>& values) const {
        return FlexGrid::_findIndex(_rootFlexNode, values.begin(), values.end());
    }

    /** Find metadata entry under key 'key' for bin which corresponds to sequence of `values` */
    YAML::Node findBinMetadata(const std::string& keySpec, const std::vector<double>& values) const {
        // split string `keySpec` on delimiter '.'
        std::vector<std::string> keySequence;
        boost::split(keySequence, keySpec, [](char c){return c == '.';});
        // pass key sequence to metadata finder
        return FlexGrid::_findBinMetadata(_rootFlexNode, keySequence, values.begin(), values.end());
    }

    FlexNode _rootFlexNode;
};


namespace karma {
    class FlexGridBinProvider {
      public:

        explicit FlexGridBinProvider(const FlexGrid& flexGrid) : _flexGrid(std::unique_ptr<FlexGrid>(new FlexGrid(flexGrid))) {};
        explicit FlexGridBinProvider(const std::string& yamlFile) :
            _flexGrid(new FlexGrid(yamlFile)) {};
        ~FlexGridBinProvider() {};

        FlexGrid& getFlexGrid() { return *_flexGrid; };

        int getFlexGridBin(const std::vector<double>& values) {
            return _flexGrid->findIndex(values);
        };

        YAML::Node getFlexGridBinMetadata(const std::string& keySpec, const std::vector<double>& values) {
            // retrieve global bin index for metadata lookup in cache
            const int globalBinIndex = _flexGrid->findIndex(values);
            // throw if values outside binning range
            if (globalBinIndex < 0) {
                throw std::out_of_range("Failed to retrieve bin metadata: bin values out of bounds!");
            }
            auto& cachedMetadataNode = _cacheMapKeySpecBinIndexToMetadataNode[keySpec][globalBinIndex];
            if (cachedMetadataNode.IsNull()) {
                cachedMetadataNode = _flexGrid->findBinMetadata(keySpec, values);
            }
            return cachedMetadataNode;
        };

      private:

        YAML::Node _getFlexGridBinMetadata(const std::string& keySpec, const std::vector<double>& values) {
            return _flexGrid->findBinMetadata(keySpec, values);
        };

        std::unique_ptr<FlexGrid> _flexGrid;
        // cache metadata by global index to increase lookup efficiency
        std::map<std::string,std::map<int, YAML::Node>> _cacheMapKeySpecBinIndexToMetadataNode;

    };
}
