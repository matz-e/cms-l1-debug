#!/usr/bin/env python
# vim: foldmethod=marker foldlevel=0
import sys

"""
The parameters can be changed by adding commandline arguments of the form
::

    create_plots.py n=-1 pu=low

or ::

    create_plots.py n=-1:wfile=foo.root

The latter can be used to change parameters in crab.
"""

n = 1000
pu = '45'
data = False
debug = False

do_reco = False

alt = False # alternative dataset
aod = False
raw = True
reco = False
reemul = False
sim = False

# filters
onepv = False
minbias = False
zerobias = False

ifile = 'please set me'
ofile = 'please set me'
wfile = 'please set me'

# Argument parsing
# vvv

if len(sys.argv) > 1 and sys.argv[1].endswith('.py'):
    sys.argv.pop(0)
if len(sys.argv) == 2 and ':' in sys.argv[1]:
    argv = sys.argv[1].split(':')
else:
    argv = sys.argv[1:]

for arg in argv:
    (k, v) = map(str.strip, arg.split('=', 1))
    if k not in globals():
        raise "Unknown argument '%s'!" % (k,)
    if type(globals()[k]) == bool:
        globals()[k] = v.lower() in ('y', 'yes', 'true', 't', '1')
    else:
        globals()[k] = type(globals()[k])(v)

if ifile == 'please set me':
    ifile = None
if ofile == 'please set me':
    ofile = 'standalone_plots_{d}_{p}.root'.format(d='data' if data else 'mc', p=pu)

mc = not data
reemul = reemul or (mc and raw)

import FWCore.ParameterSet.Config as cms

process = cms.Process('PlotPrep')
process.load('FWCore.MessageLogger.MessageLogger_cfi')
if do_reco:
    process.MessageLogger.cerr.FwkReport.reportEvery = 1
else:
    process.MessageLogger.cerr.FwkReport.reportEvery = 100
process.MessageLogger.categories.append('L1GtTrigReport')

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(n))

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.connect   = 'frontier://FrontierProd/CMS_COND_31X_GLOBALTAG'
process.GlobalTag.pfnPrefix = cms.untracked.string('frontier://FrontierProd/')
if data:
    process.GlobalTag.globaltag = cms.string('GR_R_53_V18::All')
else:
    process.GlobalTag.globaltag = cms.string('START53_V15::All')

process.load('Configuration.StandardSequences.GeometryExtended_cff')
# process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
# process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
if mc:
    process.load('Configuration.StandardSequences.Reconstruction_cff')
else:
    process.load('Configuration.StandardSequences.Reconstruction_Data_cff')

if do_reco:
    process.GlobalTag.toGet = cms.VPSet(
            cms.PSet(record = cms.string('EcalSampleMaskRcd'),
                tag = cms.string('EcalSampleMask_offline'),
                # connect = cms.untracked.string('oracle://cms_orcoff_prep/CMS_COND_ECAL'),
                connect = cms.untracked.string('frontier://FrontierPrep/CMS_COND_ECAL'),
                )
            )
    process.GlobalTag.DBParameters.authenticationPath="/afs/cern.ch/cms/DB/conddb"
    process.ecalGlobalUncalibRecHit.kPoorRecoFlagEB = cms.bool(False)
    process.ecalGlobalUncalibRecHit.kPoorRecoFlagEE = cms.bool(False)

process.p = cms.Path() # for plots
process.q = cms.Path() # for reemulation

if zerobias:
    import HLTrigger.HLTfilters.triggerResultsFilter_cfi as hlt
    process.ZeroBiasAve = hlt.triggerResultsFilter.clone()
    process.ZeroBiasAve.triggerConditions = cms.vstring('HLT_ZeroBias*',)
    process.ZeroBiasAve.hltResults = cms.InputTag( "TriggerResults", "", "HLT" )
    process.ZeroBiasAve.l1tResults = cms.InputTag("")
    process.ZeroBiasAve.throw = cms.bool( False )
    process.p *= process.ZeroBiasAve

if minbias:
    process.tfilter = cms.EDFilter( "TriggerResultsFilter",
        # triggerConditions = cms.vstring( "L1Tech_BSC_minBias_threshold1" ),
        triggerConditions = cms.vstring( "L1Tech_BSC_minBias_OR" ),
        hltResults = cms.InputTag( "TriggerResults", "", "HLT" ),
        l1tResults = cms.InputTag( "gtDigis" ),
        l1tIgnoreMask = cms.bool( True ),
        l1techIgnorePrescales = cms.bool( True ),
        daqPartitions = cms.uint32( 1 ),
        throw = cms.bool( True ))
    process.p *= process.tfilter

