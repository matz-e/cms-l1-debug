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

#include "TH1D.h"
#include "TString.h"
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

      TH1D *hcal_presample_;

      TH1D *ecal_digi_[10];
      TH1D *hcal_digi_[10];
};

DigiPlotter::DigiPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   ecal_digis_(config.getParameter<edm::InputTag>("ecalDigis")),
   hcal_digis_(config.getParameter<edm::InputTag>("hcalDigis"))
{
   edm::Service<TFileService> fs;
   hcal_presample_ = fs->make<TH1D>("hcal_presample", "HCAL presamples",
         10, -0.5, 9.5);

   for (int i = 0; i < 10; ++i) {
      ecal_digi_[i] = fs->make<TH1D>(TString::Format("ecal_digi_%d", i),
            TString::Format("ECAL digi %d;ADC count;Num", i), 2000, 0, 4000);
      hcal_digi_[i] = fs->make<TH1D>(TString::Format("hcal_digi_%d", i),
            TString::Format("HCAL digi %d;ADC count;Num", i), 500, 0, 500);
   }
}


DigiPlotter::~DigiPlotter() {}

void
DigiPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   double weight = this->weight(event);

   Handle<EBDigiCollection> e_digis;
   if (!event.getByLabel(ecal_digis_, e_digis)) {
      LogError("DigiPlotter") <<
         "Can't find ecal digi collection with tag '" <<
         ecal_digis_ << "'" << std::endl;
   } else {
      for (EBDigiCollection::const_iterator digi = e_digis->begin();
            digi != e_digis->end(); ++digi) {
         EBDataFrame df(*digi);

         for (unsigned int i = 0; i < digi->size(); ++i) {
            EcalMGPASample sample(df.sample(i));
            ecal_digi_[i]->Fill(sample.adc(), weight);
         }
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
         hcal_presample_->Fill(digi->presamples(), weight);

         for (int i = 0; i < digi->size(); ++i) {
            HcalQIESample sample(digi->sample(i));
            hcal_digi_[i]->Fill(sample.adc(), weight);
         }
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
