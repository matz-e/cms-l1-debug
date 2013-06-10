import FWCore.ParameterSet.Config as cms

caloTowerPlotter = cms.EDAnalyzer('CaloTowerPlotter',
        towers = cms.InputTag('towerMaker'),
        vertices = cms.InputTag('offlinePrimaryVertices'))
