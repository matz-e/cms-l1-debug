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

#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "CondFormats/DataRecord/interface/EcalChannelStatusRcd.h"
#include "CondFormats/DataRecord/interface/HcalChannelQualityRcd.h"
#include "CondFormats/EcalObjects/interface/EcalChannelStatus.h"
#include "CondFormats/HcalObjects/interface/HcalChannelQuality.h"

#include "DataFormats/Common/interface/SortedCollection.h"
#include "DataFormats/EcalDetId/interface/EBDetId.h"
#include "DataFormats/EcalDetId/interface/EEDetId.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHit.h"
#include "DataFormats/HcalDetId/interface/HcalDetId.h"
#include "DataFormats/HcalRecHit/interface/HBHERecHit.h"
#include "DataFormats/HcalRecHit/interface/HFRecHit.h"
#include "DataFormats/VertexReco/interface/Vertex.h"

#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/EcalAlgo/interface/EcalBarrelGeometry.h"
#include "Geometry/EcalAlgo/interface/EcalEndcapGeometry.h"
#include "Geometry/HcalTowerAlgo/interface/HcalGeometry.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"

#include "RecoLocalCalo/HcalRecAlgos/interface/HcalSeverityLevelComputer.h"
#include "RecoLocalCalo/HcalRecAlgos/interface/HcalSeverityLevelComputerRcd.h"

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

      TH1D* ecal_en_per_vtx_b_[20];
      TH1D* ecal_en_per_vtx_e_[20];
      TH1D* hcal_en_per_vtx_b_[20];
      TH1D* hcal_en_per_vtx_e_[20];
      TH1D* hcal_en_per_vtx_f_[20];

      TH1D* ecal_en_tot_per_vtx_b_[20];
      TH1D* ecal_en_tot_per_vtx_e_[20];
      TH1D* hcal_en_tot_per_vtx_b_[20];
      TH1D* hcal_en_tot_per_vtx_e_[20];
      TH1D* hcal_en_tot_per_vtx_f_[20];

      TH1D* hcal_time_b_[10];
      TH1D* hcal_time_e_[10];
      TH1D* hcal_time_f_[10];
      static const double hcal_time_bounds_[11];

      TH1D* hcal_time_vtx_low_b_[5];
      TH1D* hcal_time_vtx_high_b_[5];
      TH1D* hcal_time_vtx_low_e_[5];
      TH1D* hcal_time_vtx_high_e_[5];
      TH1D* hcal_time_vtx_low_f_[5];
      TH1D* hcal_time_vtx_high_f_[5];
      static const int hcal_time_vtx_bounds_[6];

      TProfile* ecal_en_tot_vtx_b_;
      TProfile* ecal_en_tot_vtx_e_;
      TProfile* hcal_en_tot_vtx_b_;
      TProfile* hcal_en_tot_vtx_e_;

      double cut_;
      bool transverse_;

      edm::InputTag vertices_;
      std::vector<edm::InputTag> ecalHits_;
      std::vector<edm::InputTag> hcalHits_;
};

const double RecHitPlotter::hcal_time_bounds_[11] =
   {-1., .5, 1., 2., 5., 10., 25., 50., 100., 200., std::numeric_limits<double>::infinity()};
const int RecHitPlotter::hcal_time_vtx_bounds_[6] = 
   {-1, 10, 20, 30, 40, std::numeric_limits<int>::max()};

