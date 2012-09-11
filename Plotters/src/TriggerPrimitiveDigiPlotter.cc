// -*- C++ -*-
//
// Package:    TriggerPrimitiveDigiPlotter
// Class:      TriggerPrimitiveDigiPlotter
// 
/**\class TriggerPrimitiveDigiPlotter TriggerPrimitiveDigiPlotter.cc Plotters/TriggerPrimitiveDigiPlotter/src/TriggerDigiPrimitiveDigiPlotter.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  matthias wolf
//         Created:  Fri Aug 10 11:37:21 CDT 2012
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

#include "DataFormats/Common/interface/SortedCollection.h"
#include "DataFormats/EcalDigi/interface/EcalDigiCollections.h"
#include "DataFormats/EcalDigi/interface/EcalTriggerPrimitiveDigi.h"
#include "DataFormats/EcalDetId/interface/EcalTrigTowerDetId.h"
#include "DataFormats/HcalDigi/interface/HcalTriggerPrimitiveDigi.h"
#include "DataFormats/HcalDetId/interface/HcalTrigTowerDetId.h"

#include "TH2D.h"
#include "TNtuple.h"
//
// class declaration
//

class TriggerPrimitiveDigiPlotter : public edm::EDAnalyzer {
   public:
      explicit TriggerPrimitiveDigiPlotter(const edm::ParameterSet&);
      ~TriggerPrimitiveDigiPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      edm::InputTag ecal_digis_;
      edm::InputTag hcal_digis_;

      TNtuple *tpl_e_digis_;
      TNtuple *tpl_h_digis_;

      TH2D *h_ecal_adc_;
      TH2D *h_ecal_mp_;
      TH2D *h_hcal_adc_;
      TH2D *h_hcal_mp_;
};

TriggerPrimitiveDigiPlotter::TriggerPrimitiveDigiPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   ecal_digis_(config.getParameter<edm::InputTag>("ecalDigis")),
   hcal_digis_(config.getParameter<edm::InputTag>("hcalDigis"))
{
   edm::Service<TFileService> fs;
   tpl_e_digis_ = fs->make<TNtuple>("ecal_trigger_digis", "", "e_soi:e0:e1:e2:e3:e4");
   tpl_h_digis_ = fs->make<TNtuple>("hcal_trigger_digis", "", "h_soi:h0:h1:h2:h3:h4");

   h_ecal_adc_ = fs->make<TH2D>("ecal_soi_adc", "", 57, -28.5, 28.5, 72, 0.5, 72.5);
   h_ecal_mp_  = fs->make<TH2D>("ecal_soi_mp", "", 57, -28.5, 28.5, 72, 0.5, 72.5);
   h_hcal_adc_ = fs->make<TH2D>("hcal_soi_adc", "", 65, -32.5, 32.5, 72, 0.5, 72.5);
   h_hcal_mp_  = fs->make<TH2D>("hcal_soi_mp", "", 65, -32.5, 32.5, 72, 0.5, 72.5);
}

TriggerPrimitiveDigiPlotter::~TriggerPrimitiveDigiPlotter() {}

void
TriggerPrimitiveDigiPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   float digis[6];

   Handle<EcalTrigPrimDigiCollection> ecal_handle_;
   if (!event.getByLabel(ecal_digis_, ecal_handle_)) {
      LogError("TriggerPrimitiveDigiPlotter") <<
         "Can't find ecal trigger primitive digi collection with tag '" <<
         ecal_digis_ << "'" << std::endl;
   } else {
      for (EcalTrigPrimDigiCollection::const_iterator primitive = ecal_handle_->begin();
            primitive != ecal_handle_->end(); ++primitive) {
         digis[0] = primitive->compressedEt();
         for (int i = 0; i < primitive->size(); ++i)
            digis[i + 1] = primitive->sample(i).compressedEt();
         tpl_e_digis_->Fill(digis);

         EcalTrigTowerDetId id = primitive->id();
         h_ecal_adc_->Fill(id.ieta(), id.iphi(), primitive->compressedEt());
         h_ecal_mp_->Fill(id.ieta(), id.iphi());
      }
   }

   Handle< SortedCollection<HcalTriggerPrimitiveDigi> > hcal_handle_;
   if (!event.getByLabel(hcal_digis_, hcal_handle_)) {
      LogError("TriggerPrimitiveDigiPlotter") <<
         "Can't find hcal trigger primitive digi collection with tag '" <<
         hcal_digis_ << "'" << std::endl;
   } else {
      SortedCollection<HcalTriggerPrimitiveDigi>::const_iterator primitive;
      for (primitive = hcal_handle_->begin(); primitive != hcal_handle_->end();
            ++primitive) {
         digis[0] = primitive->SOI_compressedEt();
         for (int i = 0; i < primitive->size(); ++i)
            digis[i + 1] = primitive->sample(i).compressedEt();
         tpl_h_digis_->Fill(digis);

         HcalTrigTowerDetId id = primitive->id();
         h_ecal_adc_->Fill(id.ieta(), id.iphi(), primitive->SOI_compressedEt());
         h_ecal_mp_->Fill(id.ieta(), id.iphi());
      }
   }
}

void
TriggerPrimitiveDigiPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(TriggerPrimitiveDigiPlotter);
