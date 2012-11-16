import sys

data = False

aod = False
raw = True
reco = False
reemul = False

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
    globals()[k] = v.lower() in ('y', 'yes', 'true', 't', '1')

mc = not data
reemul = reemul or (mc and raw)

import FWCore.ParameterSet.Config as cms

process = cms.Process('PlotPrep')
process.load('FWCore.MessageLogger.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 100
process.MessageLogger.categories.append('L1GtTrigReport')

# process.load("L1Trigger.GlobalTriggerAnalyzer.l1GtTrigReport_cfi")
# process.l1GtTrigReport.L1GtRecordInputTag = "simGtDigis"
# process.l1GtTrigReport.PrintVerbosity = 1

# process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(10000))
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(1000))
# process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(100))
# process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(1))

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.connect   = 'frontier://FrontierProd/CMS_COND_31X_GLOBALTAG'
process.GlobalTag.pfnPrefix = cms.untracked.string('frontier://FrontierProd/')
# process.GlobalTag.globaltag = cms.string('START44_V13::All')
# process.GlobalTag.globaltag = cms.string('START44_V6::All')
if data:
    process.GlobalTag.globaltag = cms.string('GR_R_52_V10::All')
else:
    from Configuration.AlCa.autoCond import autoCond
    process.GlobalTag.globaltag = autoCond['startup']

# process.load('Configuration.StandardSequences.GeometryExtended_cff')
# process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
# process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')

if data:
    process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
else:
    process.load('Configuration.StandardSequences.RawToDigi_cff')

process.raw2digi = cms.Path(process.RawToDigi)
process.reco = cms.Path(process.reconstruction)

process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')

process.load('Debug.Plotters.CaloRegionPlotter_cfi')
process.load('Debug.Plotters.DigiPlotter_cfi')
process.load('Debug.Plotters.L1GctPlotter_cfi')
process.load('Debug.Plotters.RecHitPlotter_cfi')
process.load('Debug.Plotters.RecHitTPPlotter_cfi')
process.load('Debug.Plotters.TrackPlotter_cfi')
process.load('Debug.Plotters.TriggerPrimitiveDigiPlotter_cfi')

process.reEmulTrigPrimPlotter = process.triggerPrimitiveDigiPlotter.clone()
process.reEmulTrigPrimPlotter.ecalDigis = cms.InputTag('gctReEmulDigis')

process.reEmulCaloRegionPlotter = process.caloRegionPlotter.clone()
process.reEmulCaloRegionPlotter.caloRegions = cms.InputTag('rctReEmulDigis')

process.reEmulGctPlotter = process.gctPlotter.clone()
process.reEmulGctPlotter.l1GctSums = cms.InputTag('gctReEmulDigis')

process.triggerPrimitiveDigiPlotter.ecalDigis = cms.InputTag(
        'ecalDigis', 'EcalTriggerPrimitives')
# always need to reemulate MC, since TPs are not in RAW
if mc:
    process.triggerPrimitiveDigiPlotter.hcalDigis = cms.InputTag(
            'hcalReEmulDigis', '')

# Plotter path assembly
# =====================

process.plotters = cms.Path()

if raw:
    process.plotters *= \
            process.digiPlotter * \
            process.triggerPrimitiveDigiPlotter * \
            process.caloRegionPlotter * \
            process.gctPlotter
if reemul:
    process.plotters *= \
            process.reEmulTrigPrimPlotter * \
            process.reEmulCaloRegionPlotter * \
            process.reEmulGctPlotter
if reco:
    process.plotters *= process.trackPlotter * process.recHitPlotter
if raw and reco:
    process.plotters *= process.recHitTPPlotter

if mc:
    class SetWeights:
        def enter(self, m):
            m.weigh = cms.untracked.bool(True)
            m.weightFile = cms.untracked.string('create_plots_mc_weights.root')
        def leave(self, m):
            pass

    process.plotters.visit(SetWeights())

process.load("L1Trigger.GlobalTriggerAnalyzer.l1GtTrigReport_cfi")
if reemul:
    process.l1GtTrigReport.L1GtRecordInputTag = "simGtDigis"
else:
    process.l1GtTrigReport.L1GtRecordInputTag = "gtDigis"
process.l1GtTrigReport.PrintVerbosity = 1
process.report = cms.Path(process.l1GtTrigReport)

import HLTrigger.HLTfilters.triggerResultsFilter_cfi as hlt
process.ZeroBiasAve = hlt.triggerResultsFilter.clone()
process.ZeroBiasAve.triggerConditions = cms.vstring('HLT_ZeroBias*',)
process.ZeroBiasAve.hltResults = cms.InputTag( "TriggerResults", "", "HLT" )
process.ZeroBiasAve.l1tResults = cms.InputTag("")
process.ZeroBiasAve.throw = cms.bool( False )
process.zerobias = cms.Path(process.ZeroBiasAve)

