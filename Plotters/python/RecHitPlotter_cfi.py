import FWCore.ParameterSet.Config as cms

recHitPlotter = cms.EDAnalyzer('RecHitPlotter',
        ecalHits = cms.InputTag('ecalRecHit', 'EcalRecHitsEB'),
        hcalHits = cms.InputTag('hbhereco', ''))

reducedRecHitPlotter = cms.EDAnalyzer('RecHitPlotter',
        ecalHits = cms.InputTag('reducedEcalRecHitsEB', ''),
        hcalHits = cms.InputTag('reducedHcalRecHits', 'hbhereco'))
