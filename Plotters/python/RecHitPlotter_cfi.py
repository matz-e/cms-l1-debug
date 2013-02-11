import FWCore.ParameterSet.Config as cms

recHitPlotter = cms.EDAnalyzer('RecHitPlotter',
        vertices = cms.InputTag('offlinePrimaryVertices'),
        ecalHits = cms.VInputTag(
            cms.InputTag('ecalRecHit', 'EcalRecHitsEB'),
            cms.InputTag('ecalRecHit', 'EcalRecHitsEE')),
        hcalHits = cms.VInputTag(
            cms.InputTag('hbhereco', ''),
            cms.InputTag('hfreco', '')))

reducedRecHitPlotter = cms.EDAnalyzer('RecHitPlotter',
        vertices = cms.InputTag('offlinePrimaryVertices'),
        ecalHits = cms.VInputTag(
            cms.InputTag('reducedEcalRecHitsEB', ''),
            cms.InputTag('reducedEcalRecHitsEE', '')),
        hcalHits = cms.VInputTag(
            cms.InputTag('reducedHcalRecHits', 'hbhereco'),
            cms.InputTag('reducedHcalRecHits', 'hfreco')))
