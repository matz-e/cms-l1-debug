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
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "CalibFormats/CaloTPG/interface/CaloTPGRecord.h"
#include "CalibFormats/CaloTPG/interface/CaloTPGTranscoder.h"

#include "DataFormats/Common/interface/SortedCollection.h"
#include "DataFormats/HcalDetId/interface/HcalDetId.h"
#include "DataFormats/HcalDetId/interface/HcalTrigTowerDetId.h"
#include "DataFormats/HcalDigi/interface/HcalTriggerPrimitiveDigi.h"
#include "DataFormats/HcalRecHit/interface/HBHERecHit.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH2F.h"
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
      const static int NETA = 32;

      edm::InputTag hcal_digis_;
      edm::InputTag hcal_hits_;

      TH2F *hists_[2 * NETA + 1];
};

RecHitTPPlotter::RecHitTPPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   hcal_digis_(config.getParameter<edm::InputTag>("hcalDigis")),
   hcal_hits_(config.getParameter<edm::InputTag>("hcalHits"))
{
   edm::Service<TFileService> fs;
   for (int i = -NETA; i <= NETA; ++i)
      hists_[i + NETA] = fs->make<TH2F>(TString::Format("ieta_%d", i),
            TString::Format("RecHits vs TP (ieta %d);TP [GeV];RecHits [GeV]", i),
            500, 0, 500, 5000, 0, 500);
}

RecHitTPPlotter::~RecHitTPPlotter() {}

void
RecHitTPPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   ESHandle<CaloTPGTranscoder> tcoder;
   setup.get<CaloTPGRecord>().get(tcoder);
   tcoder->setup(setup, CaloTPGTranscoder::HcalTPG);

   double weight = this->weight(event);

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
         energies[id.ieta()][id.iphi()].first += 
            tcoder->hcaletValue(id.ieta(), id.iphi(), p->SOI_compressedEt());
      }
   }

   for (auto i = energies.begin(); i != energies.end(); ++i) {
      int ieta = i->first;
      for (auto j = i->second.begin(); j != i->second.end(); ++j) {
         int tp = j->second.first;
         double hit = j->second.second;

         if (tp > 0 || hit > 0.)
            hists_[ieta + NETA]->Fill(tp, hit, weight);
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
