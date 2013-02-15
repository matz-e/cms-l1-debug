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

#include "DataFormats/TrackReco/interface/HitPattern.h"
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

      TH1D* chi2_;
      TH1D* dxy_;
      TH1D* dz_;
      TH1D* hits_pixel_;
      TH1D* hits_strip_;
      TH1D* pt_;
      TH1D* pt_tot_;
      TH1D* tracks_;
      TH1D* vertex_z_;
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

   chi2_ = fs->make<TH1D>("chi2", "#chi^{2} / ndof;#chi^{2} / ndof;Tracks",
         100, 0., 5.);
   dxy_ = fs->make<TH1D>("dxy", "WIP d_{xy} / #sigma(d_{xy});d_{xy} / #sigma(d_{xy});Tracks",
         250, 0., 25.);
   dz_ = fs->make<TH1D>("dz", "WIP d_{z} / #sigma(d_{z});d_{z} / #sigma(d_{z});Tracks",
         250, 0., 25.);
   hits_pixel_ = fs->make<TH1D>("hits_pixel", "Hits in the pixel tracker;Pixel hits;Tracks",
         11, -.5, 10.5);
   hits_strip_ = fs->make<TH1D>("hits_strip", "HIts in the strip tracker;Strip hits;Tracks",
         41, -.5, 40.5);
   pt_ = fs->make<TH1D>("pt", "p_{T} per track;p_{T} [GeV];Num",
         750, 0., 1500.);
   pt_tot_ = fs->make<TH1D>("pt_tot", "#sum p_{T} per event;#sum p_{T} [GeV];Num",
         750, 0., 1500.);
   vertex_z_ = fs->make<TH1D>("vertex_z", "WIP #delta z;#delta z;Num",
         80, -2.5, 2.5);

   tracks_ = fs->make<TH1D>("tracks", "# of tracks;n_{tracks};Num", 299, 1, 299);
   vertices_ = fs->make<TH1D>("vertices", "# of vertices;n_{vertices};Num", 100, 0, 100);
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
   double n_vertices = 0;

   for (const auto& v: *(vertex_h.product())) {
      if (v.ndof() < 5 || fabs(v.z()) > 24. || fabs(v.position().rho()) > 2.)
         continue;
      n_vertices += 1.;
   }

   // TODO why ref/pointer?
   const reco::Vertex *vert = &(vertex_h->front());
   double n_tracks = vert->tracksSize();

   double pt_tot = 0.;
   reco::Vertex::trackRef_iterator its;
   for (its = vert->tracks_begin(); its != vert->tracks_end(); ++its) {
      // Cut out small p_t
      if ((*its)->pt() < .5)
         continue;

      pt_tot += (*its)->pt();

      chi2_->Fill((*its)->normalizedChi2(), weight);

      dxy_->Fill((*its)->dxy() / (*its)->dxyError(), weight);
      dz_->Fill((*its)->dz() / (*its)->dzError(), weight);

      reco::HitPattern hits = (*its)->hitPattern();
      hits_pixel_->Fill(hits.numberOfValidPixelHits(), weight);
      hits_strip_->Fill(hits.numberOfValidStripHits(), weight);

      pt_->Fill((*its)->pt(), weight);
      vertex_z_->Fill((*its)->dz(), weight);

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
