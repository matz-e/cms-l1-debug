#include <map>
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

class BasePlotter {
   protected:
      BasePlotter(const edm::ParameterSet&);
      ~BasePlotter();
      double weight(const edm::Event&) const;
   private:
      static bool init_;
      static bool weigh_;
      static std::map<int, float> weights_;
};
