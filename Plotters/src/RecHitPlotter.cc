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
#include "DataFormats/EcalRecHit/interface/EcalRecHit.h"
#include "DataFormats/HcalDetId/interface/HcalDetId.h"
#include "DataFormats/HcalRecHit/interface/HBHERecHit.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH1D.h"
#include "TH2D.h"

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

      template<typename THit, typename TDetId>
      std::pair<double, double> process_calo(const edm::Event&,
            const edm::InputTag&, TH2D*, TH2D*);

      // ----------member data ---------------------------
      TH2D* ecal_en_;
      TH2D* ecal_mp_;
      TH2D* hcal_en_;
      TH2D* hcal_mp_;

      TH1D* ecal_en_tot_;
      TH1D* ecal_hits_;
      TH1D* hcal_en_tot_;
      TH1D* hcal_hits_;

      edm::InputTag ecalHits_;
      edm::InputTag hcalHits_;
};

RecHitPlotter::RecHitPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   ecalHits_(config.getParameter<edm::InputTag>("ecalHits")),
   hcalHits_(config.getParameter<edm::InputTag>("hcalHits"))
{
   edm::Service<TFileService> fs;
   ecal_en_ = fs->make<TH2D>("ecal_en", "Energy of ECAL;#eta;#phi;E [GeV]",
	 57, -85.5, 85.5, 60, 0.5, 360.5); 
   ecal_mp_ = fs->make<TH2D>("ecal_mp", "Mutliplicity of ECAL;#eta;#phi;Multiplicity",
	 57, -85.5, 85.5, 60, 0.5, 360.5); 
   hcal_en_ = fs->make<TH2D>("hcal_en", "Energy of HCAL;#eta;#phi;E [GeV]",
	 59, -29.5, 29.5, 36, 0.5, 72.5);
   hcal_mp_ = fs->make<TH2D>("hcal_mp", "Multiplicity of HCAL;#eta;#phi;Multiplicity",
	 59, -29.5, 29.5, 36, 0.5, 72.5);

   ecal_en_tot_ = fs->make<TH1D>("ecal_en_tot", "Total energy in ECAL;E [GeV];Num",
         350, 0., 3500.);
   ecal_hits_ = fs->make<TH1D>("ecal_hits", "Hits per event in the ECAL;n_{hits};Num",
         350, 0, 7000);
   hcal_en_tot_ = fs->make<TH1D>("hcal_en_tot", "Total energy in HCAL;E [GeV];Num",
         350, 0., 3500.);
   hcal_hits_ = fs->make<TH1D>("hcal_hits", "Hits per event in the HCAL;n_{hits};Num",
         200, 0, 2000);
}

RecHitPlotter::~RecHitPlotter() {}

template<typename THit, typename TDetId>
   std::pair<double, double>
RecHitPlotter::process_calo(const edm::Event& event,
      const edm::InputTag& tag, TH2D * en, TH2D * mp)
{
   double weight = this->weight(event);
   double e_tot = -1.;
   int nhits = 0;

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
      }
   }

   return std::make_pair(e_tot, nhits);
}

void
RecHitPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   double weight = this->weight(event);

   std::pair<double, double> p_ecal = process_calo<EcalRecHit, EBDetId>(
         event, ecalHits_, ecal_en_, ecal_mp_);
   std::pair<double, double> p_hcal = process_calo<HBHERecHit, HcalDetId>(
         event, hcalHits_, hcal_en_, hcal_mp_);

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
