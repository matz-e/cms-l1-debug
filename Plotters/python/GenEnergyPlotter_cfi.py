import FWCore.ParameterSet.Config as cms

genEnergyPlotter = cms.EDAnalyzer('GenEnergyPlotter',
        particles = cms.InputTag('genParticles'))
