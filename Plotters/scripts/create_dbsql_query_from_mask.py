#!/usr/bin/env python

import json
import sys

if len(sys.argv) != 2:
    sys.stderr.write('usage: {p} maskfile\n'.format(p=sys.argv[0]))
    sys.exit(1)

with open(sys.argv[1]) as f:
    data = json.loads(f.readline())
    qs = []
    for (run, lumis) in data.items():
        lq = []
        for (ls, le) in lumis:
            lq += [str(i) for i in xrange(ls, le+1)]
        qs.append("(run={r} and lumi in ({l}))".format(r=run, l=",".join(lq)))
    print "\n\n\n".join(qs)
