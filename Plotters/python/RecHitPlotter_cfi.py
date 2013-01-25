import FWCore.ParameterSet.Config as cms

recHitPlotter = cms.EDAnalyzer('RecHitPlotter',
        ecalHits = cms.VInputTag(
            cms.InputTag('ecalRecHit', 'EcalRecHitsEB'),
            cms.InputTag('ecalRecHit', 'EcalRecHitsEE')),
        hcalHits = cms.InputTag('hbhereco', ''))

reducedRecHitPlotter = cms.EDAnalyzer('RecHitPlotter',
        ecalHits = cms.VInputTag(
            cms.InputTag('reducedEcalRecHitsEB', ''),
            cms.InputTag('reducedEcalRecHitsEE', '')),
        hcalHits = cms.InputTag('reducedHcalRecHits', 'hbhereco'))
