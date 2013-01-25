#!/usr/bin/env python

mc_cmp = False

# Argument parsing
# vvv

import sys

if len(sys.argv) > 1 and sys.argv[1].endswith('.py'):
    sys.argv.pop(0)
if len(sys.argv) == 2 and ':' in sys.argv[1]:
    argv = sys.argv[1].split(':')
else:
    argv = sys.argv[1:]

new_args = []
for arg in argv:
    if '=' not in arg:
        new_args.append(arg)
        continue

    (k, v) = map(str.strip, arg.split('='))
    if k not in globals():
        raise "Unknown argument '%s'!" % (k,)
    if type(globals()[k]) == bool:
        globals()[k] = v.lower() in ('y', 'yes', 'true', 't', '1')
    else:
        globals()[k] = type(globals()[k])(v)

import math
import os
import os.path
import re
import ROOT as r

r.gROOT.SetBatch()
r.gROOT.SetStyle('Modern')

r.gStyle.SetTitleBorderSize(0)
# r.gStyle.SetTitleAlign(22)

override_limits = {
        'ecal_en_tot': (0, 750)
        }

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

def get_limits(hist):
    x_max = hist.GetXaxis().GetXmax()

    i = hist.GetNbinsX()
    while i > 0:
        if hist.GetBinContent(i) > 0:
            break
        x_max = hist.GetBinLowEdge(i)
        i -= 1

    i = 1
    x_min = 0
    while x_min < x_max:
        if hist.GetBinContent(i) > 0:
            break
        x_min = hist.GetBinLowEdge(i)
        i += 1

    extend_by = (x_max - x_min) / 10
    return (max(0, x_min - extend_by), x_max + extend_by)

def greater(l1, l2):
    return (min(l1[0], l2[0]), max(l1[1], l2[1]))

def create_stack(hists, files, norms=None, adjustlimits=True, limits=None, logplot=False, normalized=True, 
        title=''):
    l = r.TLegend(.1, .1, .9, .9)
    l.SetNColumns(min(len(files), 3 if not mc_cmp else 4))

    stack = MHStack(legend=l, logplot=logplot, limits=limits)
    stack_rel = MHStack(legend=l, logplot=logplot, limits=limits)

    new_limits = (float('inf'), 0)

    norm_hist = None
    for (h, f, n, c) in zip(hists, files, norms, range(1, len(files) + 1)):
        # h.SetLineColor(c)
        if normalized:
            h.Scale(1. / n)
            h.SetYTitle(h.GetYaxis().GetTitle() + ' / event')

        if not norm_hist:
            norm_hist = h.Clone()

        if title == '':
            title = ";".join((h.GetTitle(),
                    h.GetXaxis().GetTitle(),
                    h.GetYaxis().GetTitle()))

        new_limits = greater(new_limits, get_limits(h))

        stack.Add(h)
        stack.SetTitle(title)

        h_rel = h.Clone()
        h_rel.Divide(norm_hist)

        stack_rel.Add(h_rel)
        stack_rel.SetTitle(title)

        l.AddEntry(h, f, "l")

    if not limits and adjustlimits:
        stack.limits = new_limits
        stack_rel.limits = new_limits
    return (stack, stack_rel)

