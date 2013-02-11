#!/usr/bin/env python

mc_cmp = False

# Argument parsing
# vvv

import re
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
        print "unknown argument '%s'!\n" % (k,)
        sys.exit(1)
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
r.gStyle.SetOptStat(0)
# r.gStyle.SetTitleAlign(22)

override_limits = { 'ecal_en_tot': (0, 750) }

class Plots:
    def __init__(self, title='', legend=None, logplot=False,
            limits=None, adjust=False):
        self.__adjust = adjust or (limits is None)
        if legend:
            self.__legend = legend
        else:
            self.__legend = r.TLegend(.2, .825, .8, .925)
        self.__limits = limits
        self.__logplot = logplot
        self.__plots = []
        self.__title = title

    def add(self, plot, legend_title):
        self.__plots.append(plot)

        style = "l"
        if isinstance(plot, r.TProfile) or "data" in legend_title.lower():
            style = "p"
        self.__legend.AddEntry(plot, legend_title, style) 

        xmax = self.find_limit(plot)
        xmin = self.find_limit(plot, False)
        if self.__adjust:
            if self.__limits:
                self.__limits = (
                        min(self.__limits[0], xmin),
                        max(self.__limits[1], xmax))
            else:
                self.__limits = (xmin, xmax)

    def find_limit(self, plot, upper=True):
        nbins = plot.GetNbinsX()
        bins = [plot.GetBinContent(i) for i in range(1, nbins)]

        index = []
        for (i, bin) in enumerate(bins[:-1]):
            index.append(bin > 0 and bins[i + 1] > 0)

        if True not in index:
            index = map(lambda b: b > 0, bins)
        if True not in index:
            return 0

        if upper:
            bound = plot.GetBinLowEdge(nbins + 1 - list(reversed(index)).index(True))
        else:
            bound = plot.GetBinLowEdge(index.index(True) + 1)
        return bound

    def draw(self, pad=r.gPad):
        self.__legend.SetNColumns(
                int(math.ceil(len(self.__plots) / 2.)))

        pad.Divide(1,2)
        pad.GetPad(1).SetPad(0., .333, 1., 1.)
        pad.GetPad(2).SetPad(0., 0., 1., .333)

        pad.cd(1)
        r.gPad.SetBottomMargin(1e-5)
        r.gPad.SetTopMargin(.05)
        r.gPad.SetTickx(2)
        r.gPad.Modified()
        if self.__logplot:
            r.gPad.SetLogy(True)

        first = True
        for plt in reversed(self.__plots):
            if first:
                plt.SetTitle(self.__title)
                plt.SetTitle("")

                xaxis_up = plt.GetXaxis()
                yaxis_up = plt.GetYaxis()
                if self.__limits:
                    xaxis_up.SetRangeUser(*self.__limits)
                yaxis_up.SetTickLength(.02)

                plt.DrawCopy()
                first = False
            else:
                plt.DrawCopy("same")

        self.__legend.Draw()

        pad.cd(2)
        r.gPad.SetBottomMargin(.3)
        r.gPad.SetTopMargin(1e-5)
        r.gPad.SetTickx(1)

        ref = self.__plots[0].Clone()
        rel_plts = []

        ymax, ymin = 1.1, 0.9

        for plt in self.__plots[1:]:
            copy = plt.Clone()
            copy.Divide(ref)
            ymin = min(copy.GetMinimum(.0001), ymin)
            ymax = max(copy.GetMaximum(), ymax)

        r.gPad.SetLogy(True)

        first = True
        for plt in reversed(self.__plots[1:]):
            copy = plt.Clone()
            copy.SetTitle(self.__title)
            copy.SetTitle("")
            copy.Divide(ref)
            if self.__limits:
                copy.GetXaxis().SetRangeUser(*self.__limits)

            if "p" in copy.GetOption().lower():
                copy.SetOption("")
                opt = "hist p"
            else:
                copy.SetOption("")
                opt = "hist l"

            if first:
                xaxis_down = copy.GetXaxis()
                xaxis_down.SetLabelSize(2 * xaxis_up.GetLabelSize())
                xaxis_down.SetTickLength(.06)
                xaxis_down.SetTitleOffset(1.2)
                xaxis_down.SetTitleSize(2 * xaxis_up.GetTitleSize())
                xaxis_down.SetTitle(xaxis_up.GetTitle())

                yaxis_down = copy.GetYaxis()
                yaxis_down.SetTitle("relative")
                yaxis_down.SetTickLength(.03)
                yaxis_down.SetLabelSize(2 * yaxis_up.GetLabelSize())
                yaxis_down.SetTitleOffset(.5)
                yaxis_down.SetTitleSize(2 * yaxis_up.GetTitleSize())
                yaxis_down.SetRangeUser(ymin, ymax)

                copy.DrawCopy(opt)
                first = False
            else:
                copy.DrawCopy("same" + opt)
            rel_plts.append(copy)

        pad.Modified()
        pad.Update()

    def get_legend(self):
        return self.__legend

    def is_logplot(self):
        return self.__logplot

    def set_logplot(self, log):
        self.__logplot = log

    def set_title(self, title):
        self.__title = title

    def get_title(self):
        return self.__title

