#include "DataFormats/FWLite/interface/EventBase.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "TFile.h"
#include "TTree.h"

#include "Debug/Plotters/interface/BasePlotter.h"

int BasePlotter::count_ = 0;
bool BasePlotter::init_ = false;
bool BasePlotter::standard_ = false;
std::map<int, float> BasePlotter::weights_;
edm::LumiReWeighting *BasePlotter::helper_ = 0;

BasePlotter::BasePlotter(const edm::ParameterSet& config)
{
   weigh_ = config.getUntrackedParameter<bool>("weigh", false);
   standard_ = standard_ || config.getUntrackedParameter<bool>("useStandardMethod", true);

   if (weigh_ && !init_ && standard_) {
      std::string fn = config.getUntrackedParameter<std::string>(
            "weightFile", "weights.root");
      helper_ = new edm::LumiReWeighting(fn, fn, "mc", "data");
   } else if (weigh_ && !init_) {
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
               edm::LogInfo("BasePlotter") << "Commencing weight reading..." << std::endl;
               for (unsigned int i = 0; i < t->GetEntries(); ++i) {
                  t->GetEntry(i);
                  weights_[id] = w;
               }
               edm::LogInfo("BasePlotter") << "Finishing weight reading." << std::endl;
            } // Branch check
         } // Tree check
      } // File check
   } // weigh_ check
   if (standard_)
      ++count_;
}

BasePlotter::~BasePlotter() {
   if (standard_ && --count_ == 0)
      delete helper_;
}

double BasePlotter::weight(const edm::Event& e) const {
   if (!weigh_)
      return 1.;

   if (standard_) {
      const edm::EventBase *base = dynamic_cast<const edm::EventBase*>(&e);
      return helper_->weight(*base);
   }

   std::map<int, float>::const_iterator i = weights_.find(e.id().event());
   if (i == weights_.end()) {
      edm::LogError("BasePlotter") << "No weight found for event id "
         << e.id().event() << std::endl;
      return 1.;
   } else {
      return i->second;
   }
}
