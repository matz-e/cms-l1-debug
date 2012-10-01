import FWCore.ParameterSet.Config as cms

weights = cms.EDAnalyzer('Weights',
        weigh = cms.untracked.bool(True))
