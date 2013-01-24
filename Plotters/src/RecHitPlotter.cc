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

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH1D.h"
#include "TH2D.h"

//
// class declaration
//

template<typename THit, typename TDetId>
std::pair<double, double> process_calo(
      const edm::Event&, const edm::InputTag&,
      TH2D*, TH2D*,
      TH1D*, TH1D*, TH1D*, TH1D*, TH1D*, TH1D*,
      bool barrel=true, bool endcap=true);
template<typename THit>
std::pair<double, double> process_calo<THit, EEDetId>(
      const edm::Event&, const edm::InputTag&,
      TH2D*, TH2D*,
      TH1D*, TH1D*, TH1D*, TH1D*, TH1D*, TH1D*,
      bool barrel=true, bool endcap=true);

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
      TH1D* hcal_en_tot_e_;
      TH1D* hcal_en_tot_b_;
      TH1D* hcal_hits_b_;
      TH1D* hcal_hits_e_;

      std::vector<edm::InputTag> ecalHits_;
      edm::InputTag hcalHits_;
};

RecHitPlotter::RecHitPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   ecalHits_(config.getParameter< std::vector<edm::InputTag> >("ecalHits")),
   hcalHits_(config.getParameter<edm::InputTag>("hcalHits"))
{
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
         700, 0., 3500.);
   ecal_en_tot_ = fs->make<TH1D>("ecal_en_tot", "Total energy in ECAL;E [GeV];Num",
         700, 0., 3500.);
   ecal_hits_ = fs->make<TH1D>("ecal_hits", "Hits per event in the ECAL;n_{hits};Num",
         1400, 0, 7000);

   ecal_en_b_ = fs->make<TH1D>("ecal_en_b",
         "Energy in the ECAL barrel;n_{hits};Num",
         400, 0, 2000);
   ecal_en_e_ = fs->make<TH1D>("ecal_en_e",
         "Energy in the ECAL endcap;n_{hits};Num",
         400, 0, 2000);
   ecal_en_tot_e_ = fs->make<TH1D>("ecal_en_tot_b",
         "Total energy in the ECAL barrel;n_{hits};Num",
         400, 0, 2000);
   ecal_en_tot_b_ = fs->make<TH1D>("ecal_en_tot_e",
         "Total energy in the ECAL endcap;n_{hits};Num",
         400, 0, 2000);
   ecal_hits_b_ = fs->make<TH1D>("ecal_rechits_b",
         "Hits in the ECAL barrel;n_{hits};Num",
         400, 0, 2000);
   ecal_hits_e_ = fs->make<TH1D>("ecal_rechits_b",
         "Hits in the ECAL endcap;n_{hits};Num",
         400, 0, 2000);

   hcal_en_ = fs->make<TH1D>("hcal_en", "Energy in HCAL;E [GeV];Num",
         700, 0., 3500.);
   hcal_en_tot_ = fs->make<TH1D>("hcal_en_tot", "Total energy in HCAL;E [GeV];Num",
         700, 0., 3500.);
   hcal_hits_ = fs->make<TH1D>("hcal_hits", "Hits per event in the HCAL;n_{hits};Num",
         400, 0, 2000);

   hcal_en_b_ = fs->make<TH1D>("hcal_en_b",
         "Energy in the HCAL barrel;n_{hits};Num",
         400, 0, 2000);
   hcal_en_e_ = fs->make<TH1D>("hcal_en_e",
         "Energy in the HCAL endcap;n_{hits};Num",
         400, 0, 2000);
   hcal_en_tot_e_ = fs->make<TH1D>("hcal_en_tot_b",
         "Total energy in the HCAL barrel;n_{hits};Num",
         400, 0, 2000);
   hcal_en_tot_b_ = fs->make<TH1D>("hcal_en_tot_e",
         "Total energy in the HCAL endcap;n_{hits};Num",
         400, 0, 2000);
   hcal_hits_b_ = fs->make<TH1D>("hcal_rechits_b",
         "Hits in the HCAL barrel;n_{hits};Num",
         400, 0, 2000);
   hcal_hits_e_ = fs->make<TH1D>("hcal_rechits_b",
         "Hits in the HCAL endcap;n_{hits};Num",
         400, 0, 2000);
}

RecHitPlotter::~RecHitPlotter() {}

template<typename THit, typename TDetId>
   static std::pair<double, double>