if reco and pu == 'none' and onepv: 
    process.vfilter = cms.EDFilter("VertexCountFilter",
            src = cms.InputTag("offlinePrimaryVertices"),
            minNumber = cms.uint32(1),
            maxNumber = cms.uint32(1),
            filter = cms.bool(True))
    process.p *= process.vfilter

if data:
    process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
else:
    process.load('Configuration.StandardSequences.RawToDigi_cff')

if raw or do_reco:
    process.q *= process.RawToDigi

if raw and reemul:
    process.load('HLTrigger.Configuration.HLT_FULL_cff')
    process.load('Configuration.StandardSequences.SimL1Emulator_cff')
    process.load('EventFilter.L1GlobalTriggerRawToDigi.l1GtUnpack_cfi')

    import L1Trigger.Configuration.L1Trigger_custom
    process = L1Trigger.Configuration.L1Trigger_custom.customiseL1GtEmulatorFromRaw(process)
    process = L1Trigger.Configuration.L1Trigger_custom.customiseResetPrescalesAndMasks(process)

    import HLTrigger.Configuration.customizeHLTforL1Emulator
    process = HLTrigger.Configuration.customizeHLTforL1Emulator.switchToL1Emulator(
            process, False, 'minPt', 'minPt', False, True, False, True)
    process = HLTrigger.Configuration.customizeHLTforL1Emulator.switchToSimGtReEmulGctDigis(process)
    if mc:
        process.HcalTPGCoderULUT.LUTGenerationMode = cms.bool(True)

    # process.es_pool2 = cms.ESSource("PoolDBESSource",
            # process.CondDBSetup,
            # timetype = cms.string('runnumber'),
            # toGet = cms.VPSet( cms.PSet( record = cms.string('HcalL1TriggerObjectsRcd'),
                # tag = cms.string('L1TriggerObjects_testIdealHCALv2')),),
            # connect = cms.string('frontier://FrontierPrep/CMS_COND_HCAL'),
            # authenticationMethod = cms.untracked.uint32(0),)
    # process.es_prefer_es_pool2 = cms.ESPrefer( "PoolDBESSource", "es_pool2")

    process.load('L1Trigger.L1ExtraFromDigis.l1extraParticles_cff')
    # process.l1extraParticles.forwardJetSource = cms.InputTag('gctReEmulDigis', 'forJets')
    # process.l1extraParticles.centralJetSource = cms.InputTag('gctReEmulDigis', 'cenJets')
    # process.l1extraParticles.tauJetSource = cms.InputTag('gctReEmulDigis', 'tauJets')

    process.q *= process.l1extraParticles \
            * process.HLTL1UnpackerSequence \
            * process.l1GtUnpack 

if do_reco:
    process.q *= process.reconstruction

if debug:
    process.dump = cms.EDAnalyzer("EventContentAnalyzer")
    process.p *= process.dump

process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')

process.load('Debug.Plotters.CaloRegionPlotter_cfi')
process.load('Debug.Plotters.CaloTowerPlotter_cfi')
process.load('Debug.Plotters.CaloRegionCmpPlotter_cfi')
process.load('Debug.Plotters.DigiPlotter_cfi')
process.load('Debug.Plotters.L1GctPlotter_cfi')
process.load('Debug.Plotters.L1JetPlotter_cfi')
process.load('Debug.Plotters.PileUpPlotter_cfi')
process.load('Debug.Plotters.RecHitPlotter_cfi')
process.load('Debug.Plotters.RecHitTPPlotter_cfi')
process.load('Debug.Plotters.TrackPlotter_cfi')
process.load('Debug.Plotters.TriggerPrimitiveDigiPlotter_cfi')
process.load('Debug.Plotters.TriggerPrimitiveDigiCmpPlotter_cfi')

if sim:
    process.triggerPrimitiveDigiCmpPlotter.hcalDigis = cms.InputTag(
            'simHcalTriggerPrimitiveDigis', '')

process.jetPlotter.l1Jets = cms.untracked.string('l1extraParticles')

process.recHitPlotter00_5 = process.recHitPlotter.clone()
process.recHitPlotter00_5.cut = cms.untracked.double(0.5)

process.recHitPlotter01_0 = process.recHitPlotter.clone()
process.recHitPlotter01_0.cut = cms.untracked.double(1.0)

process.recHitPlotter02_0 = process.recHitPlotter.clone()
process.recHitPlotter02_0.cut = cms.untracked.double(2.0)

