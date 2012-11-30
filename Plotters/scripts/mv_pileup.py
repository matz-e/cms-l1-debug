#!/usr/bin/env python

import ROOT as r
import sys

r.gROOT.SetBatch()

if len(sys.argv) != 3:
    sys.stderr.write('usage: {p} source dest\n'.format(p=sys.argv[0]))
    sys.exit(1)

infile = r.TFile(sys.argv[1])
hist = infile.Get('pileup')
hist.Scale(604031.0 / hist.Integral())

outfile = r.TFile(sys.argv[2], 'CREATE')
dir = outfile.mkdir('pileUpPlotter')
dir.cd()
hist.Write()
outfile.Close()
