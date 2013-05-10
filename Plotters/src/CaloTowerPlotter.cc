// -*- C++ -*-
// vim: sw=3:smarttab
//
// Package:    Plotters
// Class:      CaloTowerPlotter
// 
/**\class CaloTowerPlotter CaloTowerPlotter.cc Debug/Plotters/src/CaloTowerPlotter.cc

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
#include "DataFormats/CaloTowers/interface/CaloTower.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH1D.h"

//
// class declaration
//

class CaloTowerPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit CaloTowerPlotter(const edm::ParameterSet&);
      ~CaloTowerPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      TH1D* et_;
      TH1D* et_em_;
      TH1D* et_had_;

      TH1D* et_tot_;
      TH1D* et_tot_em_;
      TH1D* et_tot_had_;

      TH1D* et_b_;
      TH1D* et_b_em_;
      TH1D* et_b_had_;

      TH1D* et_tot_b_;
      TH1D* et_tot_b_em_;
      TH1D* et_tot_b_had_;

      TH1D* et_e_;
      TH1D* et_e_em_;
      TH1D* et_e_had_;

      TH1D* et_tot_e_;
      TH1D* et_tot_e_em_;
      TH1D* et_tot_e_had_;

      TH1D* et_f_;
      TH1D* et_f_em_;
      TH1D* et_f_had_;

      TH1D* et_tot_f_;
      TH1D* et_tot_f_em_;
      TH1D* et_tot_f_had_;

      TH1D* n_;

      edm::InputTag towers_;
};

CaloTowerPlotter::CaloTowerPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   towers_(config.getParameter<edm::InputTag>("towers"))
{
   edm::Service<TFileService> fs;

   et_ = fs->make<TH1D>("et",
         "CaloTower energy spectrum;E_{T};CaloTowers", 400, 0., 80.);
   et_em_ = fs->make<TH1D>("et_em",
         "CaloTower EM energy spectrum;E_{T};CaloTowers", 400, 0., 80.);
   et_had_ = fs->make<TH1D>("et_had",
         "CaloTower hadronic energy spectrum;E_{T};CaloTowers", 400, 0., 80.);

   et_tot_ = fs->make<TH1D>("et_tot",
         "CaloTower total energy spectrum;#sum E_{T};CaloTowers", 700, 0., 1400.);
   et_tot_em_ = fs->make<TH1D>("et_tot_em",
         "CaloTower total EM energy spectrum;#sum E_{T};CaloTowers", 700, 0., 1400.);
   et_tot_had_ = fs->make<TH1D>("et_tot_had",
         "CaloTower total hadronic energy spectrum;#sum E_{T};CaloTowers", 700, 0., 1400.);

   et_b_ = fs->make<TH1D>("et_b",
         "CaloTower energy spectrum (barrel);E_{T};CaloTowers", 400, 0., 80.);
   et_b_em_ = fs->make<TH1D>("et_b_em",
         "CaloTower EM energy spectrum (barrel);E_{T};CaloTowers", 400, 0., 80.);
   et_b_had_ = fs->make<TH1D>("et_b_had",
         "CaloTower hadronic energy spectrum (barrel);E_{T};CaloTowers", 400, 0., 80.);

   et_tot_b_ = fs->make<TH1D>("et_tot_b",
         "CaloTower total energy spectrum (barrel);#sum E_{T};CaloTowers", 700, 0., 1400.);
   et_tot_b_em_ = fs->make<TH1D>("et_tot_b_em",
         "CaloTower total EM energy spectrum (barrel);#sum E_{T};CaloTowers", 700, 0., 1400.);
   et_tot_b_had_ = fs->make<TH1D>("et_tot_b_had",
         "CaloTower total hadronic energy spectrum (barrel);#sum E_{T};CaloTowers", 700, 0., 1400.);

   et_e_ = fs->make<TH1D>("et_e",
         "CaloTower energy spectrum (endcap);E_{T};CaloTowers", 400, 0., 80.);
   et_e_em_ = fs->make<TH1D>("et_e_em",
         "CaloTower EM energy spectrum (endcap);E_{T};CaloTowers", 400, 0., 80.);
   et_e_had_ = fs->make<TH1D>("et_e_had",
         "CaloTower hadronic energy spectrum (endcap);E_{T};CaloTowers", 400, 0., 80.);

   et_tot_e_ = fs->make<TH1D>("et_tot_e",
         "CaloTower total energy spectrum (endcap);#sum E_{T};CaloTowers", 700, 0., 1400.);
   et_tot_e_em_ = fs->make<TH1D>("et_tot_e_em",
         "CaloTower total EM energy spectrum (endcap);#sum E_{T};CaloTowers", 700, 0., 1400.);
   et_tot_e_had_ = fs->make<TH1D>("et_tot_e_had",
         "CaloTower total hadronic energy spectrum (endcap);#sum E_{T};CaloTowers", 700, 0., 1400.);

   et_f_ = fs->make<TH1D>("et_f",
         "CaloTower energy spectrum (forward);E_{T};CaloTowers", 400, 0., 80.);
   et_f_em_ = fs->make<TH1D>("et_f_em",
         "CaloTower EM energy spectrum (forward);E_{T};CaloTowers", 400, 0., 80.);
   et_f_had_ = fs->make<TH1D>("et_f_had",
         "CaloTower hadronic energy spectrum (forward);E_{T};CaloTowers", 400, 0., 80.);

   et_tot_f_ = fs->make<TH1D>("et_tot_f",
         "CaloTower total energy spectrum (forward);#sum E_{T};CaloTowers", 700, 0., 1400.);
   et_tot_f_em_ = fs->make<TH1D>("et_tot_f_em",
         "CaloTower total EM energy spectrum (forward);#sum E_{T};CaloTowers", 700, 0., 1400.);
   et_tot_f_had_ = fs->make<TH1D>("et_tot_f_had",
         "CaloTower total hadronic energy spectrum (forward);#sum E_{T};CaloTowers", 700, 0., 1400.);

   n_ = fs->make<TH1D>("n",
         "## of CaloTowers;n_{towers};Num",
         350, 0, 700);
}

CaloTowerPlotter::~CaloTowerPlotter() {}

void
CaloTowerPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   edm::Handle< edm::SortedCollection<CaloTower> > towers;
   if (!event.getByLabel(towers_, towers)) {
      edm::LogError("CaloTowerPlotter") <<
         "Can't find tower collection with tag '" << towers_ << "'" << std::endl;
      return;
   }

   double weight = this->weight(event);

   n_->Fill(towers->size(), weight);

   double et_tot = 0.;
   double et_tot_em = 0.;
   double et_tot_had = 0.;

   double et_tot_b = 0.;
   double et_tot_b_em = 0.;
   double et_tot_b_had = 0.;

   double et_tot_e = 0.;
   double et_tot_e_em = 0.;
   double et_tot_e_had = 0.;

   double et_tot_f = 0.;
   double et_tot_f_em = 0.;
   double et_tot_f_had = 0.;

   for (const auto& t: *(towers.product())) {
      et_tot += t.et();
      et_tot_em += t.emEt();
      et_tot_had += t.hadEt();

      et_->Fill(t.et(), weight);
      et_em_->Fill(t.emEt(), weight);
      et_had_->Fill(t.hadEt(), weight);

      if (t.ietaAbs() <= 16) {
         et_tot_b += t.et();
         et_tot_b_em += t.emEt();
         et_tot_b_had += t.hadEt();

         et_b_->Fill(t.et(), weight);
         et_b_em_->Fill(t.emEt(), weight);
         et_b_had_->Fill(t.hadEt(), weight);
      } else if (t.ietaAbs() <= 28) {
         et_tot_e += t.et();
         et_tot_e_em += t.emEt();
         et_tot_e_had += t.hadEt();

         et_e_->Fill(t.et(), weight);
         et_e_em_->Fill(t.emEt(), weight);
         et_e_had_->Fill(t.hadEt(), weight);
      } else {
         et_tot_f += t.et();
         et_tot_f_em += t.emEt();
         et_tot_f_had += t.hadEt();

         et_f_->Fill(t.et(), weight);
         et_f_em_->Fill(t.emEt(), weight);
         et_f_had_->Fill(t.hadEt(), weight);
      }
   }

   et_tot_->Fill(et_tot, weight);
   et_tot_em_->Fill(et_tot_em, weight);
   et_tot_had_->Fill(et_tot_had, weight);

   et_tot_b_->Fill(et_tot_b, weight);
   et_tot_b_em_->Fill(et_tot_b_em, weight);
   et_tot_b_had_->Fill(et_tot_b_had, weight);

   et_tot_e_->Fill(et_tot_e, weight);
   et_tot_e_em_->Fill(et_tot_e_em, weight);
   et_tot_e_had_->Fill(et_tot_e_had, weight);

   et_tot_f_->Fill(et_tot_f, weight);
   et_tot_f_em_->Fill(et_tot_f_em, weight);
   et_tot_f_had_->Fill(et_tot_f_had, weight);
}

void
CaloTowerPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
   //The following says we do not know what parameters are allowed so do no validation
   // Please change this to state exactly what you do use, even if it is no parameters
   edm::ParameterSetDescription desc;
   desc.setUnknown();
   descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(CaloTowerPlotter);
