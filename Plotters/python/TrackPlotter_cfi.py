import FWCore.ParameterSet.Config as cms

trackPlotter = cms.EDAnalyzer('TrackPlotter',
        vertexSrc = cms.InputTag('offlinePrimaryVertices'))
