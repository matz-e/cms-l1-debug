import FWCore.ParameterSet.Config as cms

caloRegionCmpPlotter = cms.EDAnalyzer('CaloRegionCmpPlotter',
        caloRegions = cms.InputTag('gctDigis'),
        reEmulCaloRegions = cms.InputTag('rctReEmulDigis'))
