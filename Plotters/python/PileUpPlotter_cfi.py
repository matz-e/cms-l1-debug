import FWCore.ParameterSet.Config as cms

pileUpPlotter = cms.EDAnalyzer('PileUpPlotter',
        PVT = cms.InputTag('addPileupInfo'))
