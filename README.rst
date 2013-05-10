Plotting package for L1 and other quantities
===

Trimming w.r.t. pileup
---
Use create_mask.py to trim down PU to match MC within ±3.  Use data
from here_.

.. _here: https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/PileUp/

Pileup-distribution
---
::

  pileupCalc.py -i pu_45.mask --inputLumiJSON \
    lumi_files/pileup_highLumi_fills.txt --calcMode observed --minBiasXsec \ 
    69400 --maxPileupBin 150 --numPileupBins 150 pu_45.root

Weight file generation
---
After running once with no/old weights: ::

  merge_pileup.py pu_45.root ../../../plots_mc_raw-45.root weights_45.root

Data pileup file for comparisons
---
To include a pileup curve for data in plots: ::

  mv_pileup.py pu_45.root ../../../plots_data_pileup-45.root
