// -*- C++ -*-
//
// Package:    DigiPlotter
// Class:      DigiPlotter
// 
/**\class DigiPlotter DigiPlotter.cc DataMixerValidation/DigiPlotter/src/DigiPlotter.cc

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

#include "DataFormats/EcalDigi/interface/EcalDigiCollections.h"
#include "DataFormats/HcalDigi/interface/HBHEDataFrame.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TNtuple.h"
//
// class declaration
//

class DigiPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit DigiPlotter(const edm::ParameterSet&);
      ~DigiPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      edm::InputTag ecal_digis_;
      edm::InputTag hcal_digis_;

      TNtuple *tpl_e_digis_;
      TNtuple *tpl_h_digis_;
};

DigiPlotter::DigiPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   ecal_digis_(config.getParameter<edm::InputTag>("ecalDigis")),
   hcal_digis_(config.getParameter<edm::InputTag>("hcalDigis"))
{
   edm::Service<TFileService> fs;
   tpl_e_digis_ = fs->make<TNtuple>("ecal_digis", "",
         "e0:e1:e2:e3:e4:e5:e6:e7:e8:e9:weight");
   tpl_h_digis_ = fs->make<TNtuple>("hcal_digis", "",
         "d0:d1:d2:d3:d4:d5:d6:d7:d8:d9:weight");
}


DigiPlotter::~DigiPlotter() {}

void
DigiPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   Handle<EBDigiCollection> e_digis;
   if (!event.getByLabel(ecal_digis_, e_digis)) {
      LogError("DigiPlotter") <<
         "Can't find ecal digi collection with tag '" <<
         ecal_digis_ << "'" << std::endl;
   } else {
      for (EBDigiCollection::const_iterator digi = e_digis->begin();
            digi != e_digis->end(); ++digi) {
         EBDataFrame df(*digi);
         float digi_vals[11];
         digi_vals[10] = this->weight(event);

         for (unsigned int i = 0; i < digi->size(); ++i) {
            EcalMGPASample sample(df.sample(i));
            digi_vals[i] = sample.adc();
         }

         tpl_e_digis_->Fill(digi_vals);
      }
   }

   Handle< SortedCollection<HBHEDataFrame> > h_digis;
   if (!event.getByLabel(hcal_digis_, h_digis)) {
      LogError("DigiPlotter") <<
         "Can't find hcal digi collection with tag '" <<
         hcal_digis_ << "'" << std::endl;
   } else {
      SortedCollection<HBHEDataFrame>::const_iterator digi;
      for (digi = h_digis->begin(); digi != h_digis->end(); ++digi) {
         float digi_vals[11];
         digi_vals[10] = this->weight(event);

         for (int i = 0; i < digi->size(); ++i) {
            HcalQIESample sample(digi->sample(i));
            digi_vals[i] = sample.adc();
         }

         tpl_h_digis_->Fill(digi_vals);
      }
   }
}

void
DigiPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(DigiPlotter);
