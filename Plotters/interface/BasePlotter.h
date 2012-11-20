#include <map>
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "PhysicsTools/Utilities/interface/LumiReWeighting.h"

class BasePlotter {
   protected:
      BasePlotter(const edm::ParameterSet&);
      ~BasePlotter();
      double weight(const edm::Event&) const;
   private:
      bool weigh_;

      static int count_;
      static bool init_;
      static bool standard_;
      static std::map<int, float> weights_;
      static edm::LumiReWeighting *helper_;
};
