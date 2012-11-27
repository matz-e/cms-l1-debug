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
#include "TString.h"
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

      TH1D *calo_et_b_;
      TH1D *calo_et_be_;
      TH1D *calo_et_e_;
      TH1D *calo_et_f_;
      TH1D *calo_et_tot_;
      TH1D *calo_et_tot_b_;
      TH1D *calo_et_tot_be_;
      TH1D *calo_et_tot_e_;
      TH1D *calo_et_tot_f_;

      // More fine-grained plots for the endcap
      TH1D *calo_et_e_1_;
      TH1D *calo_et_e_2_;
      TH1D *calo_et_e_3_;
      TH1D *calo_et_tot_e_1_;
      TH1D *calo_et_tot_e_2_;
      TH1D *calo_et_tot_e_3_;
};

CaloRegionPlotter::CaloRegionPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   regions_(config.getParameter<edm::InputTag>("caloRegions"))
{
   edm::Service<TFileService> fs;
   calo_et_b_ = fs->make<TH1D>("calo_et_b",
         "E_{T} of calo regions (barrel);E_{T} [GeV];Num",
         400, 0., 2000.);
   calo_et_e_ = fs->make<TH1D>("calo_et_e",
         "E_{T} of calo regions (endcap);E_{T} [GeV];Num",
         400, 0., 2000.);
   calo_et_f_ = fs->make<TH1D>("calo_et_f",
         "E_{T} of calo regions (forward);E_{T} [GeV];Num",
         400, 0., 2000.);

   calo_et_tot_ = fs->make<TH1D>("calo_et_tot",
         "#sum E_{T} of calo regions;#sum E_{T} [GeV];Num",
         500, 0., 5000.);
   calo_et_tot_b_ = fs->make<TH1D>("calo_et_tot_b",
         "#sum E_{T} of calo regions (barrel);#sum E_{T} [GeV];Num",
         500, 0., 5000.);
   calo_et_tot_be_ = fs->make<TH1D>("calo_et_tot_be",
         "#sum E_{T} of calo regions (barrel + endcap);#sum E_{T} [GeV];Num",
         500, 0., 5000.);
   calo_et_tot_e_ = fs->make<TH1D>("calo_et_tot_e",
         "#sum E_{T} of calo regions (endcap);#sum E_{T} [GeV];Num",
         500, 0., 5000.);
   calo_et_tot_f_ = fs->make<TH1D>("calo_et_tot_f",
         "#sum E_{T} of calo regions (forward);#sum E_{T} [GeV];Num",
         500, 0., 5000.);

   calo_et_e_1_ = fs->make<TH1D>("calo_et_e_1",
         "E_{T} of calo regions (ieta 6, 15);E_{T} [Gev];Num",
         500, 0., 1000.);
   calo_et_e_2_ = fs->make<TH1D>("calo_et_e_2",
         "E_{T} of calo regions (ieta 5, 16);E_{T} [Gev];Num",
         500, 0., 1000.);
   calo_et_e_3_ = fs->make<TH1D>("calo_et_e_3",
         "E_{T} of calo regions (ieta 4, 17);E_{T} [Gev];Num",
         500, 0., 1000.);
   calo_et_tot_e_1_ = fs->make<TH1D>("calo_et_tot_e_1",
         "#sum E_{T} of calo regions (ieta 6, 15);#sum E_{T} [Gev];Num",
         1000, 0., 5000.);
   calo_et_tot_e_2_ = fs->make<TH1D>("calo_et_tot_e_2",
         "#sum E_{T} of calo regions (ieta 5, 16);#sum E_{T} [Gev];Num",
         1000, 0., 5000.);
   calo_et_tot_e_3_ = fs->make<TH1D>("calo_et_tot_e_3",
         "#sum E_{T} of calo regions (ieta 4, 17);#sum E_{T} [Gev];Num",
         1000, 0., 5000.);

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
   double et_tot_b = 0.;
   double et_tot_be = 0.;
   double et_tot_e = 0.;
   double et_tot_f = 0.;

   double et_tot_e_1 = 0.;
   double et_tot_e_2 = 0.;
   double et_tot_e_3 = 0.;

   double weight = this->weight(event);

   Handle<L1CaloRegionCollection> regions;
   if (!event.getByLabel(regions_, regions)) {
      LogError("CaloRegionPlotter") <<
         "Can't find calo region collection with tag '" <<
         regions_ << "'" << std::endl;
   } else {
      for (L1CaloRegionCollection::const_iterator r = regions->begin();
            r != regions->end(); ++r) {
         int ieta = r->gctEta();

         et_tot += r->et();
         if (r->isHf()) {
            calo_et_f_->Fill(r->et(), weight);
            et_tot_f += r->et();
         } else if (ieta < 7 || ieta > 14) {
            calo_et_e_->Fill(r->et(), weight);
            et_tot_e += r->et();
            et_tot_be += r->et();

            if (ieta == 4 || ieta == 17) {
               calo_et_e_3_->Fill(r->et(), weight);
               et_tot_e_3 += r->et();
            } else if (ieta == 5 || ieta == 16) {
               calo_et_e_2_->Fill(r->et(), weight);
               et_tot_e_2 += r->et();
            } else {
               calo_et_e_1_->Fill(r->et(), weight);
               et_tot_e_1 += r->et();
            }
         } else {
            calo_et_b_->Fill(r->et(), weight);
            et_tot_b += r->et();
            et_tot_be += r->et();
         }

         h_calo_et_->Fill(r->gctEta(), r->gctPhi(), weight * r->et());
         h_calo_fg_->Fill(r->gctEta(), r->gctPhi(), weight * r->fineGrain());
         h_calo_mp_->Fill(r->gctEta(), r->gctPhi(), weight);
      }
   }

   calo_et_tot_->Fill(et_tot, weight);
   calo_et_tot_b_->Fill(et_tot_b, weight);
   calo_et_tot_be_->Fill(et_tot_be, weight);
   calo_et_tot_e_->Fill(et_tot_e, weight);
   calo_et_tot_f_->Fill(et_tot_f, weight);

   calo_et_tot_e_1_->Fill(et_tot_e_1, weight);
   calo_et_tot_e_2_->Fill(et_tot_e_2, weight);
   calo_et_tot_e_3_->Fill(et_tot_e_3, weight);
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
