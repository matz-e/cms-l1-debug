import FWCore.ParameterSet.Config as cms

hcalTPDCleaner = cms.EDProducer('HcalTrigPrimDigiCleaner',
        input = cms.InputTag('hcalDigis'),
        threshold = cms.untracked.double(-666.))
