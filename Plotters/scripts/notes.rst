Data selection
==============
from /ZeroBias1/Run2012C-v1/RAW (as per Brian Winer):

Fill 	 Runs                   	 PU
----     ----                            -- 
2824 	 198603                 	 45
2822 	 198588, 198589, 198590 	 45
2825 	 198609                 	 66

GlobalTag: GE_P_V40

MC sets: ::
  /Neutrino_Pt_2to20_gun/Summer12_DR53X-PU45_noOOT_START53_V7B-v2/GEN-RAW
  /Neutrino_Pt_2to20_gun/Summer12_DR53X-PU66_noOOT_START53_V7B-v2/GEN-RAW

GlobalTag: START53_V7B

Trimming w.r.t. pileup
----------------------
Use create_mask.py to trim down PU to match MC within ±3.  Use data
from here_.

.. _here: https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/Prompt/

Pileup-distribution
-------------------
::
  pileupCalc.py -i pu_45.mask --inputLumiJSON \
    lumi_files/pileup_highLumi_fills.txt --calcMode observed --minBiasXsec \ 
    69400 --maxPileupBin 150 --numPileupBins 150 pu_45.root
