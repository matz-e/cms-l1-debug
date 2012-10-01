#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "TFile.h"
#include "TTree.h"

#include "Debug/Plotters/interface/BasePlotter.h"

BasePlotter::BasePlotter(const edm::ParameterSet& config) :
   weigh_(config.getUntrackedParameter<bool>("weigh", false))
{
   if (weigh_) {
      std::string fn = config.getUntrackedParameter<std::string>(
            "weightFile", "weights.root");
      TFile f(fn.c_str());

      if (!f.IsOpen()) {
         edm::LogError("BasePlotter") << "Can't open file '" << fn
            << "' for reading!" << std::endl;
      } else {
         TTree *t;
         f.GetObject("weights/event_weights", t);

         if (!t) {
            edm::LogError("BasePlotter") << "Can't find weight tree in file '" << fn
               << "'" << std::endl;
         } else {
            unsigned int id;
            float w;

            if (t->SetBranchAddress("id", &id) || t->SetBranchAddress("w", &w)) {
               edm::LogError("BasePlotter") << "Can't set branches up correctly!"
                  << std::endl;
            } else {
               for (unsigned int i = 0; i < t->GetEntries(); ++i) {
                  t->GetEntry(i);
                  weights_[id] = w;
               }
            } // Branch check
         } // Tree check
      } // File check
   } // weigh_ check
}

BasePlotter::~BasePlotter() {}

double BasePlotter::weight(const edm::Event& e) const {
   if (!weigh_)
      return 1.;

   std::map<int, float>::const_iterator i = weights_.find(e.id().event());
   if (i == weights_.end()) {
      edm::LogError("BasePlotter") << "No weight found for event id "
         << e.id().event() << std::endl;
      return 1.;
   } else {
      return i->second;
   }
}
