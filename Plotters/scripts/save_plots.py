#!/usr/bin/env python

import math
import os.path
import ROOT as r

r.gROOT.SetBatch()
r.gROOT.SetStyle('Plain')

class MHStack(r.THStack):
    def __init__(self, name='', title='', legend=None, logplot=False,
            limits=None):
        r.THStack.__init__(self, name, title)
        self.legend = legend
        self.logplot = logplot
        self.limits = limits

    def Draw(self):
        r.THStack.Draw(self, "nostack")
        if self.limits:
            self.GetXaxis().SetRangeUser(*self.limits)

def get_xmax(hist):
    last = hist.GetXaxis().GetXmax()
    i = hist.GetNbinsX()
    while i > 0:
        if hist.GetBinContent(i) > 0:
            return last
        last = hist.GetBinLowEdge(i)
        i -= 1

def create_stack(hists, files, norms=None, adjustlimits=True, limits=None, logplot=False, normalized=True, 
        title=''):
    l = r.TLegend(.1, .1, .9, .9)
    l.SetNColumns(len(files))

    s = MHStack(legend=l, logplot=logplot, limits=limits)
    max_x = 0

    for (h, f, n, c) in zip(hists, files, norms, range(1, len(files) + 1)):
        h.SetLineColor(c)
        if normalized:
            h.Scale(1. / n)

        if title == '':
            title = ";".join((h.GetTitle(),
                    h.GetXaxis().GetTitle(),
                    h.GetYaxis().GetTitle()))

        max_x = max(max_x, get_xmax(h))

        s.Add(h)
        s.SetTitle(title)
        l.AddEntry(h, f, "l")

    if not limits and adjustlimits:
        s.limits = (0, max_x * 1.05)
    return s

def plot_stacks(stacks, filename, width=None):
    if not width:
        height = 1
        width = len(stacks)
    else:
        height = int(math.ceil(len(stacks) / float(width)))

    c = r.TCanvas("c", "", width * 600, height * 400)
    c.Divide(width, height)

    for (s, n) in zip(stacks, range(1, len(stacks) + 1)):
        c.cd(n)
        p = c.GetPad(n)
        p.SetTitle(s.GetTitle())
        p.Divide(1, 2)

        p.cd(2)
        p.GetPad(2).SetPad(0., 0., 1., .1)
        s.legend.Draw()
        p.cd(1)
        p.GetPad(1).SetPad(0., .1, 1., 1.)
        if s.logplot:
            p.GetPad(1).SetLogy(True)
        s.Draw()
    c.SaveAs(filename)

def legend(dir):
    r = 'Data' if 'data' in dir else 'MC'
    if 'data' in dir:
        n = 604031
    else:
        n = 49493000

    if 'reemul' in dir.lower():
        r += ' (reemulated)'
    if 'reweighted' in dir.lower():
        r += ' - reweighted'

    return r, n

alias ={}

def summarize(pdffile, files):
    handles = [r.TFile(fn) for fn in files]

    plots = {}
    plots_2d = {}
    plots_digi = {}
    plots_tp = {}

    for f in handles:
        for d in f.GetListOfKeys():
            dir = d.ReadObj()
            path = dir.GetPath()
            for k in dir.GetListOfKeys():
                key = k.GetName()
                obj = k.ReadObj()
                leg, norm = legend(path)

                if obj.GetEntries() == 0:
                    print "{k} in {p} empty!".format(k=key, p=path)

                if 'trig' in path.lower():
                    key = 'tp_' + key
                    if 'reemulated' in leg:
                        continue

                # TODO remove hotfix after fixing analyzer
                if key == 'tp_ecal_soi_adc_':
                    key = 'tp_ecal_soi_adc'

                subkey = None

                if type(obj) == r.TH2F or type(obj) == r.TH2D:
                    key, subkey = key.rsplit('_', 1)
                    plot_dict = plots_2d
                elif 'tp' in key and 'digi' in key:
                    key, subkey = key.rsplit('_', 1)
                    plot_dict = plots_tp
                elif 'digi' in key:
                    key, subkey = key.rsplit('_', 1)
                    plot_dict = plots_digi
                else:
                    plot_dict = plots

                if key not in plot_dict:
                    plot_dict[key] = [] if not subkey else {}
                if subkey:
                    if subkey not in plot_dict[key]:
                        plot_dict[key][subkey] = []
                    plot_dict[key][subkey].append((obj, leg, norm))
                else:
                    plot_dict[key].append((obj, leg, norm))

    for key, objs in plots.items():
        ps, ls, ns = zip(*objs) # unzip
        if len(ps) == 0 or type(ps[0]) not in [r.TH1D, r.TH1F]:
            continue
        s = create_stack(ps, ls, ns)
        plot_stacks([s], pdffile.format(p=key))
        s.logplot = True
        plot_stacks([s], pdffile.format(p=key + '_log'))

    for plot_dict in (plots_digi, plots_tp):
        for (key, subdict) in plot_dict.items():
            limits = [0, 0]
            for lst in subdict.values():
                for tpl in lst:
                    limits[1] = max(limits[1], get_xmax(tpl[0]))
            print key, limits
            for subkey, objs in subdict.items():
                real_key = '_'.join([key, subkey])
                ps, ls, ns = zip(*objs) # unzip
                if len(ps) == 0 or type(ps[0]) not in [r.TH1D, r.TH1F]:
                    continue
                s = create_stack(ps, ls, ns, limits=limits)
                plot_stacks([s], pdffile.format(p=real_key))
                s.logplot = True
                plot_stacks([s], pdffile.format(p=real_key + '_log'))

    for (key, subdict) in plots_2d.items():
        projs = {'ieta': lambda h: h.ProjectionX().Clone(),
                'iphi': lambda h: h.ProjectionY().Clone()}

        mps = subdict['mp']
        for other in subdict.keys():
            if other == 'mp':
                continue
            zipped = zip(subdict[other], mps)
            # print zipped
            merged = map(lambda (o, m): [(o[0].Clone(), m[0].Clone())] + list(o[1:]), zipped)
            # print merged

            subdict['_'.join([other, 'mp'])] = merged

        for (axis, proj) in projs.items():
            # subkey one of (mp, et, adc, ...)
            for subkey, objs in subdict.items():
                norm_by_event = '_' not in subkey
                # print subkey
                real_key = '_'.join([key, subkey, axis])
                if not norm_by_event:
                    tmp_ps, ls, ns = zip(*objs)
                    ps = []
                    for (val, mp) in tmp_ps:
                        tmp_v = proj(val)
                        tmp_m = proj(mp)
                        tmp_v.Divide(tmp_m)
                        ps.append(tmp_v)
                else:
                    ps, ls, ns = zip(*objs) # unzip
                    ps = map(proj, ps)
                if len(ps) == 0 or type(ps[0]) not in [r.TH1D, r.TH1F]:
                    continue
                s = create_stack(ps, ls, ns, adjustlimits=False, normalized=norm_by_event)
                plot_stacks([s], pdffile.format(p=real_key))
                s.logplot = True
                plot_stacks([s], pdffile.format(p=real_key + '_log'))
        
        # print subdict.keys()

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        sys.stderr.write(
                "usage: {p} output file...\n".format(p=sys.argv[0]))
        sys.exit(1)

    summarize(sys.argv[1], sys.argv[2:])
