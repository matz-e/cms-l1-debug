#!/usr/bin/env python
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

aod = False
raw = True
reco = False
reemul = False
sim = False

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
    (k, v) = map(str.strip, arg.split('='))
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

if data:
    process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
else:
    process.load('Configuration.StandardSequences.RawToDigi_cff')

process.p = cms.Path()

if reco and pu == 'none': 
    process.vfilter = cms.EDFilter("VertexCountFilter",
            src = cms.InputTag("offlinePrimaryVertices"),
            minNumber = cms.uint32(1),
            maxNumber = cms.uint32(1),
            filter = cms.bool(True))
    process.p *= process.vfilter

if raw or do_reco:
    process.p *= process.RawToDigi

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

    process.p *= process.HLT1UnpackerSequence \
            * process.l1GtUnpack \
            * process.l1extraParticles

if debug:
    process.dump = cms.EDAnalyzer("EventContentAnalyzer")
    process.p *= process.dump

if do_reco:
    process.p *= process.reconstruction

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

process.recHitPlotter02 = process.recHitPlotter.clone()
process.recHitPlotter02.cut = cms.untracked.double(2.0)

process.recHitPlotter05 = process.recHitPlotter.clone()
process.recHitPlotter05.cut = cms.untracked.double(5.0)

process.recHitPlotter10 = process.recHitPlotter.clone()
process.recHitPlotter10.cut = cms.untracked.double(10.0)

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
            process.recHitPlotter02 * \
            process.recHitPlotter05 * \
            process.recHitPlotter10
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

if raw:
    process.load("L1Trigger.GlobalTriggerAnalyzer.l1GtTrigReport_cfi")
    if reemul:
        process.l1GtTrigReport.L1GtRecordInputTag = "simGtDigis"
    else:
        process.l1GtTrigReport.L1GtRecordInputTag = "gtDigis"
    process.l1GtTrigReport.PrintVerbosity = 1
    process.p *= process.l1GtTrigReport

process.TFileService = cms.Service("TFileService",
        closeFileFast = cms.untracked.bool(True),
        fileName = cms.string(ofile))

if ifile:
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([ifile]))
elif data and pu == 'none':
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
elif mc and pu == 'none':
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
elif data and pu == '66':
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
elif mc and pu == '45':
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
elif mc and pu == '66':
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

if debug:
    print process.dumpPython()
