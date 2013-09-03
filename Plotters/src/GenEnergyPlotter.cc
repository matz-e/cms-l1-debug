// -*- C++ -*-
//
// Package:    GenEnergyPlotter
// Class:      GenEnergyPlotter
// 
/**\class GenEnergyPlotter GenEnergyPlotter.cc Debug/Plotters/src/GenEnergyPlotter.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  matthias wolf
//         Created:  Aug 27 11:22 CDT 2013
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/ESHandle.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH1D.h"
#include "TString.h"
//
// class declaration
//

class GenEnergyPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit GenEnergyPlotter(const edm::ParameterSet&);
      ~GenEnergyPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      edm::InputTag gen_;

      TH1D *gen_energy_;
};

GenEnergyPlotter::GenEnergyPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   gen_(config.getParameter<edm::InputTag>("particles"))
{
   edm::Service<TFileService> fs;

   gen_energy_ = fs->make<TH1D>("gen_energy",
         "Gen Particle Energy;#sum E_{T};Num", 750, 0, 750);
}

GenEnergyPlotter::~GenEnergyPlotter() {}

void
GenEnergyPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   double weight = this->weight(event);
   double sum = 0.;

   edm::Handle<std::vector<reco::GenParticle>> particles;
   if (!event.getByLabel(gen_, particles)) {
      LogError("CaloRegionPlotter") <<
         "Can't find calo region collection with tag '" <<
         gen_ << "'" << std::endl;
      return;
   }

   for (const auto& p: *particles.product()) {
      if (p.numberOfDaughters() == 0)
         sum += p.et();
   }

   gen_energy_->Fill(sum, weight);
}

void
GenEnergyPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(GenEnergyPlotter);
