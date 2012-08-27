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

#include "TH2D.h"
#include "TNtuple.h"

//
// class declaration
//

class TrackPlotter : public edm::EDAnalyzer {
   public:
      explicit TrackPlotter(const edm::ParameterSet&);
      ~TrackPlotter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      template<typename THit, typename TDetId>
      std::pair<double, double> process_calo(const edm::Event&, const
            char*, const char*, TH2D*, TH2D*);

      // ----------member data ---------------------------
      TH2D* track_en_;
      TH2D* track_mp_;

      TNtuple* event_details_;

      edm::InputTag vertexSrc_;
};

TrackPlotter::TrackPlotter(const edm::ParameterSet& iConfig) :
   edm::EDAnalyzer(),
   vertexSrc_(iConfig.getParameter<edm::InputTag>("vertexSrc"))
{
   edm::Service<TFileService> fs;
   track_en_ = fs->make<TH2D>("track_en", "Pt of tracks",
         40, -3.2, 3.2, 40, -3.2, 3.2);
   track_mp_ = fs->make<TH2D>("track_mp", "Multiplicity of tracks",
         40, -3.2, 3.2, 40, -3.2, 3.2);

   event_details_ = fs->make<TNtuple>("event_detail", "",
         "n_vert:n_track:pt_tot");
}

TrackPlotter::~TrackPlotter() {}

void
TrackPlotter::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   double n_vertices = 0., n_tracks = 0., pt_tot = 0.;

   std::pair<double, double> p_ecal, p_ecal_red, p_hcal, p_hcal_red;

   edm::Handle< std::vector<reco::Vertex> > vertex_h;
   event.getByLabel(vertexSrc_, vertex_h);

   if (!vertex_h.isValid()) {
      edm::LogError("TrackPlotter") << "No valid vertices!" << std::endl;
      return;
   }

   n_vertices = double(vertex_h->size());

   // TODO why ref/pointer?
   const reco::Vertex *vert = &(vertex_h->front());
   n_tracks = vert->tracksSize();

   reco::Vertex::trackRef_iterator its;
   for (its = vert->tracks_begin(); its != vert->tracks_end(); ++its) {
      pt_tot += (*its)->pt();

      // Cut out small p_t
      if ((*its)->pt() < .5)
         continue;

      track_en_->Fill(
            double((*its)->eta()),
            double((*its)->phi()),
            double((*its)->pt()));
      track_mp_->Fill(
            double((*its)->eta()),
            double((*its)->phi()));
   }
   
   event_details_->Fill(n_vertices, n_tracks, pt_tot);
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
