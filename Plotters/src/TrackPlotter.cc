// -*- C++ -*-
// vim: sw=3:smarttab
//
// Package:    Plotters
// Class:      TrackPlotter
// 
/**\class TrackPlotter TrackPlotter.cc Debug/Plotters/src/TrackPlotter.cc

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

#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/VertexReco/interface/Vertex.h"

#include "Debug/Plotters/interface/BasePlotter.h"

#include "TH2D.h"
#include "TH1D.h"
#include "TNtuple.h"

//
// class declaration
//

class TrackPlotter : public edm::EDAnalyzer, BasePlotter {
   public:
      explicit TrackPlotter(const edm::ParameterSet&);
      ~TrackPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      TH2D* track_en_;
      TH2D* track_mp_;

      TH1D* pt_tot_;
      TH1D* tracks_;
      TH1D* vertices_;

      edm::InputTag vertexSrc_;
};

TrackPlotter::TrackPlotter(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   BasePlotter(config),
   vertexSrc_(config.getParameter<edm::InputTag>("vertexSrc"))
{
   edm::Service<TFileService> fs;
   track_en_ = fs->make<TH2D>("track_en", "Pt of tracks;#eta;#phi;p_{T} [GeV]",
         40, -3.2, 3.2, 40, -3.2, 3.2);
   track_mp_ = fs->make<TH2D>("track_mp", "Multiplicity of tracks",
         40, -3.2, 3.2, 40, -3.2, 3.2);

   pt_tot_ = fs->make<TH1D>("pt_tot", "#sum p_{T} per event;#sum p_{T} [GeV]",
         150, 0., 1500.);
   tracks_ = fs->make<TH1D>("tracks", "# of tracks;n_{tracks}", 300, 0, 300);
   vertices_ = fs->make<TH1D>("vertices", "# of vertices;n_{vertices}", 100, 0, 100);
}

TrackPlotter::~TrackPlotter() {}

void
TrackPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   edm::Handle< std::vector<reco::Vertex> > vertex_h;
   event.getByLabel(vertexSrc_, vertex_h);

   if (!vertex_h.isValid()) {
      edm::LogError("TrackPlotter") << "No valid vertices!" << std::endl;
      return;
   }

   double weight = this->weight(event);
   double n_vertices = double(vertex_h->size());

   // TODO why ref/pointer?
   const reco::Vertex *vert = &(vertex_h->front());
   double n_tracks = vert->tracksSize();

   double pt_tot = 0.;
   reco::Vertex::trackRef_iterator its;
   for (its = vert->tracks_begin(); its != vert->tracks_end(); ++its) {
      pt_tot += (*its)->pt();

      // Cut out small p_t
      if ((*its)->pt() < .5)
         continue;

      track_en_->Fill(
            double((*its)->eta()),
            double((*its)->phi()),
            double((*its)->pt()) * weight);
      track_mp_->Fill(
            double((*its)->eta()),
            double((*its)->phi()) * weight);
   }
   
   pt_tot_->Fill(pt_tot, weight);
   tracks_->Fill(n_tracks, weight);
   vertices_->Fill(n_vertices, weight);
}

void
TrackPlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
   //The following says we do not know what parameters are allowed so do no validation
   // Please change this to state exactly what you do use, even if it is no parameters
   edm::ParameterSetDescription desc;
   desc.setUnknown();
   descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(TrackPlotter);
