import FWCore.ParameterSet.Config as cms

triggerPrimitiveDigiPlotter = cms.EDAnalyzer('TriggerPrimitiveDigiPlotter',
        ecalDigis = cms.InputTag('ecalDigis'),
        hcalDigis = cms.InputTag('hcalDigis'))
