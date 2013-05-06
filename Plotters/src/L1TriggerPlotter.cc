// -*- C++ -*-
//
// Package:    L1TriggerPlotter
// Class:      L1TriggerPlotter
// 
/**\class L1TriggerPlotter L1TriggerPlotter.cc DataMixerValidation/L1TriggerPlotter/src/L1TriggerPlotter.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Matthias Wolf,512 1-009,+41227676491,
//         Created:  Thu Jul 26 21:15:56 CEST 2012
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/ESHandle.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "CondFormats/DataRecord/interface/L1GtTriggerMenuRcd.h"
#include "CondFormats/L1TObjects/interface/L1GtTriggerMenu.h"

#include "DataFormats/L1GlobalTrigger/interface/L1GlobalTriggerReadoutSetupFwd.h"
#include "DataFormats/L1GlobalTrigger/interface/L1GlobalTriggerReadoutRecord.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH1D.h"
#include "TString.h"
//
// class declaration
//

class L1TriggerPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit L1TriggerPlotter(const edm::ParameterSet&);
      ~L1TriggerPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      edm::InputTag gt_;

      bool labelled_;

      TH1D *trig_bits_;
};

L1TriggerPlotter::L1TriggerPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   gt_(config.getParameter<edm::InputTag>("l1Bits")),
   labelled_(false)
{
   edm::Service<TFileService> fs;
   trig_bits_ = fs->make<TH1D>("trig_bits", "Trigger Bits;Bit;Num", 128, -.5, 127.5);
}


L1TriggerPlotter::~L1TriggerPlotter() {}

void
L1TriggerPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   double weight = this->weight(event);

   edm::Handle<L1GlobalTriggerReadoutRecord> bits;
   if (!event.getByLabel(gt_, bits)) {
      edm::LogError("L1TriggerPlotter") << "Could not find trigger information under '"
         << gt_ << "'!" << std::endl;
   } else {
      if (!labelled_) {
         labelled_ = true;
         edm::ESHandle<L1GtTriggerMenu> l1menu;
         setup.get<L1GtTriggerMenuRcd>().get(l1menu);
         for (const auto& p: l1menu->gtAlgorithmMap())
            trig_bits_->GetXaxis()->SetBinLabel(p.second.algoBitNumber() + 1, p.first.c_str());
      }

      for (int i = 0; i < 128; ++i)
         trig_bits_->Fill(i, bits->decisionWord()[i] * weight);
   }
}

void
L1TriggerPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(L1TriggerPlotter);
