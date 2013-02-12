// -*- C++ -*-
// vim: sw=3:smarttab
//
// Package:    Plotters
// Class:      RecHitPlotter
// 
/**\class RecHitPlotter RecHitPlotter.cc Debug/Plotters/src/RecHitPlotter.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Matthias Wolf
//         Created:  Wed Jan 25 12:12:59 EST 2012
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

#include "DataFormats/Common/interface/SortedCollection.h"
#include "DataFormats/EcalDetId/interface/EBDetId.h"
#include "DataFormats/EcalDetId/interface/EEDetId.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHit.h"
#include "DataFormats/HcalDetId/interface/HcalDetId.h"
#include "DataFormats/HcalRecHit/interface/HBHERecHit.h"
#include "DataFormats/HcalRecHit/interface/HFRecHit.h"
#include "DataFormats/VertexReco/interface/Vertex.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH1D.h"
#include "TH2D.h"
#include "TProfile.h"

//
// class declaration
//

class RecHitPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit RecHitPlotter(const edm::ParameterSet&);
      ~RecHitPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      TH2D* ecal_dist_en_;
      TH2D* ecal_dist_mp_;
      TH2D* hcal_dist_en_;
      TH2D* hcal_dist_mp_;

      TH1D* ecal_en_;
      TH1D* ecal_en_tot_;
      TH1D* ecal_hits_;

      TH1D* ecal_en_b_;
      TH1D* ecal_en_e_;
      TH1D* ecal_en_tot_e_;
      TH1D* ecal_en_tot_b_;
      TH1D* ecal_hits_b_;
      TH1D* ecal_hits_e_;

      TH1D* hcal_en_;
      TH1D* hcal_en_tot_;
      TH1D* hcal_hits_;

      TH1D* hcal_en_b_;
      TH1D* hcal_en_e_;
      TH1D* hcal_en_e1_;
      TH1D* hcal_en_e2_;
      TH1D* hcal_en_f_;
      TH1D* hcal_en_tot_b_;
      TH1D* hcal_en_tot_e_;
      TH1D* hcal_en_tot_e1_;
      TH1D* hcal_en_tot_e2_;
      TH1D* hcal_en_tot_f_;
      TH1D* hcal_hits_b_;
      TH1D* hcal_hits_e_;
      TH1D* hcal_hits_e1_;
      TH1D* hcal_hits_e2_;
      TH1D* hcal_hits_f_;

      TProfile* ecal_et_tot_vtx_b_;
      TProfile* ecal_et_tot_vtx_e_;
      TProfile* hcal_et_tot_vtx_b_;
      TProfile* hcal_et_tot_vtx_e_;

      double cut_;

      edm::InputTag vertices_;
      std::vector<edm::InputTag> ecalHits_;
      std::vector<edm::InputTag> hcalHits_;
};

RecHitPlotter::RecHitPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   cut_(config.getUntrackedParameter<double>("cut", -.1)),
   vertices_(config.getParameter<edm::InputTag>("vertices")),
   ecalHits_(config.getParameter< std::vector<edm::InputTag> >("ecalHits")),
   hcalHits_(config.getParameter< std::vector<edm::InputTag> >("hcalHits"))
{
   int en_bins = 600;
   int en_tot_bins = 5000;
   int hits_bins = 600;
   double en_max = 1200.;
   double en_tot_max = 5000.;
   double hits_max = 1200.;

   edm::Service<TFileService> fs;
   ecal_dist_en_ = fs->make<TH2D>("ecal_dist_en",
         "Energy of ECAL;#eta;#phi;E [GeV]",
         57, -85.5, 85.5, 60, 0.5, 360.5); 
   ecal_dist_mp_ = fs->make<TH2D>("ecal_dist_mp",
         "Mutliplicity of ECAL;#eta;#phi;Multiplicity",
         57, -85.5, 85.5, 60, 0.5, 360.5); 
   hcal_dist_en_ = fs->make<TH2D>("hcal_dist_en",
         "Energy of HCAL;#eta;#phi;E [GeV]",
         59, -29.5, 29.5, 36, 0.5, 72.5);
   hcal_dist_mp_ = fs->make<TH2D>("hcal_dist_mp",
         "Multiplicity of HCAL;#eta;#phi;Multiplicity",
         59, -29.5, 29.5, 36, 0.5, 72.5);

   ecal_en_ = fs->make<TH1D>("ecal_en", "Energy in ECAL;E [GeV];Num",
         en_bins, 0., en_max);
   ecal_en_tot_ = fs->make<TH1D>("ecal_en_tot", "Total energy in ECAL;E [GeV];Num",
         en_tot_bins, 0., en_tot_max);
   ecal_hits_ = fs->make<TH1D>("ecal_hits", "Hits per event in the ECAL;n_{hits};Num",
         hits_bins, 0, hits_max);

   ecal_en_b_ = fs->make<TH1D>("ecal_en_b",
         "Energy in the ECAL barrel;E [GeV];Num",
         en_bins, 0., en_max);
   ecal_en_e_ = fs->make<TH1D>("ecal_en_e",
         "Energy in the ECAL endcap;E [GeV];Num",
         en_bins, 0., en_max);
   ecal_en_tot_b_ = fs->make<TH1D>("ecal_en_tot_b",
         "Total energy in the ECAL barrel;#sum E [GeV];Num",
         en_tot_bins, 0., en_tot_max);
   ecal_en_tot_e_ = fs->make<TH1D>("ecal_en_tot_e",
         "Total energy in the ECAL endcap;#sum E [GeV];Num",
         en_tot_bins, 0., en_tot_max);
   ecal_hits_b_ = fs->make<TH1D>("ecal_hits_b",
         "Hits in the ECAL barrel;n_{hits};Num",
         hits_bins, 0, hits_max);
   ecal_hits_e_ = fs->make<TH1D>("ecal_hits_e",
         "Hits in the ECAL endcap;n_{hits};Num",
         hits_bins, 0, hits_max);

   hcal_en_ = fs->make<TH1D>("hcal_en", "Energy in HCAL;E [GeV];Num",
         en_bins, 0., en_max);
   hcal_en_tot_ = fs->make<TH1D>("hcal_en_tot", "Total energy in HCAL;E [GeV];Num",
         en_tot_bins, 0., en_tot_max);
   hcal_hits_ = fs->make<TH1D>("hcal_hits", "Hits per event in the HCAL;n_{hits};Num",
         hits_bins, 0, hits_max);

   hcal_en_b_ = fs->make<TH1D>("hcal_en_b",
         "Energy in the HCAL barrel;E [GeV];Num",
         en_bins, 0., en_max);
   hcal_en_e_ = fs->make<TH1D>("hcal_en_e",
         "Energy in the HCAL endcap;E [GeV];Num",
         en_bins, 0., en_max);
   hcal_en_e1_ = fs->make<TH1D>("hcal_en_e1",
         "Energy in the HCAL endcap (|#eta| < 2.5);E [GeV];Num",
         en_bins, 0., en_max);
   hcal_en_e2_ = fs->make<TH1D>("hcal_en_e2",
         "Energy in the HCAL endcap (|#eta| > 2.5, ieta >= 27);E [GeV];Num",
         en_bins, 0., en_max);
   hcal_en_f_ = fs->make<TH1D>("hcal_en_f",
         "Energy in the HCAL forward;E [GeV];Num",
         en_bins, 0., en_max);
   hcal_en_tot_b_ = fs->make<TH1D>("hcal_en_tot_b",
         "Total energy in the HCAL barrel;#sum E [GeV];Num",
         en_tot_bins, 0., en_tot_max);
   hcal_en_tot_e_ = fs->make<TH1D>("hcal_en_tot_e",
         "Total energy in the HCAL endcap;#sum E [GeV];Num",
         en_tot_bins, 0., en_tot_max);
   hcal_en_tot_e1_ = fs->make<TH1D>("hcal_en_tot_e1",
         "Total energy in the HCAL endcap (|#eta| < 2.5);#sum E [GeV];Num",
         en_tot_bins, 0., en_tot_max);
   hcal_en_tot_e2_ = fs->make<TH1D>("hcal_en_tot_e2",
         "Total energy in the HCAL endcap (|#eta| > 2.5, ieta >= 27);#sum E [GeV];Num",
         en_tot_bins, 0., en_tot_max);
   hcal_en_tot_f_ = fs->make<TH1D>("hcal_en_tot_f",
         "Total energy in the HCAL forward;#sum E [GeV];Num",
         en_tot_bins, 0., en_tot_max);
   hcal_hits_b_ = fs->make<TH1D>("hcal_hits_b",
         "Hits in the HCAL barrel;n_{hits};Num",
         hits_bins, 0, hits_max);
   hcal_hits_e_ = fs->make<TH1D>("hcal_hits_e",
         "Hits in the HCAL endcap;n_{hits};Num",
         hits_bins, 0, hits_max);
   hcal_hits_e1_ = fs->make<TH1D>("hcal_hits_e1",
         "Hits in the HCAL endcap (|#eta| < 2.5);n_{hits};Num",
         hits_bins, 0, hits_max);
   hcal_hits_e2_ = fs->make<TH1D>("hcal_hits_e2",
         "Hits in the HCAL endcap (|#eta| > 2.5, ieta >= 27);n_{hits};Num",
         hits_bins, 0, hits_max);
   hcal_hits_f_ = fs->make<TH1D>("hcal_hits_f",
         "Hits in the HCAL forward;n_{hits};Num",
         hits_bins, 0, hits_max);

   ecal_et_tot_vtx_b_ = fs->make<TProfile>("ecal_et_tot_vtx_b",
         "EB <#sum E_{T}> vs. #PV;n_{vertices};#sum E_{T}", 101, -0.5, 100.5);
   ecal_et_tot_vtx_e_ = fs->make<TProfile>("ecal_et_tot_vtx_e",
         "EE <#sum E_{T}> vs. #PV;n_{vertices};#sum E_{T}", 101, -0.5, 100.5);
   hcal_et_tot_vtx_b_ = fs->make<TProfile>("hcal_et_tot_vtx_b",
         "HB <#sum E_{T}> vs. #PV;n_{vertices};#sum E_{T}", 101, -0.5, 100.5);
   hcal_et_tot_vtx_e_ = fs->make<TProfile>("hcal_et_tot_vtx_e",
         "HE <#sum E_{T}> vs. #PV;n_{vertices};#sum E_{T}", 101, -0.5, 100.5);
}

RecHitPlotter::~RecHitPlotter() {}

void
RecHitPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   double weight = this->weight(event);

   edm::Handle< std::vector<reco::Vertex> > vertices;
   if (!event.getByLabel(vertices_, vertices)){
      edm::LogError("RecHitPlotter") << "No valid vertices!" << std::endl;
      return;
   }
   int nvtx = 0;
   for (const auto& v: *(vertices.product())) {
      if (v.ndof() < 5 || fabs(v.z()) > 50 || fabs(v.position().rho()) > 2.)
         continue;
      nvtx++;
   }

   int nvtx_bin = (nvtx - 1) / 5;

   double ecal_e_tot_b = -1.;
   double ecal_e_tot_e = -1.;

   int ecal_hits_b = 0;
   int ecal_hits_e = 0;

   edm::Handle< edm::SortedCollection<EcalRecHit> > eb_hits;
   if (!event.getByLabel(ecalHits_[0], eb_hits)) {
      edm::LogError("RecHitPlotter") <<
         "Can't find rec hit collection with tag '" << ecalHits_[0] << "'" << std::endl;
   } else {
      ecal_e_tot_b = 0.;
      ecal_hits_b = eb_hits->size();

      edm::SortedCollection<EcalRecHit>::const_iterator hit;
      for (hit = eb_hits->begin(); hit != eb_hits->end(); ++hit) {
         EBDetId id = static_cast<EBDetId>(hit->id());

         if (hit->energy() < cut_)
            continue;

         ecal_e_tot_b += hit->energy();
         ecal_en_->Fill(hit->energy(), weight);
         ecal_en_b_->Fill(hit->energy(), weight);
         ecal_dist_en_->Fill(id.ieta(), id.iphi(), hit->energy() * weight);
         ecal_dist_mp_->Fill(id.ieta(), id.iphi(), weight);
      }
      ecal_en_tot_b_->Fill(ecal_e_tot_b, weight);
      ecal_hits_b_->Fill(ecal_hits_b, weight);

      ecal_et_tot_vtx_b_->Fill(nvtx, ecal_e_tot_b, weight); 
   }

   edm::Handle< edm::SortedCollection<EcalRecHit> > ee_hits;
   if (!event.getByLabel(ecalHits_[1], ee_hits)) {
      edm::LogError("RecHitPlotter") <<
         "Can't find rec hit collection with tag '" << ecalHits_[1] << "'" << std::endl;
   } else {
      ecal_e_tot_e = 0.;
      ecal_hits_e = ee_hits->size();

      edm::SortedCollection<EcalRecHit>::const_iterator hit;
      for (hit = ee_hits->begin(); hit != ee_hits->end(); ++hit) {
         if (hit->energy() < cut_)
            continue;

         ecal_e_tot_e += hit->energy();
         ecal_en_->Fill(hit->energy(), weight);
         ecal_en_e_->Fill(hit->energy(), weight);
      }
      ecal_en_tot_e_->Fill(ecal_e_tot_e, weight);
      ecal_hits_e_->Fill(ecal_hits_e, weight);

      ecal_et_tot_vtx_e_->Fill(nvtx, ecal_e_tot_e, weight); 
   }

   ecal_en_tot_->Fill(ecal_e_tot_b + ecal_e_tot_e, weight);
   ecal_hits_->Fill(ecal_hits_b + ecal_hits_e, weight);

   double hcal_e_tot_b = -1.;
   double hcal_e_tot_e1 = -1.;
   double hcal_e_tot_e2 = -1.;
   double hcal_e_tot_f = -1.;

   int hcal_hits_b = 0;
   int hcal_hits_e1 = 0;
   int hcal_hits_e2 = 0;
   int hcal_hits_f = 0;

   edm::Handle< edm::SortedCollection<HBHERecHit> > hbhe_hits;
   if (!event.getByLabel(hcalHits_[0], hbhe_hits)) {
      edm::LogError("RecHitPlotter") <<
         "Can't find rec hit collection with tag '" << hcalHits_[0] << "'" << std::endl;
   } else {
      hcal_e_tot_b = 0.;
      hcal_e_tot_e1 = 0.;
      hcal_e_tot_e2 = 0.;

      edm::SortedCollection<HBHERecHit>::const_iterator hit;
      for (hit = hbhe_hits->begin(); hit != hbhe_hits->end(); ++hit) {
         HcalDetId id = static_cast<HcalDetId>(hit->id());

         if (hit->energy() < cut_)
            continue;

         hcal_en_->Fill(hit->energy(), weight);
         hcal_dist_en_->Fill(id.ieta(), id.iphi(), hit->energy() * weight);
         hcal_dist_mp_->Fill(id.ieta(), id.iphi(), weight);

         if (id.subdet() == HcalBarrel) {
            ++hcal_hits_b;
            hcal_en_b_->Fill(hit->energy(), weight);
            hcal_e_tot_b += hit->energy();
         } else if (id.subdet() == HcalEndcap) {
            hcal_en_e_->Fill(hit->energy(), weight);
            // This checks the outer endcap
            if (id.ietaAbs() < 27) {
               ++hcal_hits_e1;
               hcal_en_e1_->Fill(hit->energy(), weight);
               hcal_e_tot_e1 += hit->energy();
            } else {
               ++hcal_hits_e2;
               hcal_en_e2_->Fill(hit->energy(), weight);
               hcal_e_tot_e2 += hit->energy();
            }
         }
      }

      hcal_en_tot_->Fill(hcal_e_tot_b + hcal_e_tot_e1 + hcal_e_tot_e2, weight);
      hcal_en_tot_b_->Fill(hcal_e_tot_b, weight);
      hcal_en_tot_e_->Fill(hcal_e_tot_e1 + hcal_e_tot_e2, weight);
      hcal_en_tot_e1_->Fill(hcal_e_tot_e1, weight);
      hcal_en_tot_e2_->Fill(hcal_e_tot_e2, weight);

      hcal_hits_->Fill(hcal_hits_b + hcal_hits_e1 + hcal_hits_e2, weight);
      hcal_hits_b_->Fill(hcal_hits_b, weight);
      hcal_hits_e_->Fill(hcal_hits_e1 + hcal_hits_e2, weight);
      hcal_hits_e1_->Fill(hcal_hits_e1, weight);
      hcal_hits_e2_->Fill(hcal_hits_e2, weight);

      hcal_et_tot_vtx_b_->Fill(nvtx, hcal_e_tot_b, weight); 
      hcal_et_tot_vtx_e_->Fill(nvtx, hcal_e_tot_e1 + hcal_e_tot_e2, weight); 
   }

   edm::Handle< edm::SortedCollection<HFRecHit> > hf_hits;
   if (!event.getByLabel(hcalHits_[1], hf_hits)) {
      edm::LogError("RecHitPlotter") <<
         "Can't find rec hit collection with tag '" << hcalHits_[1] << "'" << std::endl;
   } else {
      hcal_e_tot_f = 0.;

      edm::SortedCollection<HFRecHit>::const_iterator hit;
      for (hit = hf_hits->begin(); hit != hf_hits->end(); ++hit) {
         if (hit->energy() < cut_)
            continue;

         ++hcal_hits_f;
         hcal_en_f_->Fill(hit->energy(), weight);
         hcal_e_tot_f += hit->energy();
      }

      hcal_en_tot_f_->Fill(hcal_e_tot_f, weight);
      hcal_hits_f_->Fill(hcal_hits_f, weight);
   }
}

void
RecHitPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
   //The following says we do not know what parameters are allowed so do no validation
   // Please change this to state exactly what you do use, even if it is no parameters
   edm::ParameterSetDescription desc;
   desc.setUnknown();
   descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(RecHitPlotter);
