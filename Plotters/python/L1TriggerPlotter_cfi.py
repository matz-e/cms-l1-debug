import FWCore.ParameterSet.Config as cms

trigPlotter = cms.EDAnalyzer('L1TriggerPlotter',
        l1Bits = cms.InputTag('gtDigis'))
