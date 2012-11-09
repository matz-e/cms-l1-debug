// -*- C++ -*-
//
// Package:    RecHitTPPlotter
// Class:      RecHitTPPlotter
// 
/**\class RecHitTPPlotter RecHitTPPlotter.cc Plotters/Debug/src/RecHitTPPlotter.cc

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
#include <utility>

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
#include "DataFormats/HcalDetId/interface/HcalDetId.h"
#include "DataFormats/HcalDetId/interface/HcalTrigTowerDetId.h"
#include "DataFormats/HcalDigi/interface/HcalTriggerPrimitiveDigi.h"
#include "DataFormats/HcalRecHit/interface/HBHERecHit.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TTree.h"
//
// class declaration
//

class RecHitTPPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit RecHitTPPlotter(const edm::ParameterSet&);
      ~RecHitTPPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      edm::InputTag hcal_digis_;
      edm::InputTag hcal_hits_;

      TTree *data_;

      int ieta_;
      int iphi_;
      double weight_;
      double hit_;
      int tp_;
};

RecHitTPPlotter::RecHitTPPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   hcal_digis_(config.getParameter<edm::InputTag>("hcalDigis")),
   hcal_hits_(config.getParameter<edm::InputTag>("hcalHits"))
{
   edm::Service<TFileService> fs;
   data_ = fs->make<TTree>("energies", "Energies from both RecHit and TP for HCAL");
   data_->Branch("ieta", &ieta_);
   data_->Branch("iphi", &iphi_);
   data_->Branch("HCAL_RecHit", &hit_);
   data_->Branch("HCAL_TP", &tp_);
   data_->Branch("weight", &weight_);
}

RecHitTPPlotter::~RecHitTPPlotter() {}

void
RecHitTPPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   weight_ = this->weight(event);

   std::map< int, std::map< int, std::pair<int, double> > > energies;

   edm::Handle< edm::SortedCollection<HBHERecHit> > hits;
   if (!event.getByLabel(hcal_hits_, hits)) {
      edm::LogError("RecHitPlotter") <<
         "Can't find rec hit collection with tag '" << hcal_hits_ << "'" << std::endl;
   } else {
      typename edm::SortedCollection<HBHERecHit>::const_iterator hit;
      for (hit = hits->begin(); hit != hits->end(); ++hit) {
         HcalDetId id = static_cast<HcalDetId>(hit->id());
         energies[id.ieta()][id.iphi()].second += hit->energy();
      }
   }

   Handle< SortedCollection<HcalTriggerPrimitiveDigi> > hcal_handle_;
   if (!event.getByLabel(hcal_digis_, hcal_handle_)) {
      LogError("RecHitTPPlotter") <<
         "Can't find hcal trigger primitive digi collection with tag '" <<
         hcal_digis_ << "'" << std::endl;
   } else {
      SortedCollection<HcalTriggerPrimitiveDigi>::const_iterator p;
      for (p = hcal_handle_->begin(); p != hcal_handle_->end();
            ++p) {
         HcalTrigTowerDetId id = p->id();
         energies[id.ieta()][id.iphi()].first += p->SOI_compressedEt();
      }
   }

   for (auto i = energies.begin(); i != energies.end(); ++i) {
      ieta_ = i->first;
      for (auto j = i->second.begin(); j != i->second.end(); ++j) {
         iphi_ = j->first;
         tp_ = j->second.first;
         hit_ = j->second.second;

         if (tp_ > 0 || hit_ > 0)
            data_->Fill();
      }
   }
}

void
RecHitTPPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(RecHitTPPlotter);
