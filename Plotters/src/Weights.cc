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
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "PhysicsTools/Utilities/interface/LumiReWeighting.h"

#include "TTree.h"

class Weights : public edm::EDAnalyzer
{
   public:
      explicit Weights(const edm::ParameterSet&);
      ~Weights();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      bool weigh_;
      edm::LumiReWeighting *lumiWeights_;
      edm::InputTag vertices_;
      TTree* tpl_;
      unsigned int id_;
      float weight_;
};

Weights::Weights(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   weigh_(config.getUntrackedParameter<bool>("weigh", false))
{
   try {
      vertices_ = config.getParameter<edm::InputTag>("reweighVertices");
   } catch (...) {
      vertices_ = edm::InputTag("offlinePrimaryVertices");
   }

   if (weigh_) {
      lumiWeights_ = new edm::LumiReWeighting(
            config.getUntrackedParameter<std::string>("weightFile", "weights.root"),
            config.getUntrackedParameter<std::string>("weightFile", "weights.root"),
            "mc", "data");
   }

   edm::Service<TFileService> fs;
   tpl_ = fs->make<TTree>("event_weights", "");
   tpl_->Branch("id", &id_);
   tpl_->Branch("w", &weight_);
}

Weights::~Weights() {
   if (weigh_)
      delete lumiWeights_;
}

void
Weights::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   id_ = event.id().event();
   weight_ = 1.;

   if (weigh_) {
      edm::Handle< std::vector<reco::Vertex> > vs;
      event.getByLabel(vertices_, vs);

      if (vs.isValid()) {
         weight_ = lumiWeights_->weight(float(vs->size()));
      } else {
         edm::LogError("BasePlotter") << "No valid collection found for '" << vertices_
            << "'" << std::endl;
      }
   }

   tpl_->Fill();
}

void
Weights::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
   //The following says we do not know what parameters are allowed so do no validation
   // Please change this to state exactly what you do use, even if it is no parameters
   edm::ParameterSetDescription desc;
   desc.setUnknown();
   descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(Weights);
