// -*- C++ -*-
//
// Package:    CaloRegionPlotter
// Class:      CaloRegionPlotter
// 
/**\class CaloRegionPlotter CaloRegionPlotter.cc DataMixerValidation/CaloRegionPlotter/src/CaloRegionPlotter.cc

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
#include "TH2D.h"
//
// class declaration
//

class CaloRegionPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit CaloRegionPlotter(const edm::ParameterSet&);
      ~CaloRegionPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      edm::InputTag regions_;

      TH2D *h_calo_et_;
      TH2D *h_calo_fg_;
      TH2D *h_calo_mp_;

      TH1D *calo_et_;
      TH1D *calo_et_tot_;

      TH1D *calo_et_no_hf_;
      TH1D *calo_et_tot_no_hf_;
};

CaloRegionPlotter::CaloRegionPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   regions_(config.getParameter<edm::InputTag>("caloRegions"))
{
   edm::Service<TFileService> fs;
   calo_et_ = fs->make<TH1D>("calo_et", "E_{T} of calo regions; E_{T} [GeV]",
         400, 0., 2000.);
   calo_et_tot_ = fs->make<TH1D>("calo_et_tot",
         "#sum E_{T} of calo regions;#sum E_{T} [GeV]",
         200, 0., 2000.);
   calo_et_no_hf_ = fs->make<TH1D>("calo_et_no_hf", "E_{T} of calo regions; E_{T} [GeV]",
         400, 0., 2000.);
   calo_et_tot_no_hf_ = fs->make<TH1D>("calo_et_tot_no_hf",
         "#sum E_{T} of calo regions;#sum E_{T} [GeV]",
         200, 0., 2000.);
   h_calo_et_ = fs->make<TH2D>("calo_region_et",
         "E_{T} of calo regions;#eta;#phi;E_{T} [GeV]",
         22, -.5, 21.5, 18, -.5, 17.5);
   h_calo_fg_ = fs->make<TH2D>("calo_region_fg", 
         "Finegrain of calo regions;#eta;#phi;Finegrain [GeV]",
         22, -.5, 21.5, 18, -.5, 17.5);
   h_calo_mp_ = fs->make<TH2D>("calo_region_mp",
         "Multiplicity of calo regions;#eta;#phi;Multiplicity",
         22, -.5, 21.5, 18, -.5, 17.5);
}


CaloRegionPlotter::~CaloRegionPlotter() {}

void
CaloRegionPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   double et_tot = 0.;
   double et_tot_no_hf = 0.;
   double weight = this->weight(event);

   Handle<L1CaloRegionCollection> regions;
   if (!event.getByLabel(regions_, regions)) {
      LogError("CaloRegionPlotter") <<
         "Can't find calo region collection with tag '" <<
         regions_ << "'" << std::endl;
   } else {
      // std::cout << "CR: " << regions->size() << std::endl;
      for (L1CaloRegionCollection::const_iterator r = regions->begin();
            r != regions->end(); ++r) {
         et_tot += r->et();

         calo_et_->Fill(r->et(), weight);
         h_calo_et_->Fill(r->gctEta(), r->gctPhi(), weight * r->et());
         h_calo_fg_->Fill(r->gctEta(), r->gctPhi(), weight * r->fineGrain());
         h_calo_mp_->Fill(r->gctEta(), r->gctPhi(), weight);

         if (r->gctEta() > 3 && r->gctEta() < 18) {
            et_tot_no_hf += r->et();
            calo_et_no_hf_->Fill(r->et(), weight);
         }
      }
   }

   calo_et_tot_->Fill(et_tot, weight);
   calo_et_tot_no_hf_->Fill(et_tot_no_hf, weight);
}

void
CaloRegionPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(CaloRegionPlotter);
