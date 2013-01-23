// -*- C++ -*-
//
// Package:    TriggerPrimitiveDigiCmpPlotter
// Class:      TriggerPrimitiveDigiCmpPlotter
// 
/**\class TriggerPrimitiveDigiCmpPlotter TriggerPrimitiveDigiCmpPlotter.cc Plotters/TriggerPrimitiveDigiCmpPlotter/src/TriggerDigiPrimitiveDigiCmpPlotter.cc

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

class TriggerPrimitiveDigiCmpPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit TriggerPrimitiveDigiCmpPlotter(const edm::ParameterSet&);
      ~TriggerPrimitiveDigiCmpPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      // TODO No ECAL stuff currently, which seems to be OK.
      edm::InputTag hcal_digis_;
      edm::InputTag hcal_reemul_digis_;

      TH2D *hcal_digi_diff_dist_avg_;
      TH2D *hcal_digi_diff_dist_rms_;
      TH2D *hcal_digi_diff_dist_mp_;

      TH1D *hcal_digi_diff_tot_;
      TH1D *hcal_digi_diff_hb_;
      TH1D *hcal_digi_diff_hbhe_;
      TH1D *hcal_digi_diff_he_;
      TH1D *hcal_digi_diff_hf_;

      TH2D *h_ecal_adc_;
      TH2D *h_ecal_mp_;
      TH2D *h_hcal_adc_;
      TH2D *h_hcal_mp_;

      TH1D *hcal_digi_soi_hb;
      TH1D *hcal_digi_soi_hbhe;
      TH1D *hcal_digi_soi_he;
      TH1D *hcal_digi_soi_hf;
      TH1D *hcal_digi_[5];

      TH1D *hcal_digi_mp_soi_tot;
      TH1D *hcal_digi_mp_soi_hb;
      TH1D *hcal_digi_mp_soi_hbhe;
      TH1D *hcal_digi_mp_soi_he;
      TH1D *hcal_digi_mp_soi_hf;
};

TriggerPrimitiveDigiCmpPlotter::TriggerPrimitiveDigiCmpPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   hcal_digis_(config.getParameter<edm::InputTag>("hcalDigis")),
   hcal_reemul_digis_(config.getParameter<edm::InputTag>("hcalReEmulDigis"))
{
   edm::Service<TFileService> fs;

   hcal_digi_diff_tot_ = fs->make<TH1D>("hcal_tp_digi_diff_tot",
         "HCAL trigger primitive SOI difference;"
         "#frac{E_{T} resim - E_{T} sim}{E_{T} resim};Num",
         400, -5, 5);

   hcal_digi_diff_dist_avg_ = fs->make<TH2D>("hcal_tp_digi_diff_dist_avg",
         "HCAL trigger primitive SOI difference;"
         "ieta;iphi;#sum #frac{E_{T} resim - E_{T} sim}{E_{T} resim}",
         65, -32.5, 32.5, 72, 0.5, 72.5);
   hcal_digi_diff_dist_rms_ = fs->make<TH2D>("hcal_tp_digi_diff_dist_rms",
         "HCAL trigger primitive SOI difference;"
         "ieta;iphi;#sum #left(#frac{E_{T} resim - E_{T} sim}{E_{T} resim}#right)^{2}",
         65, -32.5, 32.5, 72, 0.5, 72.5);
   hcal_digi_diff_dist_mp_ = fs->make<TH2D>("hcal_tp_digi_diff_dist_mp",
         "HCAL trigger primitive SOI difference;"
         "ieta;iphi;Num",
         65, -32.5, 32.5, 72, 0.5, 72.5);
}

TriggerPrimitiveDigiCmpPlotter::~TriggerPrimitiveDigiCmpPlotter() {}

void
TriggerPrimitiveDigiCmpPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   double weight = this->weight(event);

   Handle< SortedCollection<HcalTriggerPrimitiveDigi> > hcal_handle_;
   if (!event.getByLabel(hcal_digis_, hcal_handle_)) {
      LogError("TriggerPrimitiveDigiCmpPlotter") <<
         "Can't find hcal trigger primitive digi collection with tag '" <<
         hcal_digis_ << "'" << std::endl;
      return;
   }

   Handle< SortedCollection<HcalTriggerPrimitiveDigi> > hcal_reemul_handle_;
   if (!event.getByLabel(hcal_reemul_digis_, hcal_reemul_handle_)) {
      LogError("TriggerPrimitiveDigiCmpPlotter") <<
         "Can't find reemulated hcal trigger primitive digi collection with tag '" <<
         hcal_reemul_digis_ << "'" << std::endl;
      return;
   }

   // std::cout << "HCAL TP size: " << hcal_handle_->size() << std::endl;
   // std::cout << "HCAL reemulated TP size: " << hcal_reemul_handle_->size()
      // << std::endl;

   std::map<HcalTrigTowerDetId, int> adcs;
   for (const auto& p: *(hcal_handle_.product())) {
      HcalTrigTowerDetId id = p.id();
      if (adcs.find(id) == adcs.end()) {
         adcs[id] = p.SOI_compressedEt();
      } else {
         std::cout << "Duplicate: " << id << std::endl;
      }
   }

   std::set<HcalTrigTowerDetId> done;
   for (const auto& p: *(hcal_reemul_handle_.product())) {
      HcalTrigTowerDetId id = p.id();
      if (adcs.find(id) == adcs.end()) {
         // std::cout << "Unmatched: " << id << std::endl;
      } else if (done.find(id) != done.end()) {
         // std::cout << "Reemulated duplicate: " << id << std::endl;
      } else {
         done.insert(id);

         int ieta = id.ietaAbs();

         if (p.SOI_compressedEt() == adcs[id]) {
            continue;
         }

         // if (p.SOI_compressedEt() == 0) {
            // std::cout << "Division by zero @ " << id << std::endl;
            // continue;
         // }
         
         double diff = adcs[id] - double(p.SOI_compressedEt());
         double ratio = diff / p.SOI_compressedEt();

         // if (diff > 0 and id.iphi() == 13 and id.ieta() == -16) {
            // std::cout << "difference: " << diff << std::endl;
         // }

         hcal_digi_diff_dist_mp_->Fill(id.ieta(), id.iphi(), weight);
         hcal_digi_diff_dist_avg_->Fill(id.ieta(), id.iphi(), diff * weight);
         hcal_digi_diff_dist_rms_->Fill(id.ieta(), id.iphi(), diff * diff * weight);
         hcal_digi_diff_tot_->Fill(ratio, weight);
      }

      // if (ieta < 16) {
         // ++n_hb;
         // hcal_digi_soi_hb->Fill(p.SOI_compressedEt(), weight);
      // } else if (ieta < 17) {
         // ++n_hbhe;
         // hcal_digi_soi_hbhe->Fill(p.SOI_compressedEt(), weight);
      // } else if (ieta < 29) {
         // ++n_he;
         // hcal_digi_soi_he->Fill(p.SOI_compressedEt(), weight);
      // } else {
         // ++n_hf;
         // hcal_digi_soi_hf->Fill(p.SOI_compressedEt(), weight);
      // }

      // for (int i = 0; i < 5; ++i)
         // hcal_digi_[i]->Fill(p.sample(i).compressedEt(), weight);

      // h_hcal_adc_->Fill(id.ieta(), id.iphi(), p.SOI_compressedEt() * weight);
      // h_hcal_mp_->Fill(id.ieta(), id.iphi(), weight);
   }
}

void
TriggerPrimitiveDigiCmpPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(TriggerPrimitiveDigiCmpPlotter);
