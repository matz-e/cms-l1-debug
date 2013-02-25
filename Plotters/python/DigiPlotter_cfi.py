import FWCore.ParameterSet.Config as cms

digiPlotter = cms.EDAnalyzer('DigiPlotter',
        ecalDigis = cms.VInputTag(
            cms.InputTag('ecalDigis', 'ebDigis'),
            cms.InputTag('ecalDigis', 'eeDigis')),
        hcalDigis = cms.InputTag('hcalDigis'),
        vertices = cms.InputTag('offlinePrimaryVertices'))