process.recHitPlotter05_0 = process.recHitPlotter.clone()
process.recHitPlotter05_0.cut = cms.untracked.double(5.0)

process.recHitPlotter10_0 = process.recHitPlotter.clone()
process.recHitPlotter10_0.cut = cms.untracked.double(10.0)

process.recHitPlotter20_0 = process.recHitPlotter.clone()
process.recHitPlotter20_0.cut = cms.untracked.double(20.0)

process.reEmulTrigPrimPlotter = process.triggerPrimitiveDigiPlotter.clone()
process.reEmulTrigPrimPlotter.ecalDigis = cms.InputTag('ecalDigis', 'EcalTriggerPrimitives')
process.reEmulTrigPrimPlotter.hcalDigis = cms.InputTag('hcalReEmulDigis', '')

process.reEmulCaloRegionPlotter = process.caloRegionPlotter.clone()
process.reEmulCaloRegionPlotter.caloRegions = cms.InputTag('rctReEmulDigis')

process.reEmulGctPlotter = process.gctPlotter.clone()
process.reEmulGctPlotter.l1GctSums = cms.InputTag('gctReEmulDigis')

process.reEmulJetPlotter = process.jetPlotter.clone()
process.reEmulJetPlotter.l1Jets = cms.untracked.string('hltL1extraParticles')

process.triggerPrimitiveDigiPlotter.ecalDigis = cms.InputTag(
        'ecalDigis', 'EcalTriggerPrimitives')
# always need to reemulate MC, since TPs are not in RAW
if mc:
    process.triggerPrimitiveDigiPlotter.hcalDigis = cms.InputTag(
            'hcalReEmulDigis', '')

# Plotter path assembly
# =====================

if raw:
    process.p *= \
            process.digiPlotter * \
            process.triggerPrimitiveDigiPlotter * \
            process.caloRegionPlotter * \
            process.gctPlotter * \
            process.jetPlotter
if raw and reemul:
    process.p *= \
            process.caloRegionCmpPlotter * \
            process.reEmulTrigPrimPlotter * \
            process.reEmulCaloRegionPlotter * \
            process.reEmulGctPlotter * \
            process.reEmulJetPlotter * \
            process.triggerPrimitiveDigiCmpPlotter

if reco or do_reco:
    process.p *= \
            process.caloTowerPlotter * \
            process.trackPlotter * \
            process.recHitPlotter * \
            process.recHitPlotter00_5 * \
            process.recHitPlotter01_0 * \
            process.recHitPlotter02_0 * \
            process.recHitPlotter05_0 * \
            process.recHitPlotter10_0 * \
            process.recHitPlotter20_0
if (raw and reco) or do_reco:
    process.p *= process.recHitTPPlotter

if mc:
    process.p *= process.pileUpPlotter

    import os.path
    if os.path.exists(wfile) and os.path.isfile(wfile):
        class CreateWeighted:
            def __init__(self):
                self.weighted = []
            def enter(self, m):
                rw = m.clone()
                rw_label = m.label()
                rw_label = 'reWeighted' + rw_label[0].upper() + rw_label[1:]
                rw.setLabel(rw_label)
                rw.weigh = cms.untracked.bool(True)
                rw.weightFile = cms.untracked.string(wfile)
                self.weighted.append(rw)
            def leave(self, m):
                pass

        visitor = CreateWeighted()
        process.p.visit(visitor)
        for m in visitor.weighted:
            process.__setattr__(m.label(), m)
            process.p *= m

process.load("L1Trigger.GlobalTriggerAnalyzer.l1GtTrigReport_cfi")
if reemul:
    process.l1GtTrigReport.L1GtRecordInputTag = "simGtDigis"
else:
    process.l1GtTrigReport.L1GtRecordInputTag = "gtDigis"
process.l1GtTrigReport.PrintVerbosity = 1
process.p *= process.l1GtTrigReport

process.schedule = cms.Schedule(process.q, process.p)

process.TFileService = cms.Service("TFileService",
        closeFileFast = cms.untracked.bool(True),
        fileName = cms.string(ofile))

