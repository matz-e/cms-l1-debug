import FWCore.ParameterSet.Config as cms

digiPlotter = cms.EDAnalyzer('DigiPlotter',
        ecalDigis = cms.InputTag('ecalDigis', 'ebDigis'),
        hcalDigis = cms.InputTag('hcalDigis'),
        vertices = cms.InputTag('offlinePrimaryVertices'))
