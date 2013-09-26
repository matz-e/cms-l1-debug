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
runera = ''

do_reco = False
use_ecal = True
use_hcal = True
tpd_thres = 0.5
time_thres = -1.

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
trainback = False
trainfront = False
cleanhcal = False

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
        sys.stderr.write("Unknown argument '%s'!\n" % (k,))
        sys.exit(1)
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

def insert_before(sequence, module, reference):
    """Insert a module in front of a reference one, recursively digging
    into sequences.  Hackish, as CMSSW does not seem to offer such a
    function (or documentation thereof)."""
    try:
        idx = sequence.index(reference)
        sequence.insert(idx, module)
    except ValueError:
        for item in sequence._seq._collection:
            if isinstance(item, cms.Sequence):
                if insert_before(item, module, reference):
                    return

import FWCore.ParameterSet.Config as cms

process = cms.Process('PlotPrep')
process.load('FWCore.MessageLogger.MessageLogger_cfi')
if do_reco:
    process.MessageLogger.cerr.FwkReport.reportEvery = 1
else:
    process.MessageLogger.cerr.FwkReport.reportEvery = 100
# process.MessageLogger.categories.append('L1GtTrigReport')

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(n))

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.connect   = 'frontier://FrontierProd/CMS_COND_31X_GLOBALTAG'
process.GlobalTag.pfnPrefix = cms.untracked.string('frontier://FrontierProd/')

from Configuration.AlCa.GlobalTag import GlobalTag as alcaGlobalTag
from Configuration.AlCa.autoCond import conditions_L1_Run2012D as l1cond_raw

l1cond = dict([((r, None), (t, c)) for (t, r, c) in map(lambda s: s.split(","), l1cond_raw)])
tag = "GR_R_53_V21::All" if data else "START53_V20::All"
process.GlobalTag = alcaGlobalTag(process.GlobalTag,
        globaltag=tag, conditions=l1cond)

if mc:
    process.GlobalTag.toGet = cms.VPSet(
            cms.PSet(record=cms.string("L1GctChannelMaskRcd"),
                     tag=cms.string("L1GctChannelMask_AllEnergySumsMaskedFromHF_jetCentresToEta3Allowed_mc"),
                     connect=cms.untracked.string("frontier://FrontierProd/CMS_COND_31X_L1T")),
            cms.PSet(record=cms.string("L1GctJetFinderParamsRcd"),
                     tag=cms.string("L1GctJetFinderParams_GCTPhysics_2012_04_27_JetSeedThresh5GeV_mc"),
                     connect=cms.untracked.string("frontier://FrontierProd/CMS_COND_31X_L1T")),
            cms.PSet(record=cms.string("L1HfRingEtScaleRcd"),
                     tag=cms.string("L1HfRingEtScale_GCTPhysics_2012_04_27_JetSeedThresh5GeV_mc"),
                     connect=cms.untracked.string("frontier://FrontierProd/CMS_COND_31X_L1T")),
            cms.PSet(record=cms.string("L1JetEtScaleRcd"),
                     tag=cms.string("L1JetEtScale_GCTPhysics_2012_04_27_JetSeedThresh5GeV_mc"),
                     connect=cms.untracked.string("frontier://FrontierProd/CMS_COND_31X_L1T")),
            cms.PSet(record=cms.string("L1HtMissScaleRcd"),
                     tag=cms.string("L1HtMissScale_GCTPhysics_2012_04_27_JetSeedThresh5GeV_mc"),
                     connect=cms.untracked.string("frontier://FrontierProd/CMS_COND_31X_L1T"))
            )

# process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
# process.load('Configuration.StandardSequences.MagneticField_cff')

process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.GeometryExtended_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Services_cff')

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

if data and trainback:
    process.level1Pattern = cms.EDFilter('HLTLevel1Pattern',
            L1GtReadoutRecordTag = cms.InputTag('gtDigis'),
            triggerBit = cms.string('L1Tech_BPTX_plus_AND_minus.v0'),
            daqPartitions = cms.uint32(1),
            ignoreL1Mask = cms.bool(True),
            invert = cms.bool(False),
            throw = cms.bool(True),
            bunchCrossings = cms.vint32( -2, -1,  0,  1,  2 ),
            triggerPattern = cms.vint32(  1,  0,  1,  0,  0 ))
    process.p *= process.level1Pattern

