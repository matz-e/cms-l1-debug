#!/usr/bin/env python
"""
Use with pileup data from e.g.:
https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/PileUp/
"""
import json
import sys

from RecoLuminosity.LumiDB.pileupParser import pileupParser

try:
    pileup = float(sys.argv[1])
    epsilon = float(sys.argv[2])

    with open(sys.argv[3], 'r') as f:
        runs = map(int, f.readlines())
    with open(sys.argv[4], 'r') as f:
        data = pileupParser(f.read()).runsandls()
except:
    sys.stderr.write('usage: {p} pileup epsilon runfile pileupfile\n'.format(
        p=sys.argv[0]))
    sys.exit(1)

res = {}

for (run, lsinfo) in data.iteritems():
    if run not in runs:
        continue

    for (ls, info) in sorted(lsinfo.iteritems(), key=lambda (a, b): a):
        (lumi, rms_int, mean_int) = info

        # xsec = 73500
        xsec = 69400
        rms_int *= xsec
        mean_int *= xsec

        if abs(mean_int - pileup) < epsilon:
            srun = str(run)
            if srun not in res:
                res[srun] = []
            if len(res[srun]) > 0 and res[srun][-1][1] == ls - 1:
                res[srun][-1][1] = ls
            else:
                res[srun] += [[ls, ls]]

# print json.dumps(res, sort_keys=True, indent=2)
print json.dumps(res)