def create_stack(hists, files, norms=None, adjustlimits=True, limits=None, logplot=False, normalized=True, 
        title=''):
    # l.SetNColumns(min(len(files), 3 if not mc_cmp else 4))

    stack = Plots(logplot=logplot, limits=limits)
    stack_rel = Plots(logplot=logplot, limits=limits)

    for (h, f, n) in zip(hists, files, norms):
        if normalized:
            h.Scale(1. / n)
            h.SetYTitle(h.GetYaxis().GetTitle() + ' / event')

        if title == '':
            title = ";".join((h.GetTitle(),
                    h.GetXaxis().GetTitle(),
                    h.GetYaxis().GetTitle()))

        stack.add(h, f)
        stack.set_title(title)
    return stack

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

    for (n, s) in enumerate(stacks, 1):
        c.cd(n)
        s.draw(c.GetPad(n))
    c.SaveAs(filename)

last_color = 0
colors = {}
counts = {}
modifiers = {
    'hf': 'mod HF',
    '1pv': '1 PV'
}
pileup = {
    '66': 'PU66',
    '45': 'PU45',
    '2012C': '2012C'
}

data_colors = [1, 11, 14, 12]
data_files = []
mc_colors = [2, 8, 9, 6, 7]
mc_files = []

def legend(path, hist):
    """
    Create and return a legend label, normalization, and modified histogram
    based on the latter's path.
    """
    f, dir = path.split(':', 1)
    basedir = dir.lower().strip('/')

    m = re.search(r'plots_([a-zA-Z0-9]+)(?:_([^_]+))?_(?:([a-zA-Z0-9+]+)-)(\w+).root$', f)
    if m:
        (label, mod, tier, pu) = m.groups()
        if label == 'mc':
            label = label.upper()
            if f not in mc_files:
                mc_files.append(f)
            if isinstance(hist, r.TProfile):
                hist.SetOption("P E")
            hist.SetLineColor(mc_colors[mc_files.index(f)])
            hist.SetMarkerColor(mc_colors[mc_files.index(f)])
            hist.SetMarkerStyle(25)
            hist.SetMarkerSize(1)
        elif label == 'data':
            label = label.capitalize()
            if isinstance(hist, r.TProfile):
                hist.SetOption("P E")
            if f not in data_files:
                data_files.append(f)
            hist.SetLineColor(data_colors[data_files.index(f)])
            hist.SetMarkerColor(data_colors[data_files.index(f)])
            hist.SetMarkerStyle(8)
            hist.SetMarkerSize(1)
        else:
            raise

        label += ' ' + pileup[pu]

        if mod:
            label += ' {m}'.format(m=modifiers[mod] if mod in modifiers else mod)
                
    else:
        sys.stderr.write('filename does not match expected pattern: \
                {f}\n'.format(f=f))
        raise

    n = counts[f][0]
    # Hack to get the right normalization for pileup histograms
    if 'pileup' in f:
        hist.Scale(1. / hist.Integral())
        n = 1

    if 'data' in label.lower():
        color = 1
        # hist.SetMarkerSize(3)
        hist.SetMarkerStyle(r.kFullDotMedium)
    elif 'reweighted' in dir.lower():
        label += ' rw.'
        color = 3
    else:
        color = 2

    if mod:
        color += 2

    if mc_cmp:
        if f not in colors:
            globals()['last_color'] += 1
            colors[f] = last_color
        color = colors[f]
        try:
            m = re.search(r'Tune[^_]+', f)
            if not m:
                raise

            label = m.group(0)

            if 'reweighted' in dir.lower():
                label += ' rw.'
        except:
            pass

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

                k = (basedir, key)
                if k not in plot_dict:
                    plot_dict[k] = [] if not subkey else {}
                if subkey:
                    if subkey not in plot_dict[k]:
                        plot_dict[k][subkey] = []
                    plot_dict[k][subkey].append((obj, leg, norm))
                else:
                    plot_dict[k].append((obj, leg, norm))

    for (basedir, key), objs in plots.items():
        ps, ls, ns = zip(*objs) # unzip
        if len(ps) == 0 or type(ps[0]) not in [r.TH1D, r.TH1F, r.TProfile]:
            continue

        norm = not isinstance(ps[0], r.TProfile)
        if key in override_limits:
            s = create_stack(ps, ls, ns, limits=override_limits[key],
                    normalized=norm)
        else:
            s = create_stack(ps, ls, ns, normalized=norm)
        plot_stacks([s], pdffile.format(p=key, d=basedir))
        s.set_logplot(True)
        plot_stacks([s], pdffile.format(p=key + '_log', d=basedir))

    for plot_dict in (plots_digi, plots_tp):
        for ((basedir, key), subdict) in plot_dict.items():
            # limits = (float('inf'), 0)
            # for lst in subdict.values():
                # for tpl in lst:
                    # limits = greater(limits, get_limits(tpl[0]))
            # print key, limits
            for subkey, objs in subdict.items():
                real_key = '_'.join([key, subkey])
                ps, ls, ns = zip(*objs) # unzip
                if len(ps) == 0 or type(ps[0]) not in [r.TH1D, r.TH1F]:
                    continue
                s = create_stack(ps, ls, ns)
                plot_stacks([s], pdffile.format(p=real_key, d=basedir))
                s.set_logplot(True)
                plot_stacks([s], pdffile.format(p=real_key + '_log', d=basedir))

    for ((basedir, key), subdict) in plots_2d.items():
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

                if 'calo' in basedir:
                    quant = 'Region'
                elif 'digi' in basedir or 'trigprim' in basedir:
                    quant = 'Digi'
                elif 'jet' in basedir:
                    quant = 'Jet'
                elif 'rechit' in basedir:
                    quant = 'RecHit'
                elif 'track' in basedir:
                    quant = 'Track'
                else:
                    sys.stderr.write('Please add a quantity assignment for "{k}"\n.'.format(k=basedir))
                    raise

                if not norm_by_event:
                    tmp_ps, ls, ns = zip(*objs)
                    ps = []
                    for (val, mp) in tmp_ps:
                        tmp_v = proj(val)
                        tmp_m = proj(mp)
                        tmp_v.Divide(tmp_m)
                        tmp_v.SetYTitle(val.GetZaxis().GetTitle() + ' / ' + quant)
                        ps.append(tmp_v)
                else:
                    ps, ls, ns = zip(*objs) # unzip
                    ps = map(proj, ps)
                if len(ps) == 0 or type(ps[0]) not in [r.TH1D, r.TH1F]:
                    continue
                s = create_stack(ps, ls, ns, adjustlimits=False, normalized=norm_by_event)
                plot_stacks([s], pdffile.format(p=real_key, d=basedir))
                s.set_logplot(True)
                plot_stacks([s], pdffile.format(p=real_key + '_log', d=basedir))
        
        # print subdict.keys()

if len(sys.argv) < 3:
    sys.stderr.write(
            "usage: {p} output file...\n".format(p=sys.argv[0]))
    sys.exit(1)

summarize(new_args[0], new_args[1:])