def plot_stacks(stacks, filename, width=None):
    dirname = os.path.dirname(filename)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    if not width:
        height = 1
        width = len(stacks)
    else:
        height = int(math.ceil(len(stacks) / float(width)))

    c = r.TCanvas("c", "", width * 600, height * 600)
    c.Divide(width, height)

    for (s, n) in zip(stacks, range(1, len(stacks) + 1)):
        c.cd(n)
        p = c.GetPad(n)
        p.SetTitle(s[0].GetTitle())
        p.Divide(1, 3)

        p.cd(3)
        p.GetPad(3).SetPad(0., 0., 1., .1)
        s[0].legend.Draw()
        
        p.cd(1)
        r.gPad.SetPad(0., .4, 1., 1.)
        if s[0].logplot:
            p.GetPad(1).SetLogy(True)
        s[0].Draw()
        # s[0].GetHists()[0].Draw("same P")
        r.gPad.SetBottomMargin(1e-5)
        r.gPad.SetTopMargin(.15)
        r.gPad.SetTickx(2)
        r.gPad.Modified()

        p.cd(2)
        p.GetPad(2).SetPad(0., .1, 1., .4)
        # if s[1].logplot:
        p.GetPad(2).SetLogy(True)
        s[1].SetTitle("")
        s[1].Draw()
        # s[1].GetHists()[0].Draw("same")
        s[1].GetYaxis().SetTitle("relative")
        s[1].GetYaxis().SetLabelSize(2 * s[0].GetYaxis().GetLabelSize())
        s[1].GetYaxis().SetTitleOffset(.5)
        s[1].GetYaxis().SetTitleSize(2 * s[0].GetYaxis().GetTitleSize())
        s[1].GetXaxis().SetLabelSize(2 * s[0].GetXaxis().GetLabelSize())
        s[1].GetXaxis().SetTickLength(.06)
        s[1].GetXaxis().SetTitleOffset(1.2)
        s[1].GetXaxis().SetTitleSize(2 * s[0].GetXaxis().GetTitleSize())
        s[1].GetXaxis().SetTitle(s[0].GetXaxis().GetTitle())
        r.gPad.SetTopMargin(1e-5)
        r.gPad.SetBottomMargin(.3)
        r.gPad.SetTickx(1)
        r.gPad.Modified()
    c.Update()
    c.SaveAs(filename)

last_color = 0
colors = {}
counts = {}

def legend(path, hist):
    """
    Create and return a legend label, normalization, and modified histogram
    based on the latter's path.
    """
    f, dir = path.split(':', 1)
    basedir = dir.lower().strip('/')

    n = counts[f][0]
    # Hack to get the right normalization for pileup histograms
    if 'pileup' in f:
        hist.Scale(1. / hist.Integral())
        n = 1

    if 'data' in f:
        label = 'Data'
        color = 1
        # hist.SetMarkerSize(3)
        hist.SetMarkerStyle(r.kFullDotMedium)
    elif 'reweighted' in dir.lower():
        label = 'MC rw.'
        color = 3
    else:
        label = 'MC'
        color = 2

    if mc_cmp:
        m = re.search(r'Tune[^_]+', f)
        if not m:
            raise

        label = m.group(0)

        if 'reweighted' in dir.lower():
            label += ' rw.'

        if f not in colors:
            globals()['last_color'] += 1
            colors[f] = last_color
        color = colors[f]

    if 'reemul' in basedir:
        basedir = basedir.replace('reemul', '')
        if mc_cmp:
            color += 10
        else:
            if label == 'Data':
                color = 16
            else:
                color *= 3
        # hist.SetLineStyle(r.kDashed)
        label += ' reemul.'

    hist.SetLineColor(color)

    return label, n, basedir, hist

def get_num_events(fn):
    """
    Determine the number of events and sum of weights in file ``fn``.  Uses
    L1 energy sums or number of vertices for this.
    """
    c, c_rw = (0, 0)
    
    hist = r.gDirectory.Get('{f}:gctPlotter/et_tot'.format(f=fn))
    hist_rw = r.gDirectory.Get('{f}:reWeightedGctPlotter/et_tot'.format(f=fn))
    if hist:
        c = hist.Integral()
    if hist_rw:
        c_rw = hist.Integral()

    if c != 0:
        return (c, c_rw)

    hist = r.gDirectory.Get('{f}:trackPlotter/vertices'.format(f=fn))
    hist_rw = r.gDirectory.Get('{f}:reWeightedTrackPlotter/vertices'.format(f=fn))
    if hist:
        c = hist.Integral()
    if hist_rw:
        c_rw = hist.Integral()
    
    return (c, c_rw)