if ifile:
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([ifile]))
elif data and pu == 'none' and reco:
    # {{{
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                '/store/data/Run2012A/LP_MinBias2/RECO/PromptReco-v1/000/193/092/00A2F6F1-8895-E111-9ADD-0025901D5DB8.root',
                '/store/data/Run2012A/LP_MinBias2/RECO/PromptReco-v1/000/193/092/02762A56-9395-E111-AD5C-BCAEC532971D.root',
                '/store/data/Run2012A/LP_MinBias2/RECO/PromptReco-v1/000/193/092/02DA5B36-8C95-E111-A7CF-003048F117EA.root',
                '/store/data/Run2012A/LP_MinBias2/RECO/PromptReco-v1/000/193/092/049C146D-8D95-E111-ACC1-E0CB4E553673.root',
                '/store/data/Run2012A/LP_MinBias2/RECO/PromptReco-v1/000/193/092/00E7D27D-9095-E111-B172-0025B324400C.root',
                '/store/data/Run2012A/LP_MinBias2/RECO/PromptReco-v1/000/193/092/FADC4784-8E95-E111-A845-002481E0D90C.root',
                '/store/data/Run2012A/LP_MinBias2/RECO/PromptReco-v1/000/193/092/FC0F5100-8E95-E111-8760-001D09F2305C.root',
                '/store/data/Run2012A/LP_MinBias2/RECO/PromptReco-v1/000/193/092/F4862BD6-8C95-E111-8EBE-5404A640A63D.root',
                '/store/data/Run2012A/LP_MinBias2/RECO/PromptReco-v1/000/193/092/FA1AF863-8995-E111-8EE8-BCAEC5329702.root',
                '/store/data/Run2012A/LP_MinBias2/RECO/PromptReco-v1/000/193/092/FCD076A1-9295-E111-8EC7-001D09F295FB.root',
                '/store/data/Run2012A/LP_MinBias1/RECO/PromptReco-v1/000/193/092/BE6E717E-8D95-E111-A969-BCAEC518FF76.root',
                '/store/data/Run2012A/LP_MinBias1/RECO/PromptReco-v1/000/193/092/C2BB0FF9-9195-E111-92F3-485B3977172C.root',
                '/store/data/Run2012A/LP_MinBias1/RECO/PromptReco-v1/000/193/092/C216AE13-8895-E111-80B5-5404A640A642.root',
                '/store/data/Run2012A/LP_MinBias1/RECO/PromptReco-v1/000/193/092/CAE5DBD7-8C95-E111-8F2A-5404A63886C1.root',
                '/store/data/Run2012A/LP_MinBias1/RECO/PromptReco-v1/000/193/092/C2684086-9095-E111-9035-003048D2C174.root',
                '/store/data/Run2012A/LP_MinBias1/RECO/PromptReco-v1/000/193/092/C6BE23A6-9295-E111-91CD-003048F024DA.root',
                '/store/data/Run2012A/LP_MinBias1/RECO/PromptReco-v1/000/193/092/CE6A0D88-9095-E111-BAFA-001D09F2424A.root',
                '/store/data/Run2012A/LP_MinBias1/RECO/PromptReco-v1/000/193/092/D036380A-8995-E111-A0F4-003048F1183E.root',
                '/store/data/Run2012A/LP_MinBias1/RECO/PromptReco-v1/000/193/092/D2DF5184-9095-E111-A262-001D09F2B30B.root',
                '/store/data/Run2012A/LP_MinBias1/RECO/PromptReco-v1/000/193/092/D40DAE09-8E95-E111-AFBE-BCAEC53296F7.root',
                ]))
    # }}}
