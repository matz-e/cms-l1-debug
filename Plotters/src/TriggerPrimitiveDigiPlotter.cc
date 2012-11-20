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
#include "DataFormats/EcalDetId/interface/EcalSubdetector.h"
#include "DataFormats/EcalDetId/interface/EcalTrigTowerDetId.h"
#include "DataFormats/HcalDigi/interface/HcalTriggerPrimitiveDigi.h"
#include "DataFormats/HcalDetId/interface/HcalTrigTowerDetId.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH1D.h"
#include "TH2D.h"
#include "TString.h"
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

      TH1D *ecal_digi_soi_eb;
      TH1D *ecal_digi_soi_ebee;
      TH1D *ecal_digi_soi_ee;
      TH1D *ecal_digi_soi_ef;
      TH1D *ecal_digi_[5];

      TH1D *hcal_digi_soi_hb;
      TH1D *hcal_digi_soi_hbhe;
      TH1D *hcal_digi_soi_he;
      TH1D *hcal_digi_soi_hf;
      TH1D *hcal_digi_[5];
};

TriggerPrimitiveDigiPlotter::TriggerPrimitiveDigiPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   ecal_digis_(config.getParameter<edm::InputTag>("ecalDigis")),
   hcal_digis_(config.getParameter<edm::InputTag>("hcalDigis"))
{
   edm::Service<TFileService> fs;

   h_ecal_adc_ = fs->make<TH2D>("ecal_soi_adc_",
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

   ecal_digi_soi_eb = fs->make<TH1D>("ecal_digi_soi_eb",
         "ECAL trigger primitive digi SOI (barrel);ADC count", 250, 0, 250);
   ecal_digi_soi_ee = fs->make<TH1D>("ecal_digi_soi_ee",
         "ECAL trigger primitive digi SOI (endcap);ADC count", 250, 0, 250);

   for (int i = 0; i < 5; ++i)
      ecal_digi_[i] = fs->make<TH1D>(TString::Format("ecal_digi_%d", i),
            TString::Format("ECAL trigger primitive digi %d;ADC count", i),
            250, 0, 250);

   hcal_digi_soi_hb = fs->make<TH1D>("hcal_digi_soi_hb",
         "HCAL trigger primitive digi SOI (barrel);ADC count", 250, 0, 250);
   hcal_digi_soi_hbhe = fs->make<TH1D>("hcal_digi_soi_hbhe",
         "HCAL trigger primitive digi SOI (overlap);ADC count", 250, 0, 250);
   hcal_digi_soi_he = fs->make<TH1D>("hcal_digi_soi_he",
         "HCAL trigger primitive digi SOI (endcap);ADC count", 250, 0, 250);
   hcal_digi_soi_hf = fs->make<TH1D>("hcal_digi_soi_hf",
         "HCAL trigger primitive digi SOI (forward);ADC count", 250, 0, 250);

   for (int i = 0; i < 5; ++i)
      hcal_digi_[i] = fs->make<TH1D>(TString::Format("hcal_digi_%d", i),
            TString::Format("HCAL trigger primitive digi %d;ADC count", i),
            250, 0, 250);
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
         EcalTrigTowerDetId id = p->id();

         if (id.subDet() == EcalBarrel)
            ecal_digi_soi_eb->Fill(p->compressedEt(), weight);
         else if (id.subDet() == EcalEndcap)
            ecal_digi_soi_ee->Fill(p->compressedEt(), weight);

         for (int i = 0; i < 5; ++i)
            ecal_digi_[i]->Fill(p->sample(i).compressedEt(), weight);

         h_ecal_adc_->Fill(id.ieta(), id.iphi(), p->compressedEt() * weight);
         h_ecal_mp_->Fill(id.ieta(), id.iphi(), weight);
      }
   }

   Handle< SortedCollection<HcalTriggerPrimitiveDigi> > hcal_handle_;
   if (!event.getByLabel(hcal_digis_, hcal_handle_)) {
      LogError("TriggerPrimitiveDigiPlotter") <<
         "Can't find hcal trigger primitive digi collection with tag '" <<
         hcal_digis_ << "'" << std::endl;
   } else {
      SortedCollection<HcalTriggerPrimitiveDigi>::const_iterator p;
      for (p = hcal_handle_->begin(); p != hcal_handle_->end(); ++p) {
         HcalTrigTowerDetId id = p->id();
         int ieta = id.ietaAbs();

         if (ieta < 16)
            hcal_digi_soi_hb->Fill(p->SOI_compressedEt(), weight);
         else if (ieta < 17)
            hcal_digi_soi_hbhe->Fill(p->SOI_compressedEt(), weight);
         else if (ieta < 29)
            hcal_digi_soi_he->Fill(p->SOI_compressedEt(), weight);
         else
            hcal_digi_soi_hf->Fill(p->SOI_compressedEt(), weight);

         for (int i = 0; i < 5; ++i)
            hcal_digi_[i]->Fill(p->sample(i).compressedEt(), weight);

         h_hcal_adc_->Fill(id.ieta(), id.iphi(), p->SOI_compressedEt() * weight);
         h_hcal_mp_->Fill(id.ieta(), id.iphi(), weight);
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