def summarize(pdffile, files):
    handles = [r.TFile(fn) for fn in files]

    for fn in files:
        counts[fn] = get_num_events(fn)

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
                leg, norm, basedir, obj = legend(path, obj)

                if obj.GetEntries() == 0:
                    print "{k} in {p} empty!".format(k=key, p=path)

                if 'trig' in path.lower():
                    # TODO remove hotfix after fixing hist naming in
                    # analyzer
                    if 'tp' not in key:
                        key = 'tp_' + key
                    if 'reemul' in leg:
                        continue

                # TODO remove hotfix after fixing analyzer
                if key == 'tp_ecal_soi_adc_':
                    key = 'tp_ecal_soi_adc'

                subkey = None

                if type(obj) == r.TH2F or type(obj) == r.TH2D:
                    if '_' not in key:
                        continue
                    key, subkey = key.rsplit('_', 1)
                    plot_dict = plots_2d
                elif 'tp' in key and 'digi' in key and not 'mp' in key:
                    key, subkey = key.rsplit('_', 1)
                    plot_dict = plots_tp
                elif 'digi' in key and not 'mp' in key:
                    key, subkey = key.rsplit('_', 1)
                    plot_dict = plots_digi
                else:
                    plot_dict = plots

                if key not in plot_dict:
                    plot_dict[key] = [] if not subkey else {}
                if subkey:
                    if subkey not in plot_dict[key]:
                        plot_dict[key][subkey] = []
                    plot_dict[key][subkey].append((obj, leg, norm, basedir))
                else:
                    plot_dict[key].append((obj, leg, norm, basedir))

    for key, objs in plots.items():
        ps, ls, ns, ds = zip(*objs) # unzip
        if len(ps) == 0 or type(ps[0]) not in [r.TH1D, r.TH1F]:
            continue
        if key in override_limits:
            s = create_stack(ps, ls, ns, limits=override_limits[key])
        else:
            s = create_stack(ps, ls, ns)
        plot_stacks([s], pdffile.format(p=key, d=ds[0]))
        s[0].logplot = True
        plot_stacks([s], pdffile.format(p=key + '_log', d=ds[0]))

    for plot_dict in (plots_digi, plots_tp):
        for (key, subdict) in plot_dict.items():
            limits = (float('inf'), 0)
            for lst in subdict.values():
                for tpl in lst:
                    limits = greater(limits, get_limits(tpl[0]))
            print key, limits
            for subkey, objs in subdict.items():
                real_key = '_'.join([key, subkey])
                ps, ls, ns, ds = zip(*objs) # unzip
                if len(ps) == 0 or type(ps[0]) not in [r.TH1D, r.TH1F]:
                    continue
                s = create_stack(ps, ls, ns, limits=limits)
                plot_stacks([s], pdffile.format(p=real_key, d=ds[0]))
                s[0].logplot = True
                plot_stacks([s], pdffile.format(p=real_key + '_log', d=ds[0]))

    for (key, subdict) in plots_2d.items():
        class FixedProj:
            def __init__(self, proj):
                self.__proj = proj
            def __call__(self, hist):
                p = self.__proj(hist).Clone()
                p.SetYTitle(hist.GetZaxis().GetTitle())
                return p

        projs = {'ieta': FixedProj(r.TH2.ProjectionX),
                 'iphi': FixedProj(r.TH2.ProjectionY)}

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
                real_key = '_'.join([key, subkey, axis])

                qdir = objs[0][3].lower()
                if 'calo' in qdir:
                    quant = 'Region'
                elif 'digi' in qdir or 'trigprim' in qdir:
                    quant = 'Digi'
                elif 'jet' in qdir:
                    quant = 'Jet'
                elif 'rechit' in qdir:
                    quant = 'RecHit'
                elif 'track' in qdir:
                    quant = 'Track'
                else:
                    sys.stderr.write('Please add a quantity assignment for "{k}"\n.'.format(k=qdir))
                    raise

                if not norm_by_event:
                    tmp_ps, ls, ns, ds = zip(*objs)
                    ps = []
                    for (val, mp) in tmp_ps:
                        tmp_v = proj(val)
                        tmp_m = proj(mp)
                        tmp_v.Divide(tmp_m)
                        tmp_v.SetYTitle(val.GetZaxis().GetTitle() + ' / ' + quant)
                        ps.append(tmp_v)
                else:
                    ps, ls, ns, ds = zip(*objs) # unzip
                    ps = map(proj, ps)
                if len(ps) == 0 or type(ps[0]) not in [r.TH1D, r.TH1F]:
                    continue
                s = create_stack(ps, ls, ns, adjustlimits=False, normalized=norm_by_event)
                plot_stacks([s], pdffile.format(p=real_key, d=ds[0]))
                s[0].logplot = True
                plot_stacks([s], pdffile.format(p=real_key + '_log', d=ds[0]))
        
        # print subdict.keys()

if len(sys.argv) < 3:
    sys.stderr.write(
            "usage: {p} output file...\n".format(p=sys.argv[0]))
    sys.exit(1)

summarize(new_args[0], new_args[1:])
