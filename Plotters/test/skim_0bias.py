#!/usr/bin/env python
import FWCore.ParameterSet.Config as cms

process = cms.Process('0BiasSkim')

process.load('FWCore.MessageLogger.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

import HLTrigger.HLTfilters.triggerResultsFilter_cfi as hlt
process.ZeroBiasAve = hlt.triggerResultsFilter.clone()
process.ZeroBiasAve.triggerConditions = cms.vstring('HLT_ZeroBias*',)
process.ZeroBiasAve.hltResults = cms.InputTag( "TriggerResults", "", "HLT" )
process.ZeroBiasAve.l1tResults = cms.InputTag( "" )
process.ZeroBiasAve.throw = cms.bool( True )
process.zerobias = cms.Path(process.ZeroBiasAve)

process.writeout = cms.OutputModule("PoolOutputModule",
        fileName = cms.untracked.string("skim_0bias.root"),
        SelectEvents = cms.untracked.PSet(
            SelectEvents = cms.vstring('zerobias')),
        outputCommands = cms.untracked.vstring('keep *'))
process.end = cms.EndPath(process.writeout)

process.schedule = cms.Schedule(process.zerobias, process.end)

process.source = cms.Source('PoolSource',
        fileNames = cms.untracked.vstring([
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/FA21A724-1F84-E111-AD0E-003048F117EC.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/E2EE4DF0-1F84-E111-9D44-003048678098.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/E2E0D8F0-1A84-E111-B1EE-001D09F29533.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/D4740890-2084-E111-8308-003048F1110E.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/D0D8F3EF-1A84-E111-B0BD-0025901D5D80.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/BCEE680D-1D84-E111-847D-001D09F2983F.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/84045B31-1A84-E111-AC34-0025901D5D7E.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/7E40460D-1D84-E111-92DF-001D09F248F8.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/7AE014A4-1B84-E111-9C67-001D09F24D67.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/723F2223-1F84-E111-AC78-001D09F244DE.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/6A5CA57C-1984-E111-BC41-5404A640A642.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/3C205156-1C84-E111-B409-003048F0258C.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/3640F577-1E84-E111-B65F-001D09F34488.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/2E8A8AA3-1B84-E111-A8E8-0019B9F72CE5.root',
            '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/0C2158F6-2184-E111-9518-5404A63886A0.root'
            ]),
        lumisToProcess = cms.untracked.VLuminosityBlockRange(
                '190949:601-190949:700')) # end was: 1132'))
