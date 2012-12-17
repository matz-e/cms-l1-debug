import FWCore.ParameterSet.Config as cms

triggerPrimitiveDigiCmpPlotter = cms.EDAnalyzer('TriggerPrimitiveDigiCmpPlotter',
        hcalDigis = cms.InputTag('hcalDigis', ''),
        hcalReEmulDigis = cms.InputTag('hcalReEmulDigis', ''))