if data and trainfront:
    process.level1Pattern = cms.EDFilter('HLTLevel1Pattern',
            L1GtReadoutRecordTag = cms.InputTag('gtDigis'),
            triggerBit = cms.string('L1Tech_BPTX_plus_AND_minus.v0'),
            daqPartitions = cms.uint32(1),
            ignoreL1Mask = cms.bool(True),
            invert = cms.bool(False),
            throw = cms.bool(True),
            bunchCrossings = cms.vint32( -2, -1,  0,  1,  2 ),
            triggerPattern = cms.vint32(  0,  0,  1,  0,  1 ))
    process.p *= process.level1Pattern

if zerobias:
    process.load('HLTrigger.HLTfilters.hltHighLevel_cfi')
    process.hltHighLevel.HLTPaths = cms.vstring("HLT_ZeroBias_v*")
    process.p *= process.hltHighLevel

if minbias:
    # only for LP_MinBias samples!
    process.load('HLTrigger.HLTfilters.hltHighLevel_cfi')
    process.hltHighLevel.HLTPaths = cms.vstring("HLT_L1Tech53_MB_2_v*")
    process.p *= process.hltHighLevel

if reco:
    process.load('CommonTools.RecoAlgos.HBHENoiseFilter_cfi')
    process.load('RecoMET.METFilters.eeBadScFilter_cfi')
    process.pvfilter = cms.EDFilter("GoodVertexFilter",
            vertexCollection = cms.InputTag('offlinePrimaryVertices'),
            minimumNDOF = cms.uint32(4),
            maxAbsZ = cms.double(24),
            maxd0 = cms.double(2))
    process.p *= \
            process.pvfilter * \
            process.HBHENoiseFilter * \
            process.eeBadScFilter

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

process.load('Debug.Plotters.ChainCmpPlotter_cfi')

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

    process.q = cms.Path()
    process.q *= process.HLTL1UnpackerSequence \
            * process.l1extraParticles \
            * process.l1GtUnpack 

    if not use_ecal:
        process.rctReEmulDigis.useEcal = cms.bool(False)
    if not use_hcal:
        process.rctReEmulDigis.useHcal = cms.bool(False)
    if cleanhcal:
        process.load('Debug.Plotters.HcalTrigPrimDigiCleaner_cfi')
        process.hcalTPDCleaner.input = cms.InputTag("hcalReEmulDigis")
        process.hcalTPDCleaner.threshold = cms.untracked.double(tpd_thres)
        process.rctReEmulDigis.hcalDigis = cms.VInputTag(cms.InputTag('hcalTPDCleaner', ''))

        insert_before(process.HLTL1UnpackerSequence,
                process.hcalTPDCleaner, process.rctReEmulDigis)

        process.chainCmpPlotter.cut = cms.untracked.double(tpd_thres)

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
process.load('Debug.Plotters.GenEnergyPlotter_cfi')
process.load('Debug.Plotters.L1GctPlotter_cfi')
process.load('Debug.Plotters.L1JetPlotter_cfi')
process.load('Debug.Plotters.L1TriggerPlotter_cfi')
process.load('Debug.Plotters.PileUpPlotter_cfi')
process.load('Debug.Plotters.RecHitPlotter_cfi')
process.load('Debug.Plotters.TrackPlotter_cfi')
process.load('Debug.Plotters.TriggerPrimitiveDigiPlotter_cfi')
process.load('Debug.Plotters.TriggerPrimitiveDigiCmpPlotter_cfi')

if sim:
    process.triggerPrimitiveDigiCmpPlotter.hcalDigis = cms.InputTag(
            'simHcalTriggerPrimitiveDigis', '')

process.jetPlotter.l1Jets = cms.untracked.string('l1extraParticles')

if raw and reco:
    process.digiPlotter.useVertices = cms.untracked.bool(True)

process.caloTowerPlotter01 = process.caloTowerPlotter.clone()
process.caloTowerPlotter01.cut = cms.untracked.double(1.)

if time_thres > 0:
    process.chainCmpPlotter.timecut = cms.untracked.double(time_thres)
    process.recHitPlotter.timecut = cms.untracked.double(time_thres)

process.recHitPlotter01 = process.recHitPlotter.clone()
process.recHitPlotter01.cut = cms.untracked.double(1.0)

process.chainCmpPlotter01 = process.chainCmpPlotter.clone()
process.chainCmpPlotter01.cut = cms.untracked.double(1.0)

