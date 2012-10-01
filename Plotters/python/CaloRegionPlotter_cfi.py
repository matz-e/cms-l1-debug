import FWCore.ParameterSet.Config as cms

caloRegionPlotter = cms.EDAnalyzer('CaloRegionPlotter',
        caloRegions = cms.InputTag('gctDigis'))
