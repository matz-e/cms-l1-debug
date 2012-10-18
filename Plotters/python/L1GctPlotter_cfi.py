import FWCore.ParameterSet.Config as cms

gctPlotter = cms.EDAnalyzer('L1GctPlotter',
        l1GctSums = cms.InputTag('gctDigis'))