elif data and pu == 'none' and raw:
    # {{{
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/008C8CA6-D393-E111-88CC-BCAEC518FF8D.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/042553EC-DE93-E111-AFEF-485B3962633D.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/027F4095-F093-E111-B803-003048D37560.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/063BDDC1-D593-E111-A517-002481E0D7C0.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/06016C53-E593-E111-BF2D-5404A63886C6.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/0A643421-E393-E111-96C1-002481E94C7E.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/06B635CC-E893-E111-9A5C-001D09F24353.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/10F0AB04-D393-E111-9902-002481E0D958.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/0AE2F80B-ED93-E111-8EEA-003048D2BC30.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/16F0EB74-D693-E111-83DE-BCAEC5329709.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/12372E91-E493-E111-A96C-5404A63886B9.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/18B5C504-D393-E111-A114-00237DDC5C24.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/18292EEF-DE93-E111-89FE-001D09F2910A.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/20CE1A8F-F093-E111-98DC-002481E0D73C.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/1E979DD9-E393-E111-ACFF-5404A63886A2.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/2432439F-EB93-E111-8F6E-5404A63886BE.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/22499C71-E293-E111-BD3D-001D09F24D8A.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/2A2321E4-EF93-E111-B860-5404A63886A2.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/260E62C0-E193-E111-88DC-003048D3C944.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/2AB69BF4-E593-E111-A211-001D09F241B9.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/2A672ED6-E393-E111-A9AA-0025901D5DF4.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/2CB96675-D693-E111-A23D-001D09F253D4.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/2C7EAAC2-D593-E111-A5A3-001D09F248F8.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/34AD6696-F093-E111-8D0B-003048D2C0F0.root',
                '/store/data/Run2012A/LP_MinBias1/RAW/v1/000/193/092/308E2BFA-E593-E111-8FD6-003048D373F6.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/AED0D9EC-DE93-E111-BDE2-001D09F28EA3.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/B29F8AA6-D393-E111-88CC-BCAEC518FF8D.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/90BB0EDE-D793-E111-8026-003048D3C932.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/B6B6FC22-E393-E111-9D96-001D09F2960F.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/B80DA266-E793-E111-8A7A-001D09F2A49C.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/BC29DDAE-DA93-E111-B50F-001D09F2527B.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/C0DCAE38-D793-E111-92B7-001D09F2983F.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/C266BEF7-E593-E111-B8B2-002481E94C7E.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/A039C238-D793-E111-8354-0019B9F581C9.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/C459215C-D493-E111-A42A-BCAEC532971F.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/C483C304-D393-E111-A114-00237DDC5C24.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/C4A84513-E193-E111-92D8-BCAEC53296F8.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/A4B0B76C-E793-E111-AA11-0025B320384C.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/C6B24ACD-E893-E111-9EEE-001D09F2305C.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/C83A1C97-F093-E111-884A-001D09F241B9.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/CA193BA3-DF93-E111-8FB2-001D09F29114.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/AC2018A1-DF93-E111-80F8-001D09F276CF.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/CC8F71D7-E393-E111-A95E-003048D2BBF0.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/B2C9FEED-DE93-E111-8E05-001D09F2462D.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/D282002B-EF93-E111-96AF-003048D2BCA2.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/D47265A0-EB93-E111-ABDC-001D09F253D4.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/D68128A1-DF93-E111-8BD6-002481E0D958.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/D68FBFCC-DC93-E111-953E-001D09F2AD84.root',
                '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/D89CC874-D693-E111-810E-5404A63886B6.root',
            '/store/data/Run2012A/LP_MinBias2/RAW/v1/000/193/092/DA63B4CB-E893-E111-9038-001D09F295A1.root',
                ]))
    # }}}
elif mc and pu == 'none' and not alt and reco:
    # {{{
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/00FF600E-3E60-E211-83F7-0026189438AB.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/02B95F0B-4060-E211-8AB1-002618943908.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/06CC981F-4060-E211-8319-002618943972.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/082232C1-3E60-E211-9A18-00304867916E.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/08A876BE-3F60-E211-9040-002354EF3BDA.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/0AB349A1-4060-E211-B309-003048678B8E.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/0C854507-4260-E211-9319-003048679168.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/125FE0BA-4A60-E211-85CD-0025905964B2.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/1C38930A-3D60-E211-89FF-002618943916.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/22D59366-3D60-E211-97F4-00261894383F.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/24126F6E-3E60-E211-ACCD-0026189437E8.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/24E3A14F-4060-E211-B19C-00261894388F.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/265D8E50-4060-E211-BA99-0026189438FA.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/34D50998-4260-E211-9065-002590596486.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/36B3930A-3E60-E211-9A11-0026189438EB.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/3C6024B7-3E60-E211-BBB7-00261894383F.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/3CB21D11-3F60-E211-8D10-002618943829.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/3E6DDA03-4660-E211-99C5-0025905964C2.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/3EE12D78-4160-E211-AC9E-003048678B14.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/RECODEBUG/EflowHpu_NoPileUp_START53_V7C-v1/10000/460FDC14-3E60-E211-8EDC-002618943967.root',
                ]))
    # }}}
