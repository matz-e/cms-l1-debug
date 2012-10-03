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

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH1D.h"
#include "TH2D.h"
//
// class declaration
//

class TriggerPrimitiveDigiPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit TriggerPrimitiveDigiPlotter(const edm::ParameterSet&);
      ~TriggerPrimitiveDigiPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      edm::InputTag ecal_digis_;
      edm::InputTag hcal_digis_;

      TH2D *h_ecal_adc_;
      TH2D *h_ecal_mp_;
      TH2D *h_hcal_adc_;
      TH2D *h_hcal_mp_;

      TH1D *ecal_digi_soi_;
      TH1D *ecal_digi_0_;
      TH1D *ecal_digi_1_;
      TH1D *ecal_digi_2_;
      TH1D *ecal_digi_3_;
      TH1D *ecal_digi_4_;

      TH1D *hcal_digi_soi_;
      TH1D *hcal_digi_0_;
      TH1D *hcal_digi_1_;
      TH1D *hcal_digi_2_;
      TH1D *hcal_digi_3_;
      TH1D *hcal_digi_4_;
};

TriggerPrimitiveDigiPlotter::TriggerPrimitiveDigiPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   ecal_digis_(config.getParameter<edm::InputTag>("ecalDigis")),
   hcal_digis_(config.getParameter<edm::InputTag>("hcalDigis"))
{
   edm::Service<TFileService> fs;
   h_ecal_adc_ = fs->make<TH2D>("ecal_soi_adc",
         "ECAL trigger primitive SOI;#eta;#phi;ADC count",
         57, -28.5, 28.5, 72, 0.5, 72.5);
   h_ecal_mp_  = fs->make<TH2D>("ecal_soi_mp", 
         "ECAL trigger primitive SOI;#eta;#phi;Multiplicity", 
         57, -28.5, 28.5, 72, 0.5, 72.5);
   h_hcal_adc_ = fs->make<TH2D>("hcal_soi_adc",
         "HCAL trigger primitive SOI;#eta;#phi;ADC count", 
         65, -32.5, 32.5, 72, 0.5, 72.5);
   h_hcal_mp_  = fs->make<TH2D>("hcal_soi_mp",
         "HCAL trigger primitive SOI;#eta;#phi;Multiplicity",
         65, -32.5, 32.5, 72, 0.5, 72.5);

   ecal_digi_soi_ = fs->make<TH1D>("ecal_digi_soi",
         "ECAL trigger primitive digi SOI;ADC count", 250, 0, 250);
   ecal_digi_0_ = fs->make<TH1D>("ecal_digi_0",
         "ECAL trigger primitive digi 0;ADC count", 250, 0, 250);
   ecal_digi_1_ = fs->make<TH1D>("ecal_digi_1",
         "ECAL trigger primitive digi 1;ADC count", 250, 0, 250);
   ecal_digi_2_ = fs->make<TH1D>("ecal_digi_2",
         "ECAL trigger primitive digi 2;ADC count", 250, 0, 250);
   ecal_digi_3_ = fs->make<TH1D>("ecal_digi_3",
         "ECAL trigger primitive digi 3;ADC count", 250, 0, 250);
   ecal_digi_4_ = fs->make<TH1D>("ecal_digi_4",
         "ECAL trigger primitive digi 4;ADC count", 250, 0, 250);

   hcal_digi_soi_ = fs->make<TH1D>("hcal_digi_soi",
         "HCAL trigger primitive digi SOI;ADC count", 250, 0, 250);
   hcal_digi_0_ = fs->make<TH1D>("hcal_digi_0",
         "HCAL trigger primitive digi 0;ADC count", 250, 0, 250);
   hcal_digi_1_ = fs->make<TH1D>("hcal_digi_1",
         "HCAL trigger primitive digi 1;ADC count", 250, 0, 250);
   hcal_digi_2_ = fs->make<TH1D>("hcal_digi_2",
         "HCAL trigger primitive digi 2;ADC count", 250, 0, 250);
   hcal_digi_3_ = fs->make<TH1D>("hcal_digi_3",
         "HCAL trigger primitive digi 3;ADC count", 250, 0, 250);
   hcal_digi_4_ = fs->make<TH1D>("hcal_digi_4",
         "HCAL trigger primitive digi 4;ADC count", 250, 0, 250);
}

TriggerPrimitiveDigiPlotter::~TriggerPrimitiveDigiPlotter() {}

void
TriggerPrimitiveDigiPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   double weight = this->weight(event);

   Handle<EcalTrigPrimDigiCollection> ecal_handle_;
   if (!event.getByLabel(ecal_digis_, ecal_handle_)) {
      LogError("TriggerPrimitiveDigiPlotter") <<
         "Can't find ecal trigger primitive digi collection with tag '" <<
         ecal_digis_ << "'" << std::endl;
   } else {
      for (EcalTrigPrimDigiCollection::const_iterator p = ecal_handle_->begin();
            p != ecal_handle_->end(); ++p) {
         ecal_digi_soi_->Fill(p->compressedEt(), weight);
         ecal_digi_0_->Fill(p->sample(0).compressedEt(), weight);
         ecal_digi_1_->Fill(p->sample(1).compressedEt(), weight);
         ecal_digi_2_->Fill(p->sample(2).compressedEt(), weight);
         ecal_digi_3_->Fill(p->sample(3).compressedEt(), weight);
         ecal_digi_4_->Fill(p->sample(4).compressedEt(), weight);

         EcalTrigTowerDetId id = p->id();
         h_ecal_adc_->Fill(id.ieta(), id.iphi(), p->compressedEt());
         h_ecal_mp_->Fill(id.ieta(), id.iphi());
      }
   }

   Handle< SortedCollection<HcalTriggerPrimitiveDigi> > hcal_handle_;
   if (!event.getByLabel(hcal_digis_, hcal_handle_)) {
      LogError("TriggerPrimitiveDigiPlotter") <<
         "Can't find hcal trigger primitive digi collection with tag '" <<
         hcal_digis_ << "'" << std::endl;
   } else {
      SortedCollection<HcalTriggerPrimitiveDigi>::const_iterator p;
      for (p = hcal_handle_->begin(); p != hcal_handle_->end();
            ++p) {
         hcal_digi_soi_->Fill(p->SOI_compressedEt(), weight);
         hcal_digi_0_->Fill(p->sample(0).compressedEt(), weight);
         hcal_digi_1_->Fill(p->sample(1).compressedEt(), weight);
         hcal_digi_2_->Fill(p->sample(2).compressedEt(), weight);
         hcal_digi_3_->Fill(p->sample(3).compressedEt(), weight);
         hcal_digi_4_->Fill(p->sample(4).compressedEt(), weight);

         HcalTrigTowerDetId id = p->id();
         h_ecal_adc_->Fill(id.ieta(), id.iphi(), p->SOI_compressedEt());
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
