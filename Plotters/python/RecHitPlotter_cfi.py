import FWCore.ParameterSet.Config as cms

recHitPlotter = cms.EDAnalyzer('RecHitPlotter',
        ecalHits = cms.VInputTag(
            ('ecalRecHit', 'EcalRecHitsEB'),
            ('ecalRecHit', 'EcalRecHitsEE')),
        hcalHits = cms.InputTag('hbhereco', ''))

reducedRecHitPlotter = cms.EDAnalyzer('RecHitPlotter',
        ecalHits = cms.VInputTag(
            ('reducedEcalRecHitsEB', ''),
            ('reducedEcalRecHitsEE', '')),
        hcalHits = cms.InputTag('reducedHcalRecHits', 'hbhereco'))
