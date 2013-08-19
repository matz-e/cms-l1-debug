# Plotting L1 and other quantities

## Setup

[PyYaml](http://pyyaml.org/wiki/PyYAML) is a pre-requisite.  Install it
locally after executing `cmsenv`:

    cd /tmp
    wget -O - http://pyyaml.org/download/pyyaml/PyYAML-3.10.tar.gz|tar xzf -
    cd PyYAML-3.10/
    python setup.py install --user
    cd ..
    rm -rf PyYAML-3.10/

Afterwards, clone this repository in the CMSSW source area:

    git clone https://github.com/matz-e/cms-l1-debug.git Debug
    scram b -j32

## Running

See `Debug/Plotters/test/create_plots.py` and the `crab` configurations in the
same directory.

## Plotting

To plot using the basic configuration:

    save_plots.py Debug/Plotters/test/plots.yaml

## Miscellaneous

### Trimming w.r.t. pileup

Use `create_mask.py` to trim down PU to match MC within ±3.  Use data
from [here][1].

[1]: https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/PileUp/

### Pileup-distribution

    pileupCalc.py -i pu_45.mask --inputLumiJSON \
      lumi_files/pileup_highLumi_fills.txt --calcMode observed --minBiasXsec \ 
      69400 --maxPileupBin 150 --numPileupBins 150 pu_45.root

### Weight file generation

After running once with no/old weights: ::

    merge_pileup.py pu_45.root ../../../plots_mc_raw-45.root weights_45.root

### Data pileup file for comparisons

To include a pileup curve for data in plots: ::

    mv_pileup.py pu_45.root ../../../plots_data_pileup-45.root
