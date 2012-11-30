import sys

n = 1000
pu = '45'
data = False
debug = False

do_reco = False

aod = False
raw = True
reco = False
reemul = False

wfile = 'Debug/Plotters/test/weights_{n}.root'.format(n=pu)

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
    elif type(globals()[k]) == int:
        globals()[k] = int(v)
    else:
        globals()[k] = v

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
    process.GlobalTag.globaltag = cms.string('GR_P_V40::All')
else:
    process.GlobalTag.globaltag = cms.string('START53_V7B::All')

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

process.raw2digi = cms.Path(process.RawToDigi)
process.reco = cms.Path(process.reconstruction)

process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')

process.load('Debug.Plotters.CaloRegionPlotter_cfi')
process.load('Debug.Plotters.DigiPlotter_cfi')
process.load('Debug.Plotters.L1GctPlotter_cfi')
process.load('Debug.Plotters.L1JetPlotter_cfi')
process.load('Debug.Plotters.PileUpPlotter_cfi')
process.load('Debug.Plotters.RecHitPlotter_cfi')
process.load('Debug.Plotters.RecHitTPPlotter_cfi')
process.load('Debug.Plotters.TrackPlotter_cfi')
process.load('Debug.Plotters.TriggerPrimitiveDigiPlotter_cfi')

process.reEmulTrigPrimPlotter = process.triggerPrimitiveDigiPlotter.clone()
if data:
    process.reEmulTrigPrimPlotter.ecalDigis = cms.InputTag('gctReEmulDigis')
else:
    process.reEmulTrigPrimPlotter.ecalDigis = cms.InputTag('ecalDigis', 'EcalTriggerPrimitives')
process.reEmulTrigPrimPlotter.hcalDigis = cms.InputTag('hcalReEmulDigis', '')

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
            process.gctPlotter * \
            process.jetPlotter
if raw and reemul:
    process.plotters *= \
            process.reEmulTrigPrimPlotter * \
            process.reEmulCaloRegionPlotter * \
            process.reEmulGctPlotter

if reco or do_reco:
    process.plotters *= process.trackPlotter * process.recHitPlotter
if (raw and reco) or do_reco:
    process.plotters *= process.recHitTPPlotter

if mc:
    process.plotters *= process.pileUpPlotter

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
    process.plotters.visit(visitor)
    for m in visitor.weighted:
        process.__setattr__(m.label(), m)
        process.plotters *= m

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
    process.load("EventFilter.L1GlobalTriggerRawToDigi.l1GtUnpack_cfi")

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
    process.l1unpack = cms.Path(process.l1GtUnpack)

process.dump = cms.EDAnalyzer("EventContentAnalyzer")
process.pdump = cms.Path(process.dump)

process.schedule = cms.Schedule()

if data:
    process.schedule.append(process.zerobias)
if raw or do_reco:
    process.schedule.append(process.raw2digi)
if reemul:
    process.schedule.append(process.unpacker)
    process.schedule.append(process.l1unpack)
if debug:
    process.schedule.append(process.pdump)
if do_reco:
    process.schedule.append(process.reco)

process.schedule.append(process.plotters)

if raw:
    process.schedule.append(process.report)

process.TFileService = cms.Service("TFileService",
        closeFileFast = cms.untracked.bool(True),
        fileName = cms.string("standalone_plots_{d}_{p}.root".format(d='data' if data else 'mc', p=pu)))