elif mc and pu == 'none' and not alt and raw:
    # {{{
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/027A314A-925F-E211-8650-002354EF3BDA.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/02E342B2-915F-E211-B714-002354EF3BE0.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/005EA36A-915F-E211-A6CE-0026189438FC.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/00CFEC95-925F-E211-BC72-00261894397B.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/06F80846-925F-E211-8DB3-0026189438CB.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/00F11B64-915F-E211-9EDD-003048B95B30.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/0A3AA8F6-8D5F-E211-8E55-003048FFCB84.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/0A89A79E-925F-E211-85AD-003048FFD728.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/048605D8-905F-E211-9B34-0025905938A8.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/0C0FE6D4-905F-E211-9120-002354EF3BDB.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/0C47DF47-925F-E211-A959-002618943868.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/0CDEFED8-905F-E211-80EA-0026189438B5.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/0E566BCC-8E5F-E211-BB02-0026189438F6.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/06C32DB6-915F-E211-AF56-002618943854.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/08A9A695-925F-E211-88C8-00304867916E.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/0ACCCD3C-905F-E211-B5C0-002618943854.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/187B2C01-925F-E211-8204-002354EF3BE2.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/18880CB0-915F-E211-9928-0026189438C1.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/1A0CFCBA-935F-E211-B499-003048D3FC94.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/1AA5C866-915F-E211-8F54-003048678DA2.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/1AAB5C46-905F-E211-9562-00304867D446.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/0E823C44-925F-E211-AF56-002618943984.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/1087BBB4-915F-E211-8249-003048679168.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/1E745A99-905F-E211-B129-003048678FC4.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/141C66FF-8F5F-E211-A330-00261894389F.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/1ACEB946-925F-E211-BE87-0030486792AC.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/2211F5B1-915F-E211-92DC-002618943821.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/28210C69-8F5F-E211-BBE2-003048678ADA.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/2A0D49D8-905F-E211-B330-003048678F74.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/1C0141A8-925F-E211-805F-003048FFD752.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/2E1D0B18-8F5F-E211-BB06-002618FDA248.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/30368C21-8F5F-E211-8C21-003048678BC6.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/30FC936A-915F-E211-BA37-002618943913.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/2012E152-925F-E211-94D5-002618943856.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/32EBD793-925F-E211-AC8B-002618943829.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/38092F24-915F-E211-909F-002590596498.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/38462CB7-915F-E211-93A4-002354EF3BDB.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/3A595BB4-915F-E211-BB2F-00261894385A.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/3A7A7EB1-915F-E211-9D9D-00304867915A.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/3A9AEF51-925F-E211-AC9D-0026189438CC.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/3ADEEA1F-8F5F-E211-B470-00259059649C.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/3C07BF64-915F-E211-AE7B-00261894387B.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/3C0E075B-925F-E211-978D-002354EF3BE2.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/3C7CBDD3-905F-E211-B32E-0026189438FE.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/201327D6-905F-E211-AD4E-003048678AE4.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/2C986442-925F-E211-814F-003048678ADA.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/3CEE80AE-8F5F-E211-AE26-00304867903E.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/3CF52E4C-925F-E211-BEB0-003048679180.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/320CD819-915F-E211-BEDD-0026189438CB.root',
                '/store/mc/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM-RAW/EflowHpu_NoPileUp_START53_V7C-v1/10000/3C95B45F-905F-E211-8702-003048678F74.root',
                ]))
    # }}}
elif mc and pu == 'none' and alt and reco:
    # {{{
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/3C08C1F1-5065-E211-B3A6-003048678AE2.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/3A271A37-4F65-E211-A98A-003048678F9C.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/3A1544AB-4F65-E211-9B49-003048679248.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/38EC1D77-4D65-E211-AF4D-0025905964BA.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/344A2207-5065-E211-A27D-003048679296.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/30F9A918-3E65-E211-8246-0025905938A4.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/305CDDC5-4F65-E211-96C4-003048678FD6.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/2E9BA7A2-4865-E211-9858-0025905822B6.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/2E4969BE-4465-E211-8521-003048FF9AA6.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/2E45483C-4165-E211-B475-002590596486.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/2CC67A4E-4B65-E211-A5ED-0026189438A9.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/2CB28AA2-4B65-E211-B48F-0030486792B6.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/285351DB-4F65-E211-8466-002590593902.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/26ED9768-4D65-E211-B5FA-003048678BAE.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/242374A2-3565-E211-96AF-003048FFD736.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/22EC8AF0-4A65-E211-A62D-003048679084.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/224BE255-5265-E211-B639-002590593920.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/1CB683C7-3465-E211-97D2-003048FFD75C.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/1C9C9EB8-3D65-E211-8CE3-00259059649C.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/1C8A80EE-4165-E211-AC9A-003048FFD71A.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/1A4AE567-4165-E211-9217-002590593902.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/16ADE404-2365-E211-87F8-0025905964BE.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/165C6D22-5065-E211-98D6-00259059391E.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/16113393-5065-E211-B88D-00248C0BE012.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/12110058-5965-E211-B410-0026189438D5.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/10BC2D25-6065-E211-9298-002354EF3BDB.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0EA63E52-4E65-E211-A506-002618943807.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0AB9DA8B-4B65-E211-84D4-003048FF9AA6.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0A7FE46A-4C65-E211-8FA4-003048678AC0.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0A676389-3F65-E211-AF88-003048FFD730.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0A5B88AA-5065-E211-9465-0025905964C2.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/08B7C273-2065-E211-8652-0025905964C2.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/RECODEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0895C8E1-4B65-E211-82FA-003048FFD7BE.root',
                ]))
    # }}}
