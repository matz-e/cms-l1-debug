import FWCore.ParameterSet.Config as cms

recHitTPPlotter = cms.EDAnalyzer('RecHitTPPlotter',
        hcalDigis = cms.InputTag('hcalDigis'),
        hcalHits = cms.InputTag('hbhereco', ''))

reducedRecHitTPPlotter = cms.EDAnalyzer('RecHitTPPlotter',
        hcalDigis = cms.InputTag('hcalDigis'),
        hcalHits = cms.InputTag('reducedHcalRecHits', 'hbhereco'))