if cleanhcal:
    process.cleanTrigPrimPlotter = process.triggerPrimitiveDigiPlotter.clone()
    process.cleanTrigPrimPlotter.ecalDigis = cms.InputTag('ecalDigis', 'EcalTriggerPrimitives')
    process.cleanTrigPrimPlotter.hcalDigis = cms.InputTag('hcalTPDCleaner', '')
    process.p *= process.cleanTrigPrimPlotter

process.reEmulTrigPrimPlotter = process.triggerPrimitiveDigiPlotter.clone()
process.reEmulTrigPrimPlotter.ecalDigis = cms.InputTag('ecalDigis', 'EcalTriggerPrimitives')
process.reEmulTrigPrimPlotter.hcalDigis = cms.InputTag('hcalReEmulDigis', '')

process.reEmulCaloRegionPlotter = process.caloRegionPlotter.clone()
process.reEmulCaloRegionPlotter.caloRegions = cms.InputTag('rctReEmulDigis')

process.reEmulGctPlotter = process.gctPlotter.clone()
process.reEmulGctPlotter.l1GctSums = cms.InputTag('gctReEmulDigis')

process.reEmulTrigPlotter = process.trigPlotter.clone()
process.reEmulTrigPlotter.l1Bits = cms.InputTag('simGtDigis')

process.reEmulChainCmpPlotter = process.chainCmpPlotter.clone()
process.reEmulChainCmpPlotter.tpds = cms.InputTag('hcalReEmulDigis')
process.reEmulChainCmpPlotter.regions = cms.InputTag('rctReEmulDigis')

process.reEmulChainCmpPlotter01 = process.chainCmpPlotter01.clone()
process.reEmulChainCmpPlotter01.tpds = cms.InputTag('hcalReEmulDigis')
process.reEmulChainCmpPlotter01.regions = cms.InputTag('rctReEmulDigis')
process.reEmulChainCmpPlotter01.debug = cms.untracked.bool(True)

process.triggerPrimitiveDigiPlotter.ecalDigis = cms.InputTag(
        'ecalDigis', 'EcalTriggerPrimitives')
# always need to reemulate MC, since TPs are not in RAW
if mc:
    process.triggerPrimitiveDigiPlotter.hcalDigis = cms.InputTag(
            'hcalReEmulDigis', '')

# Plotter path assembly
# =====================

if raw or reco:
    process.p *= \
            process.gctPlotter * \
            process.trigPlotter
if raw:
    process.p *= \
            process.digiPlotter * \
            process.triggerPrimitiveDigiPlotter * \
            process.caloRegionPlotter
if raw and reemul:
    process.p *= \
            process.caloRegionCmpPlotter * \
            process.reEmulTrigPrimPlotter * \
            process.reEmulCaloRegionPlotter * \
            process.reEmulGctPlotter * \
            process.reEmulTrigPlotter * \
            process.triggerPrimitiveDigiCmpPlotter

if reco or do_reco:
    process.p *= \
            process.caloTowerPlotter * \
            process.caloTowerPlotter01 * \
            process.trackPlotter * \
            process.recHitPlotter * \
            process.recHitPlotter01

if (raw and reco) or do_reco:
    process.p *= process.chainCmpPlotter
    process.p *= process.chainCmpPlotter01

    if reemul:
        process.p *= process.reEmulChainCmpPlotter
        process.p *= process.reEmulChainCmpPlotter01

if mc:
    process.p *= process.genEnergyPlotter

class CreateTransverse:
    def __init__(self):
        self.transverse = []
    def enter(self, m):
        if 'rechitplotter' not in m.label().lower():
            return
        tr = m.clone()
        tr_label = m.label()
        tr_label = 'transverse' + tr_label[0].upper() + tr_label[1:]
        tr.setLabel(tr_label)
        tr.transverse = cms.untracked.bool(True)
        self.transverse.append(tr)
    def leave(self, m):
        pass

visitor = CreateTransverse()
process.p.visit(visitor)
for m in visitor.transverse:
    process.__setattr__(m.label(), m)
    process.p *= m

if mc:
    process.p *= process.pileUpPlotter

    if wfile != 'please set me':
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
    if ifile.endswith(".root"):
        if not ifile.startswith("/store/"):
            ifile = 'file:' + ifile
        process.source = cms.Source('PoolSource',
                fileNames = cms.untracked.vstring(ifile))
    else:
        process.source = cms.Source('PoolSource',
                fileNames = cms.untracked.vstring(
                    map(str.strip, open(ifile).readlines())))
else:
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([]))

if debug:
    print process.dumpPython()