elif mc and pu == 'none' and alt and raw:
    # {{{
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/FEED0816-1961-E211-8FF5-00248C55CC97.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/00011113-F560-E211-A8A3-00259059391E.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0246EE0C-1D61-E211-80A7-0026189438D9.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/02D1A40C-FA60-E211-9CF8-003048FFD76E.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/000C6D77-1561-E211-9F77-003048FFD754.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/00815041-1161-E211-8362-003048FFCBA8.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/042F31C0-0E61-E211-AB6B-003048FFD754.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/043A7A0B-1A61-E211-ABF0-003048FFD752.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/04FE5529-2061-E211-B1E3-002590593872.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0209A169-0961-E211-80A4-0026189438BA.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/066E26BF-1561-E211-B162-0025905964C2.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/02E617D4-1861-E211-ADD3-00261894396F.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0809708B-0861-E211-8031-003048FFD71E.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0866AD66-1F61-E211-B82A-003048FFD7C2.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0A31E6A4-0361-E211-9400-002354EF3BE1.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0A5C75F6-1061-E211-957B-003048FF9AA6.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0C6B2B92-F960-E211-8A0F-003048FFCB74.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0C8B9AE2-1461-E211-9C38-003048FF86CA.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0CCC6426-FD60-E211-BE83-003048FFCB6A.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/04096F44-1861-E211-B08F-003048FFCBB0.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0EC41771-0561-E211-8BC8-003048FFD760.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0EF123A7-1D61-E211-8739-003048FFD760.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0635770D-1461-E211-93DF-003048FFD7D4.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0689B457-0B61-E211-8C46-003048FFD730.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/10C38753-F360-E211-BAC1-003048FF9AA6.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/10CE8884-1A61-E211-B38A-002354EF3BE1.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/0CE0F559-1F61-E211-A381-003048FFD720.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/146E20AB-F460-E211-AE94-0025905822B6.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/10137B93-0661-E211-ADE9-003048678FAE.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/161A7E5B-1F61-E211-AC94-003048FFD7A2.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/1654308C-1661-E211-AFDA-002618FDA28E.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/166D00DE-FE60-E211-A87F-0026189438BA.root',
                '/store/mc/Summer12/MB8TeVEtanoCasHFShoLib/GEN-SIM-RAWDEBUG/EflowHpu_NoPileUp_START53_V16-v1/10000/169F3808-1A61-E211-ABCD-002590596468.root',
                ]))
    # }}}
elif data and pu == 'low':
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                'file:skim_0bias.root'
                ]))
elif mc and pu == 'low':
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                'file:SingleNuPt10_Mix.root'
                ]))
elif data and pu == '45':
    # {{{
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/1EADEC56-1BCA-E111-9692-BCAEC518FF68.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/1E723C8C-1CCA-E111-AF5B-003048CF94A6.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/1C1D7655-1BCA-E111-8C36-001D09F23D1D.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/1AC963F9-1BCA-E111-A617-00215AEDFCCC.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/16D41F92-1ACA-E111-8B7F-0015C5FDE067.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/164A3155-1BCA-E111-B583-001D09F295A1.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/1483DC8C-1ACA-E111-B1AD-BCAEC53296F8.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/107B9052-1BCA-E111-BADB-001D09F248F8.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/100DFA8C-1CCA-E111-AD18-003048678098.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/0EEDFA91-1ACA-E111-A846-001D09F295A1.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/0E2AFE55-1BCA-E111-B902-001D09F2462D.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/0CE3DC51-1BCA-E111-861F-E0CB4E55365C.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/0ADC3E07-1CCA-E111-8666-001D09F2AF96.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/0A178602-1CCA-E111-82A7-001D09F248F8.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/08D703F9-1BCA-E111-912D-E0CB4E5536AE.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/083AB0B4-19CA-E111-9423-001D09F248F8.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/08184950-1BCA-E111-8575-001D09F2915A.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/04A01F55-1BCA-E111-8541-001D09F2905B.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/00EFBD57-1BCA-E111-81DD-003048D3733E.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/588/00D2FD57-1BCA-E111-8481-003048F118C6.root',
                ]))
            # lumisToProcess = cms.untracked.VLuminosityBlockRange(
                # '179828:179-179828:189', '179828:366-179828:366'
                # ))
    # }}}
