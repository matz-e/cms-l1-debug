// -*- C++ -*-
//
// Package:    L1JetPlotter
// Class:      L1JetPlotter
// 
/**\class L1JetPlotter L1JetPlotter.cc DataMixerValidation/L1JetPlotter/src/L1JetPlotter.cc

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

#include "DataFormats/L1Trigger/interface/L1JetParticleFwd.h"
#include "DataFormats/L1Trigger/interface/L1JetParticle.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH1D.h"
#include "TH2D.h"
//
// class declaration
//

class L1JetPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit L1JetPlotter(const edm::ParameterSet&);
      ~L1JetPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      std::string jets_;

      TH1D *jet_n_;
      TH1D *jet_et_;
      TH1D *jet_et_tot_;

      TH2D *jet_dist_et_;
      TH2D *jet_dist_mp_;

      TH1D *jet_n_tau_;
      TH1D *jet_et_tau_;
      TH1D *jet_et_tot_tau_;

      TH2D *jet_dist_et_tau_;
      TH2D *jet_dist_mp_tau_;

      TH1D *jet_n_notau_;
      TH1D *jet_et_notau_;
      TH1D *jet_et_tot_notau_;

      TH2D *jet_dist_et_notau_;
      TH2D *jet_dist_mp_notau_;
};

L1JetPlotter::L1JetPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   jets_(config.getUntrackedParameter<std::string>("l1Jets"))
{
   edm::Service<TFileService> fs;

   jet_n_ = fs->make<TH1D>("jet_n", 
         "L1 GCT Jet Candidate Counts;# of jets;Num", 100, 0, 100);
   jet_et_ = fs->make<TH1D>("jet_et", 
         "L1 GCT Jet Candidates E_{T};E_{T} of jet;Num", 500, 0, 5000);
   jet_et_tot_ = fs->make<TH1D>("jet_et_tot", 
         "L1 GCT Jet Candidates;#sum E_{T} of jets;Num", 2000, 0, 20000);

   jet_dist_et_ = fs->make<TH2D>("jet_dist_et", 
         "L1 GCT Jet Candidate E_{T};ieta;iphi;E_{T}",
         22, -0.5, 21.5, 18, -0.5, 17.5);
   jet_dist_mp_ = fs->make<TH2D>("jet_dist_mp", 
         "L1 GCT Jet Candidate Count;ieta;iphi;Num",
         22, -0.5, 21.5, 18, -0.5, 17.5);

   jet_n_tau_ = fs->make<TH1D>("jet_tau_n", 
         "L1 GCT Jet Candidate Counts (#tau veto);# of jets;Num", 100, 0, 100);
   jet_et_tau_ = fs->make<TH1D>("jet_tau_et", 
         "L1 GCT Jet Candidates E_{T} (#tau veto);E_{T} of jet;Num", 500, 0, 5000);
   jet_et_tot_tau_ = fs->make<TH1D>("jet_tau_et_tot", 
         "L1 GCT Jet Candidates (#tau veto);#sum E_{T} of jets;Num", 2000, 0, 20000);

   jet_dist_et_tau_ = fs->make<TH2D>("jet_tau_dist_et", 
         "L1 GCT Jet Candidate E_{T} (#tau veto);ieta;iphi;E_{T}",
         22, -0.5, 21.5, 18, -0.5, 17.5);
   jet_dist_mp_tau_ = fs->make<TH2D>("jet_tau_dist_mp", 
         "L1 GCT Jet Candidate Count (#tau veto);ieta;iphi;Num",
         22, -0.5, 21.5, 18, -0.5, 17.5);

   jet_n_notau_ = fs->make<TH1D>("jet_notau_n", 
         "L1 GCT Jet Candidate Counts (no #tau veto);# of jets;Num", 100, 0, 100);
   jet_et_notau_ = fs->make<TH1D>("jet_notau_et", 
         "L1 GCT Jet Candidates E_{T} (no #tau veto);E_{T} of jet;Num", 500, 0, 5000);
   jet_et_tot_notau_ = fs->make<TH1D>("jet_notau_et_tot", 
         "L1 GCT Jet Candidates (no #tau veto);#sum E_{T} of jets;Num", 2000, 0, 20000);

   jet_dist_et_notau_ = fs->make<TH2D>("jet_notau_dist_et", 
         "L1 GCT Jet Candidate E_{T} (no #tau veto);ieta;iphi;E_{T}",
         22, -0.5, 21.5, 18, -0.5, 17.5);
   jet_dist_mp_notau_ = fs->make<TH2D>("jet_notau_dist_mp", 
         "L1 GCT Jet Candidate Count (no #tau veto);ieta;iphi;Num",
         22, -0.5, 21.5, 18, -0.5, 17.5);
}

L1JetPlotter::~L1JetPlotter() {}

void
L1JetPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   static const std::string jet_types[] = {"Central", "Forward", "Tau"};

   double weight = this->weight(event);

   int n = 0;
   int n_tau = 0;

   double jet_et_tot = 0;
   double jet_et_tot_tau = 0;
   double jet_et_tot_notau = 0;

   for (const auto& t: jet_types) {
      edm::InputTag tag(jets_, t);

      // All other L1 jet collections seem to be unsuitable...
      Handle<l1extra::L1JetParticleCollection> jets;
      if (!event.getByLabel(tag, jets)) {
         LogError("L1JetPlotter") <<
            "Can't find L1JetParticle collection with tag '" << tag << "'" << std::endl;
      } else {
         n += jets->size();
         if (t == "Tau")
            n_tau = jets->size();

         for (auto j = jets->cbegin(); j != jets->cend(); ++j) {
            auto jcand = j->gctJetCand();
            auto id = jcand->regionId();

            double en = j->energy();
            int ieta = id.ieta();
            int iphi = id.iphi();

            jet_et_tot += en;
            jet_et_->Fill(en, weight);
            jet_dist_et_->Fill(ieta, iphi, en * weight);
            jet_dist_mp_->Fill(ieta, iphi, weight);

            if (jcand->isTau()) {
               jet_et_tot_tau += en;
               jet_et_tau_->Fill(en, weight);
               jet_dist_et_tau_->Fill(ieta, iphi, en * weight);
               jet_dist_mp_tau_->Fill(ieta, iphi, weight);
            } else {
               jet_et_tot_notau += en;
               jet_et_notau_->Fill(en, weight);
               jet_dist_et_notau_->Fill(ieta, iphi, en * weight);
               jet_dist_mp_notau_->Fill(ieta, iphi, weight);
            }
         }
      }
   }

   jet_n_->Fill(n, weight);
   jet_n_tau_->Fill(n_tau, weight);
   jet_n_notau_->Fill(n - n_tau, weight);

   jet_et_tot_->Fill(jet_et_tot, weight);
   jet_et_tot_tau_->Fill(jet_et_tot_tau, weight);
   jet_et_tot_notau_->Fill(jet_et_tot_notau, weight);
}

void
L1JetPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(L1JetPlotter);
