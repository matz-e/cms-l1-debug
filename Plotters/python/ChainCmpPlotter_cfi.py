import FWCore.ParameterSet.Config as cms

chainCmpPlotter = cms.EDAnalyzer('ChainCmpPlotter',
        regions = cms.InputTag('gctDigis'),
        hits = cms.InputTag('hbhereco', ''),
        towers = cms.InputTag('towerMaker'))
