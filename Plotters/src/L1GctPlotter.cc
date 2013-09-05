// -*- C++ -*-
//
// Package:    L1GctPlotter
// Class:      L1GctPlotter
// 
/**\class L1GctPlotter L1GctPlotter.cc DataMixerValidation/L1GctPlotter/src/L1GctPlotter.cc

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

#include "DataFormats/L1GlobalCaloTrigger/interface/L1GctCollections.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH1D.h"
#include "TString.h"
//
// class declaration
//

class L1GctPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit L1GctPlotter(const edm::ParameterSet&);
      ~L1GctPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      edm::InputTag gct_;

      TH1D *et_had_;
      TH1D *et_miss_;
      TH1D *et_tot_;
};

L1GctPlotter::L1GctPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   gct_(config.getParameter<edm::InputTag>("l1GctSums"))
{
   edm::Service<TFileService> fs;
   et_had_ = fs->make<TH1D>("et_had", "HTT;HTT [GeV];Num", 1000, 0., 4000.);
   et_miss_ = fs->make<TH1D>("et_miss", "ETM;ETM [GeV];Num", 1000, 0., 4000.);
   et_tot_ = fs->make<TH1D>("et_tot", "ETT;ETT [GeV];Num", 1000, 0., 4000.);
}


L1GctPlotter::~L1GctPlotter() {}

void
L1GctPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   double weight = this->weight(event);

   Handle<L1GctEtHadCollection> et_hads;
   if (!event.getByLabel(gct_, et_hads)) {
      LogError("L1GctPlotter") <<
         "Can't find L1GctEtHad collection with tag '" << gct_ << "'" << std::endl;
   } else {
      for (L1GctEtHadCollection::const_iterator et = et_hads->begin();
            et != et_hads->end(); ++et)
         et_had_->Fill(et->et() * 0.5, weight);
   }

   Handle<L1GctEtMissCollection> et_misss;
   if (!event.getByLabel(gct_, et_misss)) {
      LogError("L1GctPlotter") <<
         "Can't find L1GctEtMiss collection with tag '" << gct_ << "'" << std::endl;
   } else {
      for (L1GctEtMissCollection::const_iterator et = et_misss->begin();
            et != et_misss->end(); ++et)
         et_miss_->Fill(et->et() * 0.5, weight);
   }

   Handle<L1GctEtTotalCollection> et_tots;
   if (!event.getByLabel(gct_, et_tots)) {
      LogError("L1GctPlotter") <<
         "Can't find L1GctEtTotal collection with tag '" << gct_ << "'" << std::endl;
   } else {
      for (L1GctEtTotalCollection::const_iterator et = et_tots->begin();
            et != et_tots->end(); ++et)
         et_tot_->Fill(et->et() * 0.5, weight);
   }
}

void
L1GctPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(L1GctPlotter);