if data and pu == '45':
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
elif data and pu == 'low':
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/FCEF0A4B-1084-E111-83B4-E0CB4E5536AE.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/FA21A724-1F84-E111-AD0E-003048F117EC.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/F89B48BA-2984-E111-AE96-003048D2BDD8.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/F6343A2E-3284-E111-BCD6-003048F118C6.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/F454B050-2184-E111-BB9A-BCAEC518FF65.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/EE9555B2-1184-E111-83AE-BCAEC518FF44.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/EC068C54-0B84-E111-9BF5-001D09F2841C.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/E4FC910E-3084-E111-B00E-BCAEC518FF50.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/E2EE4DF0-1F84-E111-9D44-003048678098.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/E2E0D8F0-1A84-E111-B1EE-001D09F29533.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/E04FEAF9-1584-E111-906D-0019B9F70468.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/DEA28EE3-0E84-E111-8F07-BCAEC5329719.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/D4740890-2084-E111-8308-003048F1110E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/D2F895FE-0B84-E111-9229-E0CB4E55365D.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/D0D8F3EF-1A84-E111-B0BD-0025901D5D80.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/CE8FFC16-1884-E111-8763-0025901D5D7E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/CCFE3878-1284-E111-9391-5404A638869C.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/CC76E9D3-2484-E111-B3C3-001D09F2841C.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/CC50E5D7-1384-E111-9C82-E0CB4E553651.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/C8A93544-0784-E111-8EAF-BCAEC518FF89.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/C86BB5C8-1884-E111-A85A-003048F1BF66.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/C49EEF48-0784-E111-8673-003048F01E88.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/C48D3094-2C84-E111-AB6D-003048F11C28.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/C488DE3E-1584-E111-B715-003048D2C020.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/C0AF3FDE-3284-E111-9ABA-003048F118D4.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/BE606E50-0B84-E111-87E9-001D09F2915A.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/BE486D66-0984-E111-9E6A-5404A63886CB.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/BE468800-2E84-E111-9FA0-003048D2BE12.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/BCEE680D-1D84-E111-847D-001D09F2983F.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/BC956DEB-1F84-E111-858A-003048D2C16E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/BAF27156-2884-E111-AE2A-001D09F29524.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/BA008C4B-1084-E111-B50D-003048F117F6.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/B4C8D82E-3284-E111-8FEA-0025901D626C.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/B4AA22FC-1084-E111-97F3-BCAEC518FF6E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/B27E2F45-0784-E111-99F6-BCAEC5329716.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/B229C9BA-2984-E111-ABB7-003048D2BD66.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/AC62D1EA-1384-E111-877A-BCAEC5364C4C.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/AA0E622E-0984-E111-B3EE-BCAEC518FF65.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/A8507FBA-2984-E111-9E3E-003048D2C01E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/A64D34FF-3484-E111-9211-003048F118D4.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/A489B921-2B84-E111-A9E5-BCAEC518FF74.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/9E05ECA9-2784-E111-8827-0025B32445E0.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/98FC9CF3-4084-E111-8995-001D09F24D4E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/96F82600-2E84-E111-A634-003048F117B6.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/96E10FD3-2484-E111-A3B6-001D09F295FB.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/96DF3201-3584-E111-A84B-003048F1BF66.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/94264CFC-2184-E111-B32C-5404A63886AE.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/8EFBD78E-2084-E111-892A-003048F11112.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/8A31E25C-2F84-E111-960F-003048F118C2.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/8A27C073-1784-E111-A7A3-00215AEDFD98.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/86F92E62-2384-E111-9C10-BCAEC5329700.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/84045B31-1A84-E111-AC34-0025901D5D7E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/82B7B7B9-2984-E111-B880-003048F118E0.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/7E40460D-1D84-E111-92DF-001D09F248F8.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/7AE014A4-1B84-E111-9C67-001D09F24D67.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/789CC2BA-3384-E111-B172-5404A640A648.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/723F2223-1F84-E111-AC78-001D09F244DE.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/6CEBB1EE-0984-E111-86EC-003048D2BC42.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/6AA3CEC6-1884-E111-84D1-001D09F29597.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/6A8F357D-1984-E111-A6CE-001D09F2424A.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/6A5CA57C-1984-E111-BC41-5404A640A642.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/6660E163-2384-E111-80F2-5404A63886C1.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/64311749-3484-E111-8D68-0025901D629C.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/606A21B8-3584-E111-9C42-003048F1110E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/5AEF48F8-2184-E111-AA4B-5404A63886EC.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/583008A9-2784-E111-B998-002481E0D73C.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/5814F454-0684-E111-85F1-001D09F2B2CF.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/5667A0D7-2B84-E111-ACF0-BCAEC532971F.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/54E09066-0D84-E111-9E96-0025901D5C80.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/52AFD35C-2F84-E111-B3F3-003048F1C58C.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/52150C2E-2484-E111-BFF0-003048D3C944.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/4EEE658E-0884-E111-891C-001D09F2447F.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/4C442AB8-0C84-E111-9E59-003048F24A04.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/4C2856A5-1484-E111-A15C-001D09F25479.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/4A77387C-3184-E111-9E3F-001D09F2910A.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/4A2BBC7C-1284-E111-936A-BCAEC532971F.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/422D83C1-0784-E111-AAB5-002481E0D7D8.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/421E86E4-0984-E111-B722-003048D37456.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/40A47F2E-2484-E111-8141-003048D3751E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/4074B930-0E84-E111-9C43-E0CB4E4408E7.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/40369B23-1384-E111-9305-BCAEC518FF8E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/3EACF4E6-0E84-E111-9A09-5404A63886A0.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/3C205156-1C84-E111-B409-003048F0258C.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/3640F577-1E84-E111-B65F-001D09F34488.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/30F590FE-0B84-E111-81CB-5404A63886CF.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/2E8A8AA3-1B84-E111-A8E8-0019B9F72CE5.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/2AD9408B-0F84-E111-BB0C-BCAEC5364CFB.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/28F41271-2A84-E111-90F5-002481E94C7E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/20497F47-0E84-E111-A7BA-BCAEC518FF41.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/1E7E0214-1884-E111-AB7C-003048F1182E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/1E41629F-0A84-E111-8868-003048F024E0.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/18946F48-0784-E111-A553-485B39897227.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/12E82174-1784-E111-A088-003048D3C980.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/12A1DC64-0D84-E111-A571-0025901D6272.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/10806F22-2B84-E111-9D42-003048F024C2.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/0EEE6C94-2C84-E111-9FAE-BCAEC518FF50.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/0E42AD6A-0D84-E111-A2BC-001D09F2305C.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/0E0CBA55-2884-E111-ADC1-001D09F2AF1E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/0C2158F6-2184-E111-9518-5404A63886A0.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/0AEDB96D-4284-E111-B0C5-003048F1110E.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/0A631907-2984-E111-8A1A-003048F024DA.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/08388CAC-2E84-E111-A4C6-003048F1C58C.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/00BF62C3-3084-E111-8D66-BCAEC518FF8A.root',
                '/store/data/Run2012A/MinimumBias/RAW/v1/000/190/949/00A1CFF8-1584-E111-9EA0-001D09F25479.root'
                ]),
            lumisToProcess = cms.untracked.VLuminosityBlockRange(
                    '190949:221-190949:1132'))
elif mc and pu == 'low':
    process.source = cms.Source('PoolSource',
            fileNames = cms.untracked.vstring([
                'SingleNuPt10_cfi_GEN_SIM_PU_RAW.root'
                ]))
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