elif data and pu == '66':
    # {{{
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/3C4A28B8-72CA-E111-827A-003048F118AA.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/3848706F-74CA-E111-AEAE-001D09F2527B.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/2AB1ACB6-72CA-E111-8361-5404A638869B.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/2AA64072-74CA-E111-BEE7-BCAEC518FF5F.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/26A74020-74CA-E111-9778-5404A63886B9.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/24CA1463-73CA-E111-A700-003048F11C28.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/2421D4B6-72CA-E111-B939-003048CFB40C.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/22E5C4B8-72CA-E111-894E-003048F11DE2.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/1CCDBF70-74CA-E111-8334-0025901D62A0.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/1A9A53BE-72CA-E111-B173-003048D2C0F4.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/18F82005-71CA-E111-AC70-001D09F34488.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/1467473D-75CA-E111-A572-003048F118C4.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/12C53B00-71CA-E111-9741-001D09F253C0.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/128B8EB8-72CA-E111-A703-BCAEC518FF40.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/102F8715-71CA-E111-A9EF-003048D2BC5C.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/0E2082FE-70CA-E111-AA9C-00215AEDFD98.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/0CC9AA6C-74CA-E111-B56E-BCAEC518FF52.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/0AB01403-71CA-E111-B705-003048F110BE.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/08361F06-71CA-E111-B50E-003048F1C424.root',
                '/store/data/Run2012C/ZeroBias1/RAW/v1/000/198/609/04F0C0E3-72CA-E111-A802-003048F117EC.root'
                ]))
            # lumisToProcess = cms.untracked.VLuminosityBlockRange(
                # '179828:179-179828:189', '179828:366-179828:366'
                # ))
    # }}}
elif mc and pu == '45':
    # {{{
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/04853736-9828-E211-A015-003048FFD756.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/047A94A7-9D28-E211-B894-00261894385A.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/046BCF99-A228-E211-A2A1-002618943985.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/0442A929-9E28-E211-BCF3-002618943875.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/0421DA70-E228-E211-BB68-001A92811716.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/04069C54-9E28-E211-92D6-0018F3D09600.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/04067F68-A228-E211-A597-00304867D836.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/02D5AB9A-9E28-E211-9071-00261894390C.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/029734EF-9F28-E211-86CF-002618943874.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/028BD335-9928-E211-BEB4-0026189438C2.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/02717B35-9D28-E211-B1A7-00261894386B.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/024B81D1-F328-E211-9CD3-00261894392D.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/023CB170-9828-E211-BC9D-003048FFCB8C.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/02286BDA-A128-E211-8B61-001A928116B2.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/0227ECE0-9D28-E211-8C62-00261894393A.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/0216B862-A228-E211-B280-002618943979.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/0214A21D-0429-E211-B4D2-001A92810AAA.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/00CB9FB5-A028-E211-A70D-001A928116E6.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/00A47645-9828-E211-9203-003048678C06.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU45_noOOT_START53_V7B-v2/00000/0046FAB4-9E28-E211-8A5C-003048678F74.root'
                ]))
    # }}}
elif mc and pu == '66':
    # {{{
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/049AECD1-9C27-E211-9AC5-001A92971B82.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/0417A36C-9C27-E211-8C0B-00304867903E.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/0401D3C0-9C27-E211-BDF9-001A92971B26.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/02FC9F05-9C27-E211-8FF3-002618943960.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/02D7BFBA-9B27-E211-A0B5-003048FFD728.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/02C699F1-9B27-E211-90C9-0026189438F7.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/027B7196-9C27-E211-82ED-001A92971B08.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/0276E95A-9C27-E211-9FF7-002618943908.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/027477F1-9C27-E211-9942-001A92810AB2.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/025505F6-9C27-E211-913F-001A92971BC8.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/023F74CB-9B27-E211-AFAD-002618943821.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/02257BED-9B27-E211-BA26-0026189437E8.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/021BDF6A-9C27-E211-BB75-003048678FF6.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/00DCDAE7-9B27-E211-BC28-002618943869.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/00AB1C9A-9C27-E211-AD73-001A92971B36.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/00814A55-9C27-E211-B5B6-001BFCDBD15E.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/00750835-9C27-E211-883B-002354EF3BDB.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/0041164C-9C27-E211-AA46-002618943982.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/0037F92C-9C27-E211-BF0E-002618943930.root',
                '/store/mc/Summer12_DR53X/Neutrino_Pt_2to20_gun/GEN-RAW/PU66_noOOT_START53_V7B-v2/00000/00124F6F-9C27-E211-A055-003048FFD732.root'
                ]))
    # }}}
else:
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([]))

if debug:
    print process.dumpPython()
