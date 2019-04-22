#include "Karma/Common/interface/TriggerEfficienciesProvider.h"

#include "TKey.h"


karma::TriggerEfficienciesProvider::TriggerEfficienciesProvider(std::string fileName) {

    TFile file(fileName.c_str());
    TIter next(file.GetListOfKeys());
    TKey *key;

    // go through all the objects in the ROOT file
    while ((key=(TKey*)next())) {
        TObject* effObj;
        file.GetObject(key->GetName(), effObj);
        TEfficiency* eff = dynamic_cast<TEfficiency*>(effObj);
        // dynamic cast successful if object is of type TEfficiency
        if (eff) {
            // clone object and store in map
            triggerEfficiencies_[key->GetName()] = std::unique_ptr<TEfficiency>(static_cast<TEfficiency*>(eff->Clone()));
        }
    }

    file.Close();
}


const TEfficiency* karma::TriggerEfficienciesProvider::getEfficiency(const std::string& key) {
    const auto mapIter = triggerEfficiencies_.find(key);
    if (mapIter == triggerEfficiencies_.end())
        return nullptr;
    return &(*mapIter->second);
}