process_calo(
      const edm::Event& event,
      const edm::InputTag& tag,
      TH2D *en, TH2D *mp,
      TH1D *en_b, TH1D *en_e,
      TH1D *en_tot_b, TH1D *en_tot_e,
      TH1D *hits_b, TH1D *hits_e,
      bool barrel, bool endcap)
{
   double weight = this->weight(event);
   double e_tot = -1.;
   double e_tot_b = -1.;
   double e_tot_e = -1.;
   int nhits = 0;
   int nhits_b = 0;
   int nhits_e = 0;

   edm::Handle< edm::SortedCollection<THit> > hits;
   if (!event.getByLabel(tag, hits)) {
      edm::LogError("RecHitPlotter") <<
         "Can't find rec hit collection with tag '" << tag << "'" << std::endl;
   } else {
      nhits = hits->size();
      e_tot = 0.;

      typename edm::SortedCollection<THit>::const_iterator hit;
      for (hit = hits->begin(); hit != hits->end(); ++hit) {
         TDetId id = static_cast<TDetId>(hit->id());
         e_tot += hit->energy();
         en->Fill(id.ieta(), id.iphi(), hit->energy() * weight);
         mp->Fill(id.ieta(), id.iphi(), weight);

         if (id.subdet() == 1) {
            ++nhits_b;
            en_b->Fill(hit->energy(), weight);
            e_tot_b += hit->energy();
         } else if (id.subdet() == 2) {
            ++nhits_e;
            en_e->Fill(hit->energy(), weight);
            e_tot_e += hit->energy();
         } else {
            edm::LogError("RecHitPlotter") <<
               "Unknown subdet id in rec hit collection with tag '" <<
               tag << "': " << id.subdet() << std::endl;
         }
      }
   }

   if (barrel)
      hits_b->Fill(nhits_b, weight);
   if (endcap)
      hits_e->Fill(nhits_e, weight);

   return std::make_pair(e_tot, nhits);
}

template<typename THit>
   std::pair<double, double>
process_calo<THit, EEDetId>(
      const edm::Event& event,
      const edm::InputTag& tag,
      TH2D *en, TH2D *mp,
      TH1D *en_b, TH1D *en_e,
      TH1D *en_tot_b, TH1D *en_tot_e,
      TH1D *hits_b, TH1D *hits_e,
      bool barrel, bool endcap)
{
   double weight = this->weight(event);
   double e_tot = -1.;
   double e_tot_b = -1.;
   double e_tot_e = -1.;
   int nhits = 0;
   int nhits_b = 0;
   int nhits_e = 0;

   edm::Handle< edm::SortedCollection<THit> > hits;
   if (!event.getByLabel(tag, hits)) {
      edm::LogError("RecHitPlotter") <<
         "Can't find rec hit collection with tag '" << tag << "'" << std::endl;
   } else {
      nhits = hits->size();
      e_tot = 0.;

      typename edm::SortedCollection<THit>::const_iterator hit;
      for (hit = hits->begin(); hit != hits->end(); ++hit) {
         TDetId id = static_cast<EEDetId>(hit->id());
         e_tot += hit->energy();

         if (id.subdet() == 1) {
            ++nhits_b;
            en_b->Fill(hit->energy(), weight);
            e_tot_b += hit->energy();
         } else if (id.subdet() == 2) {
            ++nhits_e;
            en_e->Fill(hit->energy(), weight);
            e_tot_e += hit->energy();
         } else {
            edm::LogError("RecHitPlotter") <<
               "Unknown subdet id in rec hit collection with tag '" <<
               tag << "': " << id.subdet() << std::endl;
         }
      }
   }

   if (barrel)
      hits_b->Fill(nhits_b, weight);
   if (endcap)
      hits_e->Fill(nhits_e, weight);

   return std::make_pair(e_tot, nhits);
}

void
RecHitPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   double weight = this->weight(event);

   std::pair<double, double> p_ecal = process_calo<EcalRecHit, EBDetId>(
         event, ecalHits_[0],
         ecal_dist_en_, ecal_dist_mp_,
         ecal_en_b_, ecal_en_e_,
         ecal_en_tot_b_, ecal_en_tot_e_,
         ecal_hits_b_, ecal_hits_e_);
   std::pair<double, double> p_ecal = process_calo<EcalRecHit, EEDetId>(
         event, ecalHits_[1],
         ecal_dist_en_, ecal_dist_mp_,
         ecal_en_b_, ecal_en_e_,
         ecal_en_tot_b_, ecal_en_tot_e_,
         ecal_hits_b_, ecal_hits_e_);
   std::pair<double, double> p_hcal = process_calo<HBHERecHit, HcalDetId>(
         event, hcalHits_,
         hcal_dist_en_, hcal_dist_mp_,
         hcal_en_b_, hcal_en_e_,
         hcal_en_tot_b_, hcal_en_tot_e_,
         hcal_hits_b_, hcal_hits_e_);

   ecal_en_tot_->Fill(p_ecal.first, weight);
   ecal_hits_->Fill(p_ecal.second, weight);
   hcal_en_tot_->Fill(p_hcal.first, weight);
   hcal_hits_->Fill(p_hcal.second, weight);
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
