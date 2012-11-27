import FWCore.ParameterSet.Config as cms

jetPlotter = cms.EDAnalyzer('L1JetPlotter',
        l1Jets = cms.untracked.string('hltL1extraParticles'))
