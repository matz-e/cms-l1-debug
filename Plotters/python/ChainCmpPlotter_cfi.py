import FWCore.ParameterSet.Config as cms

chainCmpPlotter = cms.EDAnalyzer('ChainCmpPlotter',
        tpds = cms.InputTag('hcalDigis'),
        regions = cms.InputTag('gctDigis'),
        hits = cms.InputTag('hbhereco', ''),
        towers = cms.InputTag('towerMaker'))
