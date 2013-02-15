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
#include "DataFormats/VertexReco/interface/Vertex.h"

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
      edm::InputTag vertices_;

      bool use_vertices_;

      TH1D *hcal_presample_;

      TH1D *ecal_digi_b_[10];
      TH1D *ecal_digi_e_[10];
      TH1D *hcal_digi_b_[10];
      TH1D *hcal_digi_e_[10];
      TH1D *hcal_digi_ieta_b_[10][8];
      TH1D *hcal_digi_ieta_e_[10][8];

      TH1D *ecal_digi_vtx_b_[10][20];
      TH1D *ecal_digi_vtx_e_[10][20];
      TH1D *hcal_digi_vtx_b_[10][20];
      TH1D *hcal_digi_vtx_e_[10][20];
};

DigiPlotter::DigiPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   ecal_digis_(config.getParameter<edm::InputTag>("ecalDigis")),
   hcal_digis_(config.getParameter<edm::InputTag>("hcalDigis")),
   vertices_(config.getParameter<edm::InputTag>("vertices")),
   use_vertices_(config.getUntrackedParameter<bool>("useVertices", false))
{
   edm::Service<TFileService> fs;
   hcal_presample_ = fs->make<TH1D>("hcal_presample", "HCAL presamples",
         10, -0.5, 9.5);

   for (int i = 0; i < 10; ++i) {
      ecal_digi_b_[i] = fs->make<TH1D>(TString::Format("ecal_digi_b_%d", i),
            TString::Format("ECAL digi %d;ADC count;Num", i), 2000, 0, 4000);
      ecal_digi_e_[i] = fs->make<TH1D>(TString::Format("ecal_digi_e_%d", i),
            TString::Format("ECAL digi %d;ADC count;Num", i), 2000, 0, 4000);
      hcal_digi_b_[i] = fs->make<TH1D>(TString::Format("hcal_digi_b_%d", i),
            TString::Format("HCAL digi %d;ADC count;Num", i), 500, 0, 500);
      hcal_digi_e_[i] = fs->make<TH1D>(TString::Format("hcal_digi_e_%d", i),
            TString::Format("HCAL digi %d;ADC count;Num", i), 500, 0, 500);

      for (int j = 0; j < 20 && use_vertices_; ++j) {
         ecal_digi_vtx_b_[i][j] = fs->make<TH1D>(
            TString::Format("ecal_digi_%d_vtx_b_%02d", i, j),
            TString::Format("EB ADC of digi %d with %d < nvtx < %d;ADC;Num",
               i, j * 5, j * 5 + 6),
            2000, 0., 4000);
         ecal_digi_vtx_e_[i][j] = fs->make<TH1D>(
            TString::Format("ecal_digi_%d_vtx_e_%02d", i, j),
            TString::Format("EE ADC of digi %d with %d < nvtx < %d;ADC;Num",
               i, j * 5, j * 5 + 6),
            500, 0., 500);
         hcal_digi_vtx_b_[i][j] = fs->make<TH1D>(
            TString::Format("hcal_digi_%d_vtx_b_%02d", i, j),
            TString::Format("HB ADC of digi %d with %d < nvtx < %d;ADC;Num",
               i, j * 5, j * 5 + 6),
            500, 0., 500);
         hcal_digi_vtx_e_[i][j] = fs->make<TH1D>(
            TString::Format("hcal_digi_%d_vtx_e_%02d", i, j),
            TString::Format("HE ADC of digi %d with %d < nvtx < %d;ADC;Num",
               i, j * 5, j * 5 + 6),
            500, 0., 500);
      }
   }

   for (int j = 0; j < 8; ++j) {
      for (int i = 0; i < 10; ++i) {
         hcal_digi_ieta_b_[i][j] = fs->make<TH1D>(TString::Format("hcal_digi_b_ieta%d_%d", j + 1, i),
               TString::Format("HB digi %d (%d <= ieta <= %d);ADC count;Num", i, j * 4 + 1, (j + 1) * 4), 500, 0, 500);
         hcal_digi_ieta_e_[i][j] = fs->make<TH1D>(TString::Format("hcal_digi_e_ieta%d_%d", j + 1, i),
               TString::Format("HE digi %d (%d <= ieta <= %d);ADC count;Num", i, j * 4 + 1, (j + 1) * 4), 500, 0, 500);
      }
   }
}


DigiPlotter::~DigiPlotter() {}

void
DigiPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   double weight = this->weight(event);
   int nvtx_bin = -1;

   edm::Handle< std::vector<reco::Vertex> > vertices;
   if (use_vertices_) {
      if (!event.getByLabel(vertices_, vertices)){
         edm::LogError("DigiPlotter") << "No valid vertices!" << std::endl;
         return;
      }

      int nvtx = 0;
      for (const auto& v: *(vertices.product())) {
         if (v.ndof() < 5 || fabs(v.z()) > 24. || fabs(v.position().rho()) > 2.)
            continue;
         nvtx++;
      }
      nvtx_bin = (nvtx - 1) / 5;
   }

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
            ecal_digi_b_[i]->Fill(sample.adc(), weight);

            if (0 <= nvtx_bin && nvtx_bin < 20)
               ecal_digi_vtx_b_[i][nvtx_bin]->Fill(sample.adc(), weight);
         }
      }
   }

   Handle<EEDigiCollection> ee_digis;
   if (!event.getByLabel(ecal_digis_, ee_digis)) {
      LogError("DigiPlotter") <<
         "Can't find ecal digi collection with tag '" <<
         ecal_digis_ << "'" << std::endl;
   } else {
      for (EEDigiCollection::const_iterator digi = e_digis->begin();
            digi != e_digis->end(); ++digi) {
         EEDataFrame df(*digi);

         for (unsigned int i = 0; i < digi->size(); ++i) {
            EcalMGPASample sample(df.sample(i));
            ecal_digi_e_[i]->Fill(sample.adc(), weight);

            if (0 <= nvtx_bin && nvtx_bin < 20)
               ecal_digi_vtx_e_[i][nvtx_bin]->Fill(sample.adc(), weight);
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
         HcalDetId id = digi->id();

         hcal_presample_->Fill(digi->presamples(), weight);

         for (int i = 0; i < digi->size(); ++i) {
            HcalQIESample sample(digi->sample(i));
            int bin = (abs(digi->id().ieta()) - 1) / 4;

            if (id.subdet() == HcalBarrel) {
               hcal_digi_b_[i]->Fill(sample.adc(), weight);
               hcal_digi_ieta_b_[i][bin]->Fill(sample.adc(), weight);

               if (0 <= nvtx_bin && nvtx_bin < 20)
                  hcal_digi_vtx_b_[i][nvtx_bin]->Fill(sample.adc(), weight);
            } else {
               hcal_digi_e_[i]->Fill(sample.adc(), weight);
               hcal_digi_ieta_e_[i][bin]->Fill(sample.adc(), weight);

               if (0 <= nvtx_bin && nvtx_bin < 20)
                  hcal_digi_vtx_e_[i][nvtx_bin]->Fill(sample.adc(), weight);
            }
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
