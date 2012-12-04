// -*- C++ -*-
//
// Package:    CaloRegionCmpPlotter
// Class:      CaloRegionCmpPlotter
// 
/**\class CaloRegionCmpPlotter CaloRegionCmpPlotter.cc DataMixerValidation/CaloRegionCmpPlotter/src/CaloRegionCmpPlotter.cc

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

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/L1CaloTrigger/interface/L1CaloCollections.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH1D.h"
//
// class declaration
//

class CaloRegionCmpPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit CaloRegionCmpPlotter(const edm::ParameterSet&);
      ~CaloRegionCmpPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      edm::InputTag regions_;
      edm::InputTag reemul_regions_;

      TH1D *calo_diff_tot_;
      TH1D *calo_diff_barrel_;
      TH1D *calo_diff_endcap_;
      TH1D *calo_diff_endcap_c_;
      TH1D *calo_diff_endcap_m_;
      TH1D *calo_diff_endcap_f_;
      TH1D *calo_diff_forward_;
};

CaloRegionCmpPlotter::CaloRegionCmpPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   regions_(config.getParameter<edm::InputTag>("caloRegions")),
   reemul_regions_(config.getParameter<edm::InputTag>("reEmulCaloRegions"))
{
   edm::Service<TFileService> fs;
   calo_diff_tot_ = fs->make<TH1D>("calo_diff_tot",
         "Overall;#frac{E_{T} reemulated - E_{T} from raw}{E_{T} from raw};Num",
         400, -5., 5.);
   calo_diff_barrel_ = fs->make<TH1D>("calo_diff_barrel",
         "Barrel;#frac{E_{T} reemulated - E_{T} from raw}{E_{T} from raw};Num",
         400, -5., 5.);
   calo_diff_endcap_ = fs->make<TH1D>("calo_diff_endcap",
         "Endcap;#frac{E_{T} reemulated - E_{T} from raw}{E_{T} from raw};Num",
         400, -5., 5.);
   calo_diff_endcap_c_ = fs->make<TH1D>("calo_diff_endcap_c",
         "Endcap (ieta 6, 15);#frac{E_{T} reemulated - E_{T} from raw}{E_{T} from raw};Num",
         400, -5., 5.);
   calo_diff_endcap_m_ = fs->make<TH1D>("calo_diff_endcap_m",
         "Endcap (ieta 5, 16);#frac{E_{T} reemulated - E_{T} from raw}{E_{T} from raw};Num",
         400, -5., 5.);
   calo_diff_endcap_f_ = fs->make<TH1D>("calo_diff_endcap_f",
         "Endcap (ieta 4, 17);#frac{E_{T} reemulated - E_{T} from raw}{E_{T} from raw};Num",
         400, -5., 5.);
   calo_diff_forward_ = fs->make<TH1D>("calo_diff_forward",
         "Forward;#frac{E_{T} reemulated - E_{T} from raw}{E_{T} from raw};Num",
         400, -5., 5.);
}


CaloRegionCmpPlotter::~CaloRegionCmpPlotter() {}

void
CaloRegionCmpPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   // map[ieta][iphi] = calo_region_et
   std::map< int, std::map<int, double> > energies;

   double weight = this->weight(event);

   Handle<L1CaloRegionCollection> regions;
   if (!event.getByLabel(regions_, regions)) {
      LogError("CaloRegionCmpPlotter") <<
         "Can't find calo region collection with tag '" <<
         regions_ << "'" << std::endl;
      return;
   } 

   Handle<L1CaloRegionCollection> reemul_regions;
   if (!event.getByLabel(reemul_regions_, reemul_regions)) {
      LogError("CaloRegionCmpPlotter") <<
         "Can't find reemulated calo region collection with tag '" <<
         reemul_regions_ << "'" << std::endl;
      return;
   } 

   for (L1CaloRegionCollection::const_iterator r = regions->begin();
         r != regions->end(); ++r) {
      int ieta = r->gctEta();
      int iphi = r->gctPhi();

      energies[ieta][iphi] = r->et();
   }

   for (auto const& r: *(reemul_regions.product())) {
      int ieta = r.gctEta();
      int iphi = r.gctPhi();

      double ratio = (r.et() - energies[ieta][iphi]) / r.et();

      calo_diff_tot_->Fill(ratio, weight);

      if (r.isHf()) {
         calo_diff_forward_->Fill(ratio, weight);
      } else if (ieta < 7 || ieta > 14) {
         calo_diff_endcap_->Fill(ratio, weight);

         if (ieta == 6 || ieta == 15) {
            calo_diff_endcap_c_->Fill(ratio, weight);
         } else if (ieta == 5 || ieta == 16) {
            calo_diff_endcap_m_->Fill(ratio, weight);
         } else {
            calo_diff_endcap_f_->Fill(ratio, weight);
         }
      } else {
         calo_diff_barrel_->Fill(ratio, weight);
      }
   }
}

void
CaloRegionCmpPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(CaloRegionCmpPlotter);
