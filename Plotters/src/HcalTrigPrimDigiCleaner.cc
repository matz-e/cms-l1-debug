// -*- C++ -*-
//
// Package:    HcalTrigPrimDigiCleaner
// Class:      HcalTrigPrimDigiCleaner
// 
/**\class HcalTrigPrimDigiCleaner HcalTrigPrimDigiCleaner.cc Debug/Plotters/src/HcalTrigPrimDigiCleaner.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  matthias wolf
//         Created:  Wed Jun 19 10:36:10 CDT 2013
// $Id$
//
//

#include <memory>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/ESHandle.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "CondFormats/L1TObjects/interface/L1RCTParameters.h"
#include "CondFormats/DataRecord/interface/L1RCTParametersRcd.h"
#include "CondFormats/L1TObjects/interface/L1CaloHcalScale.h"
#include "CondFormats/DataRecord/interface/L1CaloHcalScaleRcd.h"

#include "DataFormats/HcalDigi/interface/HcalDigiCollections.h"

class HcalTrigPrimDigiCleaner : public edm::EDProducer {
   public:
      explicit HcalTrigPrimDigiCleaner(const edm::ParameterSet&);
      ~HcalTrigPrimDigiCleaner();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void produce(edm::Event&, const edm::EventSetup&);

      bool first_;
      double threshold_;
      edm::InputTag dirtytpds_;
};

HcalTrigPrimDigiCleaner::HcalTrigPrimDigiCleaner(const edm::ParameterSet& config) :
   first_(true),
   threshold_(config.getUntrackedParameter<double>("threshold", -1000.)),
   dirtytpds_(config.getParameter<edm::InputTag>("input"))
{
   produces<HcalTrigPrimDigiCollection>();
}


HcalTrigPrimDigiCleaner::~HcalTrigPrimDigiCleaner()
{
}

void
HcalTrigPrimDigiCleaner::produce(edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   ESHandle<L1CaloHcalScale> hcal_scale;
   setup.get<L1CaloHcalScaleRcd>().get(hcal_scale);
   const L1CaloHcalScale* h = hcal_scale.product();

   edm::ESHandle<L1RCTParameters> rct;
   setup.get<L1RCTParametersRcd>().get(rct);
   const L1RCTParameters* r = rct.product();

   if (first_) {
      h->print(std::cout);
      r->print(std::cout);
      first_ = false;
   }

   Handle<HcalTrigPrimDigiCollection> digis;
   if (!event.getByLabel(dirtytpds_, digis)) {
      LogError("HcalTrigPrimDigiCleaner") <<
         "Can't find hcal trigger primitive digi collection with tag '" <<
         dirtytpds_ << "'" << std::endl;
      return;
   }

   std::auto_ptr<HcalTrigPrimDigiCollection> result(new HcalTrigPrimDigiCollection());

   for (const auto& digi: *digis) {
      HcalTrigTowerDetId id = digi.id();

      if (id.ietaAbs() >= 29) {
         result->push_back(digi);
         continue;
      }

      float hcal = h->et(digi.SOI_compressedEt(), id.ietaAbs(), id.zside());
      float ecal = 0.;
      float et = r->JetMETTPGSum(ecal, hcal, id.ietaAbs());

      // Trigger primitives and calo regions have energies measured in half
      // GeV.
      if (et * 0.5 >= threshold_)
         result->push_back(digi);
   }

   event.put(result);
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
HcalTrigPrimDigiCleaner::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(HcalTrigPrimDigiCleaner);