RecHitPlotter::RecHitPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   cut_(config.getUntrackedParameter<double>("cut", -.1)),
   transverse_(config.getUntrackedParameter<bool>("transverse", false)),
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

   for (int i = 0; i < 20; ++i) {
      ecal_en_per_vtx_b_[i] = fs->make<TH1D>(
            TString::Format("ecal_en_per_vtx_b_%02d", i),
            TString::Format("EB E with %d < nvtx < %d;E;Num", i * 5, i * 5 + 6),
            en_bins, 0., en_max);
      ecal_en_per_vtx_e_[i] = fs->make<TH1D>(
            TString::Format("ecal_en_per_vtx_e_%02d", i),
            TString::Format("EE E with %d < nvtx < %d;E;Num", i * 5, i * 5 + 6),
            en_bins, 0., en_max);
      hcal_en_per_vtx_b_[i] = fs->make<TH1D>(
            TString::Format("hcal_en_per_vtx_b_%02d", i),
            TString::Format("HB E with %d < nvtx < %d;E;Num", i * 5, i * 5 + 6),
            en_bins, 0., en_max);
      hcal_en_per_vtx_e_[i] = fs->make<TH1D>(
            TString::Format("hcal_en_per_vtx_e_%02d", i),
            TString::Format("HE E with %d < nvtx < %d;E;Num", i * 5, i * 5 + 6),
            en_bins, 0., en_max);
      hcal_en_per_vtx_f_[i] = fs->make<TH1D>(
            TString::Format("hcal_en_per_vtx_f_%02d", i),
            TString::Format("HF E with %d < nvtx < %d;E;Num", i * 5, i * 5 + 6),
            en_bins, 0., en_max);
      ecal_en_tot_per_vtx_b_[i] = fs->make<TH1D>(
            TString::Format("ecal_en_tot_per_vtx_b_%02d", i),
            TString::Format("EB #sum E with %d < nvtx < %d;E;Num", i * 5, i * 5 + 6),
            en_tot_bins, 0., en_tot_max);
      ecal_en_tot_per_vtx_e_[i] = fs->make<TH1D>(
            TString::Format("ecal_en_tot_per_vtx_e_%02d", i),
            TString::Format("EE #sum E with %d < nvtx < %d;E;Num", i * 5, i * 5 + 6),
            en_tot_bins, 0., en_tot_max);
      hcal_en_tot_per_vtx_b_[i] = fs->make<TH1D>(
            TString::Format("hcal_en_tot_per_vtx_b_%02d", i),
            TString::Format("HB #sum E with %d < nvtx < %d;E;Num", i * 5, i * 5 + 6),
            en_tot_bins, 0., en_tot_max);
      hcal_en_tot_per_vtx_e_[i] = fs->make<TH1D>(
            TString::Format("hcal_en_tot_per_vtx_e_%02d", i),
            TString::Format("HE #sum E with %d < nvtx < %d;E;Num", i * 5, i * 5 + 6),
            en_tot_bins, 0., en_tot_max);
      hcal_en_tot_per_vtx_f_[i] = fs->make<TH1D>(
            TString::Format("hcal_en_tot_per_vtx_f_%02d", i),
            TString::Format("HF #sum E with %d < nvtx < %d;E;Num", i * 5, i * 5 + 6),
            en_tot_bins, 0., en_tot_max);
   }

   for (int i = 0; i < 10; ++i) {
      hcal_time_b_[i] = fs->make<TH1D>(
            TString::Format("hcal_time_b_%d", i),
            TString::Format("HB timing for RecHits w/ %.1f < E < %.1f GeV;time (ns);Num",
               hcal_time_bounds_[i], hcal_time_bounds_[i + 1]),
            149, -149, 149);
      hcal_time_e_[i] = fs->make<TH1D>(
            TString::Format("hcal_time_e_%d", i),
            TString::Format("HE timing for RecHits w/ %.1f < E < %.1f GeV;time (ns);Num",
               hcal_time_bounds_[i], hcal_time_bounds_[i + 1]),
            149, -149, 149);
      hcal_time_f_[i] = fs->make<TH1D>(
            TString::Format("hcal_time_f_%d", i),
            TString::Format("HF timing for RecHits w/ %.1f < E < %.1f GeV;time (ns);Num",
               hcal_time_bounds_[i], hcal_time_bounds_[i + 1]),
            149, -149, 149);
   }

   for (int i = 0; i < 5; ++i) {
      hcal_time_vtx_low_b_[i] = fs->make<TH1D>(
            TString::Format("hcal_time_vtx_low_b_%d", i),
            TString::Format("HB timing for RecHits w/ E < .5 GeV, "
               "%d < PV < %d;time (ns);Num",
               hcal_time_vtx_bounds_[i], hcal_time_vtx_bounds_[i + 1]),
            149, -149, 149);
      hcal_time_vtx_high_b_[i] = fs->make<TH1D>(
            TString::Format("hcal_time_vtx_high_b_%d", i),
            TString::Format("HB timing for RecHits w/ 2 < E < 5 GeV, "
               "%d < PV < %d;time (ns);Num",
               hcal_time_vtx_bounds_[i], hcal_time_vtx_bounds_[i + 1]),
            149, -149, 149);
      hcal_time_vtx_low_e_[i] = fs->make<TH1D>(
            TString::Format("hcal_time_vtx_low_e_%d", i),
            TString::Format("HE timing for RecHits w/ E < .5 GeV, "
               "%d < PV < %d;time (ns);Num",
               hcal_time_vtx_bounds_[i], hcal_time_vtx_bounds_[i + 1]),
            149, -149, 149);
      hcal_time_vtx_high_e_[i] = fs->make<TH1D>(
            TString::Format("hcal_time_vtx_high_e_%d", i),
            TString::Format("HE timing for RecHits w/ 2 < E < 5 GeV, "
               "%d < PV < %d;time (ns);Num",
               hcal_time_vtx_bounds_[i], hcal_time_vtx_bounds_[i + 1]),
            149, -149, 149);
      hcal_time_vtx_low_f_[i] = fs->make<TH1D>(
            TString::Format("hcal_time_vtx_low_f_%d", i),
            TString::Format("HF timing for RecHits w/ E < .5 GeV, "
               "%d < PV < %d;time (ns);Num",
               hcal_time_vtx_bounds_[i], hcal_time_vtx_bounds_[i + 1]),
            149, -149, 149);
      hcal_time_vtx_high_f_[i] = fs->make<TH1D>(
            TString::Format("hcal_time_vtx_high_f_%d", i),
            TString::Format("HF timing for RecHits w/ 2 < E < 5 GeV, "
               "%d < PV < %d;time (ns);Num",
               hcal_time_vtx_bounds_[i], hcal_time_vtx_bounds_[i + 1]),
            149, -149, 149);
   }

   ecal_en_tot_vtx_b_ = fs->make<TProfile>("ecal_en_tot_vtx_b",
         "EB <#sum E> vs. #PV;n_{vertices};#sum E", 101, -0.5, 100.5);
   ecal_en_tot_vtx_e_ = fs->make<TProfile>("ecal_en_tot_vtx_e",
         "EE <#sum E> vs. #PV;n_{vertices};#sum E", 101, -0.5, 100.5);
   hcal_en_tot_vtx_b_ = fs->make<TProfile>("hcal_en_tot_vtx_b",
         "HB <#sum E> vs. #PV;n_{vertices};#sum E", 101, -0.5, 100.5);
   hcal_en_tot_vtx_e_ = fs->make<TProfile>("hcal_en_tot_vtx_e",
         "HE <#sum E> vs. #PV;n_{vertices};#sum E", 101, -0.5, 100.5);
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
      if (v.ndof() < 5 || fabs(v.z()) > 24. || fabs(v.position().rho()) > 2.)
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
      edm::ESHandle<CaloGeometry> gen_geo;
      setup.get<CaloGeometryRecord>().get(gen_geo);
      const CaloSubdetectorGeometry *geo = 
         gen_geo->getSubdetectorGeometry(DetId::Ecal, EcalBarrel);

      edm::ESHandle<EcalChannelStatus> status;
      setup.get<EcalChannelStatusRcd>().get(status);

      ecal_e_tot_b = 0.;
      ecal_hits_b = eb_hits->size();

      edm::SortedCollection<EcalRecHit>::const_iterator hit;
      for (hit = eb_hits->begin(); hit != eb_hits->end(); ++hit) {
         EBDetId id = static_cast<EBDetId>(hit->id());
         double en = hit->energy();

         if (hit->checkFlag(EcalRecHit::kWeird || hit->checkFlag(EcalRecHit::kDiWeird)))
            continue;

         auto channel_status = status.product()->find(id);
         if (channel_status == status.product()->end() ||
               (channel_status->getStatusCode() & 0x1F) != 0)
            continue;

         if (transverse_)
            en /= cosh(geo->getGeometry(id)->getPosition().eta());

         if (en < cut_)
            continue;

         ecal_e_tot_b += en;
         ecal_en_->Fill(en, weight);
         ecal_en_b_->Fill(en, weight);
         ecal_dist_en_->Fill(id.ieta(), id.iphi(), en * weight);
         ecal_dist_mp_->Fill(id.ieta(), id.iphi(), weight);

         if (0 <= nvtx_bin && nvtx_bin < 20)
            ecal_en_per_vtx_b_[nvtx_bin]->Fill(en, weight);
      }
      ecal_en_tot_b_->Fill(ecal_e_tot_b, weight);
      ecal_hits_b_->Fill(ecal_hits_b, weight);
      ecal_en_tot_vtx_b_->Fill(nvtx, ecal_e_tot_b, weight); 

      if (0 <= nvtx_bin && nvtx_bin < 20)
         ecal_en_tot_per_vtx_b_[nvtx_bin]->Fill(ecal_e_tot_b, weight);
   }

   edm::Handle< edm::SortedCollection<EcalRecHit> > ee_hits;
   if (!event.getByLabel(ecalHits_[1], ee_hits)) {
      edm::LogError("RecHitPlotter") <<
         "Can't find rec hit collection with tag '" << ecalHits_[1] << "'" << std::endl;
   } else {
      edm::ESHandle<CaloGeometry> gen_geo;
      setup.get<CaloGeometryRecord>().get(gen_geo);
      const CaloSubdetectorGeometry *geo = 
         gen_geo->getSubdetectorGeometry(DetId::Ecal, EcalEndcap);

      edm::ESHandle<EcalChannelStatus> status;
      setup.get<EcalChannelStatusRcd>().get(status);

      ecal_e_tot_e = 0.;
      ecal_hits_e = ee_hits->size();

      edm::SortedCollection<EcalRecHit>::const_iterator hit;
      for (hit = ee_hits->begin(); hit != ee_hits->end(); ++hit) {
         EEDetId id = static_cast<EEDetId>(hit->id());
         double en = hit->energy();

         if (hit->checkFlag(EcalRecHit::kWeird || hit->checkFlag(EcalRecHit::kDiWeird)))
            continue;

         auto channel_status = status.product()->find(id);
         if (channel_status == status.product()->end() ||
               (channel_status->getStatusCode() & 0x1F) != 0)
            continue;

         if (transverse_)
            en /= cosh(geo->getGeometry(id)->getPosition().eta());

         if (en < cut_)
            continue;

         ecal_e_tot_e += en;
         ecal_en_->Fill(en, weight);
         ecal_en_e_->Fill(en, weight);

         if (0 <= nvtx_bin && nvtx_bin < 20)
            ecal_en_per_vtx_e_[nvtx_bin]->Fill(en, weight);
      }
      ecal_en_tot_e_->Fill(ecal_e_tot_e, weight);
      ecal_hits_e_->Fill(ecal_hits_e, weight);
      ecal_en_tot_vtx_e_->Fill(nvtx, ecal_e_tot_e, weight); 

      if (0 <= nvtx_bin && nvtx_bin < 20)
         ecal_en_tot_per_vtx_e_[nvtx_bin]->Fill(ecal_e_tot_e, weight);
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
      edm::ESHandle<CaloGeometry> gen_geo;
      setup.get<CaloGeometryRecord>().get(gen_geo);
      const CaloSubdetectorGeometry *geo_barrel =
         gen_geo->getSubdetectorGeometry(DetId::Hcal, HcalBarrel);
      const CaloSubdetectorGeometry *geo_endcap =
         gen_geo->getSubdetectorGeometry(DetId::Hcal, HcalEndcap);

      edm::ESHandle<HcalChannelQuality> h_status;
      setup.get<HcalChannelQualityRcd>().get(h_status);
      const HcalChannelQuality *status = h_status.product();

      edm::ESHandle<HcalSeverityLevelComputer> h_comp;
      setup.get<HcalSeverityLevelComputerRcd>().get(h_comp);
      const HcalSeverityLevelComputer *comp = h_comp.product();

      hcal_e_tot_b = 0.;
      hcal_e_tot_e1 = 0.;
      hcal_e_tot_e2 = 0.;

      edm::SortedCollection<HBHERecHit>::const_iterator hit;
      for (hit = hbhe_hits->begin(); hit != hbhe_hits->end(); ++hit) {
         HcalDetId id = static_cast<HcalDetId>(hit->id());
         double en = hit->energy();

         if (comp->getSeverityLevel(id,
                  hit->flags(),
                  status->getValues(id)->getValue()) > 10)
            continue;

         if (transverse_) {
            if (id.subdet() == HcalBarrel)
               en /= cosh(geo_barrel->getGeometry(id)->getPosition().eta());
            else
               en /= cosh(geo_endcap->getGeometry(id)->getPosition().eta());
         }

         if (en < cut_)
            continue;

         hcal_en_->Fill(en, weight);
         hcal_dist_en_->Fill(id.ieta(), id.iphi(), en * weight);
         hcal_dist_mp_->Fill(id.ieta(), id.iphi(), weight);

         if (id.subdet() == HcalBarrel) {
            ++hcal_hits_b;
            hcal_en_b_->Fill(en, weight);
            hcal_e_tot_b += en;

            if (0 <= nvtx_bin && nvtx_bin < 20)
               hcal_en_per_vtx_b_[nvtx_bin]->Fill(en, weight);

            for (int i = 0; i < 10; ++i)
               if (hcal_time_bounds_[i] <= en and en < hcal_time_bounds_[i + 1])
                  hcal_time_b_[i]->Fill(hit->time(), weight);

            for (int i = 0; i < 5; ++i) {
               if (hcal_time_vtx_bounds_[i] <= nvtx and
                     nvtx < hcal_time_vtx_bounds_[i + 1]) {
                  if (en < .5)
                     hcal_time_vtx_low_b_[i]->Fill(hit->time(), weight);
                  else if (2. <= en and en < 5.)
                     hcal_time_vtx_high_b_[i]->Fill(hit->time(), weight);
               }
            }
         } else if (id.subdet() == HcalEndcap) {
            hcal_en_e_->Fill(en, weight);

            if (0 <= nvtx_bin && nvtx_bin < 20)
               hcal_en_per_vtx_e_[nvtx_bin]->Fill(en, weight);

            for (int i = 0; i < 10; ++i)
               if (hcal_time_bounds_[i] <= en and en < hcal_time_bounds_[i + 1])
                  hcal_time_e_[i]->Fill(hit->time(), weight);

            for (int i = 0; i < 5; ++i) {
               if (hcal_time_vtx_bounds_[i] <= nvtx and
                     nvtx < hcal_time_vtx_bounds_[i + 1]) {
                  if (en < .5)
                     hcal_time_vtx_low_e_[i]->Fill(hit->time(), weight);
                  else if (2. <= en and en < 5.)
                     hcal_time_vtx_high_e_[i]->Fill(hit->time(), weight);
               }
            }

            // This checks the outer endcap
            if (id.ietaAbs() < 27) {
               ++hcal_hits_e1;
               hcal_en_e1_->Fill(en, weight);
               hcal_e_tot_e1 += en;
            } else {
               ++hcal_hits_e2;
               hcal_en_e2_->Fill(en, weight);
               hcal_e_tot_e2 += en;
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

      hcal_en_tot_vtx_b_->Fill(nvtx, hcal_e_tot_b, weight); 
      hcal_en_tot_vtx_e_->Fill(nvtx, hcal_e_tot_e1 + hcal_e_tot_e2, weight); 

      if (0 <= nvtx_bin && nvtx_bin < 20) {
         hcal_en_tot_per_vtx_b_[nvtx_bin]->Fill(hcal_e_tot_b, weight);
         hcal_en_tot_per_vtx_e_[nvtx_bin]->Fill(hcal_e_tot_e1 + hcal_e_tot_e2, weight);
      }
   }

   edm::Handle< edm::SortedCollection<HFRecHit> > hf_hits;
   if (!event.getByLabel(hcalHits_[1], hf_hits)) {
      edm::LogError("RecHitPlotter") <<
         "Can't find rec hit collection with tag '" << hcalHits_[1] << "'" << std::endl;
   } else {
      edm::ESHandle<CaloGeometry> gen_geo;
      setup.get<CaloGeometryRecord>().get(gen_geo);
      const CaloSubdetectorGeometry *geo =
         gen_geo->getSubdetectorGeometry(DetId::Hcal, HcalForward);

      edm::ESHandle<HcalChannelQuality> h_status;
      setup.get<HcalChannelQualityRcd>().get(h_status);
      const HcalChannelQuality *status = h_status.product();

      edm::ESHandle<HcalSeverityLevelComputer> h_comp;
      setup.get<HcalSeverityLevelComputerRcd>().get(h_comp);
      const HcalSeverityLevelComputer *comp = h_comp.product();

      hcal_e_tot_f = 0.;

      edm::SortedCollection<HFRecHit>::const_iterator hit;
      for (hit = hf_hits->begin(); hit != hf_hits->end(); ++hit) {
         HcalDetId id = static_cast<HcalDetId>(hit->id());
         double en = hit->energy();

         if (comp->getSeverityLevel(id,
                  hit->flags(),
                  status->getValues(id)->getValue()) > 10)
            continue;

         if (transverse_)
            en /= cosh(geo->getGeometry(id)->getPosition().eta());

         if (en < cut_)
            continue;

         ++hcal_hits_f;
         hcal_en_f_->Fill(en, weight);
         hcal_e_tot_f += en;

         if (0 <= nvtx_bin && nvtx_bin < 20)
            hcal_en_per_vtx_f_[nvtx_bin]->Fill(en, weight);

         for (int i = 0; i < 10; ++i)
            if (hcal_time_bounds_[i] <= en and en < hcal_time_bounds_[i + 1])
               hcal_time_f_[i]->Fill(hit->time(), weight);

            for (int i = 0; i < 5; ++i) {
               if (hcal_time_vtx_bounds_[i] <= nvtx and
                     nvtx < hcal_time_vtx_bounds_[i + 1]) {
                  if (en < .5)
                     hcal_time_vtx_low_f_[i]->Fill(hit->time(), weight);
                  else if (2. <= en and en < 5.)
                     hcal_time_vtx_high_f_[i]->Fill(hit->time(), weight);
               }
            }
      }

      hcal_en_tot_f_->Fill(hcal_e_tot_f, weight);
      hcal_hits_f_->Fill(hcal_hits_f, weight);

      if (0 <= nvtx_bin && nvtx_bin < 20)
         hcal_en_tot_per_vtx_f_[nvtx_bin]->Fill(hcal_e_tot_f, weight);
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
