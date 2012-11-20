// -*- C++ -*-
// vim: sw=3:smarttab
//
// Package:    Plotters
// Class:      PileUpPlotter
// 
/**\class PileUpPlotter PileUpPlotter.cc Debug/Plotters/src/PileUpPlotter.cc

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

#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH2D.h"
#include "TH1D.h"
#include "TNtuple.h"

//
// class declaration
//

class PileUpPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit PileUpPlotter(const edm::ParameterSet&);
      ~PileUpPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      TH1D* interactions_;

      edm::InputTag pileup_;
};

PileUpPlotter::PileUpPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   pileup_(config.getParameter<edm::InputTag>("PVT"))
{
   edm::Service<TFileService> fs;
   interactions_ = fs->make<TH1D>("pileup", "PileUp;# of true interactions",
         150, 0., 150.);
}

PileUpPlotter::~PileUpPlotter() {}

void
PileUpPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   edm::Handle< std::vector<PileupSummaryInfo> > pu;
   event.getByLabel(pileup_, pu);

   if (!pu.isValid()) {
      edm::LogError("PileUpPlotter") << "No valid pileup information for '"
         << pileup_ << "'!" << std::endl;
      return;
   }

   double weight = this->weight(event);

   for (auto i = pu->begin(); i != pu->end(); ++i) {
      if (i->getBunchCrossing() == 0) {
         interactions_->Fill(i->getPU_NumInteractions(), weight);
      }
   }
}

void
PileUpPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
   //The following says we do not know what parameters are allowed so do no validation
   // Please change this to state exactly what you do use, even if it is no parameters
   edm::ParameterSetDescription desc;
   desc.setUnknown();
   descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PileUpPlotter);
