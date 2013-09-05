// -*- C++ -*-
//
// Package:    ChainCmpPlotter
// Class:      ChainCmpPlotter
// 
/**\class ChainCmpPlotter ChainCmpPlotter.cc Debug/Plotters/src/ChainCmpPlotter.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  matthias wolf
//         Created:  Fri Aug 26 11:37:21 CDT 2013
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

#include "CondFormats/DataRecord/interface/EcalChannelStatusRcd.h"
#include "CondFormats/DataRecord/interface/HcalChannelQualityRcd.h"
#include "CondFormats/DataRecord/interface/L1CaloGeometryRecord.h"
#include "CondFormats/EcalObjects/interface/EcalChannelStatus.h"
#include "CondFormats/HcalObjects/interface/HcalChannelQuality.h"
#include "CondFormats/L1TObjects/interface/L1CaloGeometry.h"

#include "CondFormats/L1TObjects/interface/L1RCTParameters.h"
#include "CondFormats/DataRecord/interface/L1RCTParametersRcd.h"
#include "CondFormats/L1TObjects/interface/L1CaloHcalScale.h"
#include "CondFormats/DataRecord/interface/L1CaloHcalScaleRcd.h"

#include "DataFormats/Common/interface/SortedCollection.h"
#include "DataFormats/CaloTowers/interface/CaloTower.h"
#include "DataFormats/EcalDigi/interface/EcalDigiCollections.h"
#include "DataFormats/EcalDigi/interface/EcalTriggerPrimitiveDigi.h"
#include "DataFormats/EcalDetId/interface/EcalSubdetector.h"
#include "DataFormats/EcalDetId/interface/EcalTrigTowerDetId.h"
#include "DataFormats/HcalDigi/interface/HcalDigiCollections.h"
#include "DataFormats/HcalDigi/interface/HcalTriggerPrimitiveDigi.h"
#include "DataFormats/HcalDetId/interface/HcalTrigTowerDetId.h"
#include "DataFormats/HcalDetId/interface/HcalDetId.h"
#include "DataFormats/HcalRecHit/interface/HBHERecHit.h"
#include "DataFormats/L1CaloTrigger/interface/L1CaloCollections.h"

#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/EcalAlgo/interface/EcalBarrelGeometry.h"
#include "Geometry/EcalAlgo/interface/EcalEndcapGeometry.h"
#include "Geometry/HcalTowerAlgo/interface/HcalGeometry.h"
#include "Geometry/HcalTowerAlgo/interface/HcalTrigTowerGeometry.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"

#include "RecoLocalCalo/HcalRecAlgos/interface/HcalSeverityLevelComputer.h"
#include "RecoLocalCalo/HcalRecAlgos/interface/HcalSeverityLevelComputerRcd.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH2D.h"
#include "TString.h"
//
// class declaration
//

class ChainCmpPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit ChainCmpPlotter(const edm::ParameterSet&);
      ~ChainCmpPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      edm::InputTag digis_;
      edm::InputTag regions_;
      edm::InputTag rechits_;
      edm::InputTag towers_;

      TH2D *regions_vs_rechits_b_;
      TH2D *regions_vs_towers_b_;
      TH2D *regions_vs_rechits_e_;
      TH2D *regions_vs_towers_e_;

      double cut_;
      bool debug_;
};

ChainCmpPlotter::ChainCmpPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   digis_(config.getParameter<edm::InputTag>("tpds")),
   regions_(config.getParameter<edm::InputTag>("regions")),
   rechits_(config.getParameter<edm::InputTag>("hits")),
   towers_(config.getParameter<edm::InputTag>("towers")),
   cut_(config.getUntrackedParameter<double>("cut", -.1)),
   debug_(config.getUntrackedParameter<bool>("debug", false))
{
   edm::Service<TFileService> fs;

   regions_vs_rechits_b_ = fs->make<TH2D>("regions_vs_rechits_b",
         "CaloRegions vs RecHits (barrel);Region E_{T};RecHit E_{T};Num", 750, 0, 750, 500, 0, 500);
   regions_vs_towers_b_ = fs->make<TH2D>("regions_vs_towers_b",
         "CaloRegions vs CaloTowers (barrel);Region E_{T};Tower E_{T};Num", 750, 0, 750, 500, 0, 500);
   regions_vs_rechits_e_ = fs->make<TH2D>("regions_vs_rechits_e",
         "CaloRegions vs RecHits (endcap);Region E_{T};RecHit E_{T};Num", 750, 0, 750, 500, 0, 500);
   regions_vs_towers_e_ = fs->make<TH2D>("regions_vs_towers_e",
         "CaloRegions vs CaloTowers (endcap);Region E_{T};Tower E_{T};Num", 750, 0, 750, 500, 0, 500);
}

ChainCmpPlotter::~ChainCmpPlotter() {}

void
ChainCmpPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   double weight = this->weight(event);

   double region_sum_b = 0.;
   double rechit_sum_b = 0.;
   double tower_sum_b = 0.;
   double region_sum_e = 0.;
   double rechit_sum_e = 0.;
   double tower_sum_e = 0.;

   double tp_energies[22][18];
   double l1_energies[22][18];
   double rh_energies[22][18];
   double ct_energies[22][18];

   for (int i = 0; i < 22; ++i) {
      for (int j = 0; j < 18; ++j) {
         tp_energies[i][j] = 0.;
         l1_energies[i][j] = 0.;
         rh_energies[i][j] = 0.;
         ct_energies[i][j] = 0.;
      }
   }

   edm::Handle<L1CaloRegionCollection> regions;
   if (!event.getByLabel(regions_, regions)) {
      LogError("CaloRegionPlotter") <<
         "Can't find calo region collection with tag '" <<
         regions_ << "'" << std::endl;
      return;
   }

   edm::ESHandle<L1CaloGeometry> l1_geo;
   setup.get<L1CaloGeometryRecord>().get(l1_geo);

   for (L1CaloRegionCollection::const_iterator r = regions->begin();
         r != regions->end(); ++r) {
      double et = r->et() * 0.5;

      int ieta = r->gctEta();
      l1_energies[ieta][r->gctPhi()] += et;

      if (et < cut_)
         continue;

      if ((ieta < 7 || ieta > 14) && !r->isHf()) {
         region_sum_e += et;
      } else if (ieta >= 7 && ieta <= 14) {
         region_sum_b += et;
      }
   }

   edm::Handle< edm::SortedCollection<HBHERecHit> > hits;
   if (!event.getByLabel(rechits_, hits)) {
      edm::LogError("ChainCmpPlotter") <<
         "Can't find rec hit collection with tag '" << rechits_ << "'" << std::endl;
      return;
   }

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

   for (auto hit = hits->begin(); hit != hits->end(); ++hit) {
      HcalDetId id = static_cast<HcalDetId>(hit->id());

      double eta = geo_endcap->getGeometry(id)->getPosition().eta();
      double phi = geo_endcap->getGeometry(id)->getPosition().phi();

      if (id.subdet() == HcalBarrel) {
         eta = geo_barrel->getGeometry(id)->getPosition().eta();
         phi = geo_barrel->getGeometry(id)->getPosition().phi();
      }

      double et = hit->energy() / cosh(eta);

      if (comp->getSeverityLevel(id,
               hit->flags(),
               status->getValues(id)->getValue()) > 10)
         continue;

      rh_energies[l1_geo->globalEtaIndex(eta)][l1_geo->htSumPhiIndex(phi)] += et;

      if (hit->energy() < 0.7)
         continue;

      if (et < cut_)
         continue;

      if (id.subdet() == HcalBarrel)
         rechit_sum_b += et;
      else if (id.subdet() == HcalEndcap)
         rechit_sum_e += et;
   }

   // ====.
   // TPDs >-----------------------------------------------------------
   // ===='
   Handle<HcalTrigPrimDigiCollection> digis;
   if (!event.getByLabel(digis_, digis)) {
      LogError("HcalTrigPrimDigiCleaner") <<
         "Can't find hcal trigger primitive digi collection with tag '" <<
         digis_ << "'" << std::endl;
      return;
   }

   HcalTrigTowerGeometry tpd_geo;
   // setup.get<CaloGeometryRecord>().get(tpd_geo);

   ESHandle<L1CaloHcalScale> hcal_scale;
   setup.get<L1CaloHcalScaleRcd>().get(hcal_scale);
   const L1CaloHcalScale* h = hcal_scale.product();

   edm::ESHandle<L1RCTParameters> rct;
   setup.get<L1RCTParametersRcd>().get(rct);
   const L1RCTParameters* r = rct.product();

   for (const auto& digi: *digis) {
      HcalTrigTowerDetId id = digi.id();

      float hcal = h->et(digi.SOI_compressedEt(), id.ietaAbs(), id.zside());
      float ecal = 0.;
      float et = 0.;

      if (id.ietaAbs() > 28)
         continue;

      try {
         et = r->JetMETTPGSum(ecal, hcal, id.ietaAbs());
      } catch (...) {
         edm::LogError("ChainCmpPlotter") << "Failed to convert "
            << id.ietaAbs() << ", " << hcal << std::endl;
         continue;
      }

      auto ids = tpd_geo.detIds(id);

      if (ids.size() < 1)
         continue;

      double eta = geo_endcap->getGeometry(ids[0])->getPosition().eta();
      double phi = geo_endcap->getGeometry(ids[0])->getPosition().phi();

      if (ids[0].subdet() == HcalBarrel) {
         eta = geo_barrel->getGeometry(ids[0])->getPosition().eta();
         phi = geo_barrel->getGeometry(ids[0])->getPosition().phi();
      }

      tp_energies[l1_geo->globalEtaIndex(eta)][l1_geo->htSumPhiIndex(phi)] += et;
   }

   edm::Handle< edm::SortedCollection<CaloTower> > towers;
   if (!event.getByLabel(towers_, towers)) {
      edm::LogError("ChainCmpPlotter") <<
         "Can't find tower collection with tag '" << towers_ << "'" << std::endl;
      return;
   }

   for (const auto& t: *(towers.product())) {
      if (t.hadEnergy() < 0.7)
         continue;

      if (t.hadEt() < cut_)
         continue;


      if (t.ietaAbs() <= 16)
         tower_sum_b += t.hadEt();
      else if (t.ietaAbs() <= 28)
         tower_sum_e += t.hadEt();
   }

   for (int i = 0; i < 22; ++i) {
      for (int j = 0; j < 18; ++j) {
         double l1 = 0.;
         double rh = 0.;
         double tp = 0.;

         for (int n = -1; n <= 1; ++n) {
            for (int m = -1; m <= 1; ++m) {
               int x = (i + n + 22) % 22;
               int y = (j + m + 18) % 18;

               l1 += l1_energies[x][y];
               rh += rh_energies[x][y];
               tp += tp_energies[x][y];
            }
         }

         if (l1_energies[i][j] > 1 || rh_energies[i][j] > 1 || tp_energies[i][j] > 1)
            if (debug_)
               std::cout << i << ", " << l1 << "\t->\t" << tp << "\t,\t" << rh << std::endl;
      }
   }

   regions_vs_rechits_b_->Fill(region_sum_b, rechit_sum_b, weight);
   regions_vs_towers_b_->Fill(region_sum_b, tower_sum_b, weight);
   regions_vs_rechits_e_->Fill(region_sum_e, rechit_sum_e, weight);
   regions_vs_towers_e_->Fill(region_sum_e, tower_sum_e, weight);
}

void
ChainCmpPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(ChainCmpPlotter);