if reemul:
    process.load('HLTrigger.Configuration.HLT_FULL_cff')
    process.load('Configuration.StandardSequences.SimL1Emulator_cff')

    import L1Trigger.Configuration.L1Trigger_custom
    process = L1Trigger.Configuration.L1Trigger_custom.customiseL1GtEmulatorFromRaw(process)
    process = L1Trigger.Configuration.L1Trigger_custom.customiseResetPrescalesAndMasks(process)

    import HLTrigger.Configuration.customizeHLTforL1Emulator
    process = HLTrigger.Configuration.customizeHLTforL1Emulator.switchToL1Emulator(
            process, False, 'minPt', 'minPt', False, True, False, True)
    process = HLTrigger.Configuration.customizeHLTforL1Emulator.switchToSimGtReEmulGctDigis(process)
    process.HcalTPGCoderULUT.LUTGenerationMode = cms.bool(True)

    # process.es_pool2 = cms.ESSource("PoolDBESSource",
            # process.CondDBSetup,
            # timetype = cms.string('runnumber'),
            # toGet = cms.VPSet( cms.PSet( record = cms.string('HcalL1TriggerObjectsRcd'),
                # tag = cms.string('L1TriggerObjects_testIdealHCALv2')),),
            # connect = cms.string('frontier://FrontierPrep/CMS_COND_HCAL'),
            # authenticationMethod = cms.untracked.uint32(0),)
    # process.es_prefer_es_pool2 = cms.ESPrefer( "PoolDBESSource", "es_pool2")

    process.unpacker = cms.Path(process.HLTL1UnpackerSequence)

    process.load("EventFilter.L1GlobalTriggerRawToDigi.l1GtUnpack_cfi")
    process.l1unpack = cms.Path(process.l1GtUnpack)

process.dump = cms.EDAnalyzer("EventContentAnalyzer")
process.pdump = cms.Path(process.dump)

process.schedule = cms.Schedule(
        process.zerobias)

if raw:
    process.schedule.append(process.raw2digi)
if reemul:
    process.schedule.append(process.unpacker)
    process.schedule.append(process.l1unpack)

# process.schedule.append(process.pdump)
process.schedule.append(process.plotters)

if raw:
    process.schedule.append(process.report)

process.TFileService = cms.Service("TFileService",
        closeFileFast = cms.untracked.bool(True),
        fileName = cms.string("plots.root"))

if data:
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                '/store/data/Run2011B/ZeroBiasHPF0/RAW/v1/000/179/828/D091ECAE-39FF-E011-8105-001D09F2A49C.root',
                '/store/data/Run2011B/ZeroBiasHPF0/RAW/v1/000/179/828/CAC9A8F8-38FF-E011-9D05-003048D3750A.root',
                '/store/data/Run2011B/ZeroBiasHPF0/RAW/v1/000/179/828/C057138E-37FF-E011-A9A6-001D09F26C5C.root',
                '/store/data/Run2011B/ZeroBiasHPF0/RAW/v1/000/179/828/BE735C1D-3BFF-E011-873D-BCAEC53296F2.root',
                '/store/data/Run2011B/ZeroBiasHPF0/RAW/v1/000/179/828/90BCCB91-37FF-E011-8F43-002481E0D90C.root',
                '/store/data/Run2011B/ZeroBiasHPF0/RAW/v1/000/179/828/8895F0E0-42FF-E011-ACD4-001D09F2AF96.root',
                '/store/data/Run2011B/ZeroBiasHPF0/RAW/v1/000/179/828/428EB095-34FF-E011-87FB-001D09F291D7.root',
                '/store/data/Run2011B/ZeroBiasHPF0/RAW/v1/000/179/828/1C9C298C-37FF-E011-B893-001D09F24664.root',
                '/store/data/Run2011B/ZeroBiasHPF0/RAW/v1/000/179/828/1A49A7B1-39FF-E011-8D22-001D09F25393.root',
                '/store/data/Run2011B/ZeroBiasHPF0/RAW/v1/000/179/828/088937ED-35FF-E011-BA7A-001D09F24D8A.root',
                ]),
            lumisToProcess = cms.untracked.VLuminosityBlockRange(
                '179828:179-179828:189', '179828:366-179828:366'
                ))
else:
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0000/DEE6A498-F259-E111-96EB-1CC1DE1D0600.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0000/227E66F1-F259-E111-A450-1CC1DE0437C8.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0000/1CE4EBFF-EF59-E111-8E40-001F296A527C.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0001/5C326C5D-F259-E111-94B3-1CC1DE1D16C8.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0003/507724FE-F159-E111-8543-1CC1DE1CDF30.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0003/9A9A4A64-F359-E111-9EA9-1CC1DE1CF280.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0003/64C8D5F5-F259-E111-8820-1CC1DE055158.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0004/B6A5D4C7-F259-E111-8CB0-1CC1DE041FD8.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0004/54375620-F359-E111-ACA2-1CC1DE1CEDB2.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0003/D006977F-F359-E111-9B0B-1CC1DE040FE8.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0003/70BA27A4-F459-E111-A9C7-1CC1DE1CDD02.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0003/4CC63156-F159-E111-8BF0-1CC1DE0503C0.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0004/C068B06E-F359-E111-A8BA-78E7D1E4B874.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0000/CC344013-EC59-E111-A8C7-0017A477103C.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0001/5280B60A-E959-E111-83D6-00237DA1494E.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0002/001706D0-F359-E111-B787-78E7D1651098.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0003/66E6667B-F359-E111-904F-1CC1DE048F98.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0003/20D358F0-EF59-E111-80AF-001F296AC6F2.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0002/4A78AA4A-E359-E111-BFF9-1CC1DE055158.root",
                "/store/mc/Fall11/Neutrino_Pt_2to20_gun/GEN-SIM-RAW-HLTDEBUG-RECO/E7TeV_Ave23_50ns-v3/0001/F8DDC23B-E459-E111-B849-1CC1DE041F38.root"
                ]))

# print process.dumpPython()
