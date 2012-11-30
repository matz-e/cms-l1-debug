#!/usr/bin/env python

import ROOT as r
import sys

r.gROOT.SetBatch()

if len(sys.argv) != 4:
    sys.stderr.write("usage: {p} datafile mcfile outfile\n".format(p=sys.argv[0]))
    sys.exit(1)

(dfile, mfile) = [r.TFile(fn) for fn in sys.argv[1:3]]
real_pu = dfile.Get('pileup')
sim_pu = mfile.Get('pileUpPlotter/pileup')

ofile = r.TFile(sys.argv[3], 'CREATE')
ofile.WriteObject(real_pu, 'data')
ofile.WriteObject(sim_pu, 'mc')
ofile.Close()
