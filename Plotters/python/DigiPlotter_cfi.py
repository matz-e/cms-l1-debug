import FWCore.ParameterSet.Config as cms

digiPlotter = cms.EDAnalyzer('DigiPlotter',
        ecalDigis = cms.InputTag('ecalDigis'),
        hcalDigis = cms.InputTag('hcalDigis'))
