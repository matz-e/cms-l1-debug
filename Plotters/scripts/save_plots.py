#!/usr/bin/env python

reweighed = True
unweighed = True
plot_only = ""

# Argument parsing
# vvv

import re
import sys

new_args = []
for arg in sys.argv[1:]:
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

sys.argv = [sys.argv[0]] + new_args

NOPLOT = 0b00
LOGPLOT = 0b01
REGPLOT = 0b10

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

class CustomLimits:
    def __init__(self, map):
        self.__dict = map
    def __contains__(self, key):
        if self.__getitem__(key):
            return True
        return False
    def __getitem__(self, key):
        for (k, v) in self.__dict.items():
            if k.search(key):
                return v
        return None

override_limits = CustomLimits({
        re.compile('ecal_en_tot'): (0, 750),
        re.compile('cal_time'): (-100, 100)
        })

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

    def find_x_limits(self):
        if not self.__adjust:
            return self.__limits

        self.__limits = [float("inf"), float("-inf")]

        frac = .0 if self.__logplot else .05

        for plot in self.__plots:
            xmax = self.find_limit(plot, frac=frac)
            xmin = self.find_limit(plot, False, frac=frac)
            if self.__limits:
                self.__limits = (
                        min(self.__limits[0], xmin),
                        max(self.__limits[1], xmax))
        return self.__limits

    def add(self, plot, legend_title):
        self.__plots.append(plot)

        style = "l"
        if isinstance(plot, r.TProfile) or "p" in plot.GetOption().lower():
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

    def find_limit(self, plot, upper=True, frac=0):
        nbins = plot.GetNbinsX()
        bins = [plot.GetBinContent(i) for i in range(1, nbins)]
        # pmax = plot.GetMaximum()
        pmin = frac * max([p.GetBinContent(p.GetMaximumBin()) for p in self.__plots])

        index = []
        for (i, bin) in enumerate(bins[:-1]):
            index.append(bin > pmin and bins[i + 1] > pmin)

        if True not in index:
            index = map(lambda b: b > pmin, bins)
        if True not in index:
            return 0

        if upper:
            bound = plot.GetBinLowEdge(nbins + 1 - list(reversed(index)).index(True))
        else:
            bound = plot.GetBinLowEdge(index.index(True) + 1)
        return bound

    def get_max(self, plt):
        return self.get_ex(plt, max, float.__gt__, 1.5, "-inf")

    def get_min(self, plt):
        return self.get_ex(plt, min, float.__lt__, .75, "inf")

    def get_ex(self, plt, cmp, op, f, default):
        contents = filter(lambda x: x > 0,
                [plt.GetBinContent(i + 1) for i in range(plt.GetNbinsX())])
        if len(contents) == 0:
            return float(default)

        omin = cmp(contents)
        pmin = cmp(contents)
        while len(contents) > plt.GetNbinsX() * .66:
            idx = contents.index(pmin)
            others = []
            if idx > 0:
                others.append(contents[idx - 1])
            if idx < len(contents) - 1:
                others.append(contents[idx + 1])
            if op(cmp(others), f * pmin):
                return pmin
            contents.remove(pmin)
            pmin = cmp(contents)
        return omin

    def draw(self, pad=r.gPad):
        # find optimal legend column count: between 4 and 2, optimally
        # higher and all rows as full as possible
        mods = {}
        for i in range(4, 1, -1):
            m = len(self.__plots) % i
            if m not in mods:
                mods[m] = i
        self.__legend.SetNColumns(mods[min(mods.keys())])
        height = math.ceil(len(self.__plots) / mods[min(mods.keys())])
        self.__legend.SetY1(self.__legend.GetY2() - .05 * height)

        pad.Divide(1,2)
        pad.GetPad(1).SetPad(0., .333, 1., 1.)
        pad.GetPad(2).SetPad(0., 0., 1., .333)

        pad.cd(1)
        r.gPad.SetBottomMargin(1e-5)
        r.gPad.SetTopMargin(.05)
        r.gPad.SetTickx(2)
        r.gPad.Modified()
        self.find_x_limits()
        if self.__logplot:
            r.gPad.SetLogy(True)

        # first rebin, then determine limits
        drawn_plots = []
        first = True
        for plt in self.__plots:
            if first:
                if self.__limits:
                    xaxis = plt.GetXaxis()
                    ratio = xaxis.GetNbins() * \
                            float.__rsub__(*map(float, self.__limits)) / \
                            (xaxis.GetXmax() - xaxis.GetXmin()) / \
                            80.
                else:
                    ratio = xaxis_up.GetNbins() / 80.
                ratio = max(1, int(ratio))
                drawn_plots.append(plt.Rebin(ratio))
                first = False
            else:
                drawn_plots.append(plt.Rebin(ratio))

        # now determine y-axis plotting range
        ymax, ymin = 0., float("inf")
        for plt in drawn_plots:
            ymin = min(self.get_min(plt), ymin)
            ymax = max(self.get_max(plt), ymax)

        if not self.__logplot:
            ymin = 0.
        else:
            ymax *= 4.

        first = True
        for plt in reversed(drawn_plots):
            if "p" in plt.GetOption().lower():
                # plt.SetOption("")
                opt = "p"
            else:
                # plt.SetOption("")
                opt = ""

            if first:
                plt.SetTitle(self.__title)
                plt.SetTitle("")

                xaxis_up = plt.GetXaxis()
                yaxis_up = plt.GetYaxis()
                yaxis_up.SetTickLength(.02)
                yaxis_up.SetRangeUser(ymin * .5, ymax * 1.2)

                if self.__limits:
                    xaxis_up.SetRangeUser(*self.__limits)

                # plt.DrawCopy(plt.GetOption())
                plt.DrawCopy("hist" + opt)
                # plt.DrawCopy()
                first = False
            else:
                # plt.DrawCopy("same" + plt.GetOption())
                plt.DrawCopy("same hist" + opt)
                # plt.DrawCopy("same")

        self.__legend.Draw()

        pad.cd(2)
        r.gPad.SetBottomMargin(.3)
        r.gPad.SetTopMargin(1e-5)
        r.gPad.SetTickx(1)

        ref = drawn_plots[0].Clone()
        ymax, ymin = 0., float("inf")
        for plt in drawn_plots[1:]:
            copy = plt.Clone()
            copy.Divide(ref)
            ymin = min(self.get_min(copy), ymin)
            ymax = max(self.get_max(copy), ymax)

        if ymax / ymin > 10.:
            r.gPad.SetLogy(True)
            ymax *= 2.
            ymin *= .7
        else:
            ymax *= 1.1
            ymin *= 0.9

        first = True
        for plt in reversed(drawn_plots[1:]):
            copy = plt.Clone()
            copy.SetTitle(self.__title)
            copy.SetTitle("")
            copy.Divide(ref)
            if self.__limits:
                copy.GetXaxis().SetRangeUser(*self.__limits)

            if "p" in plt.GetOption().lower():
                # copy.SetOption("")
                opt = "p"
            else:
                # copy.SetOption("")
                opt = ""

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

                copy.DrawCopy("hist" + opt)
                # copy.DrawCopy()
                first = False
            else:
                copy.DrawCopy("same hist" + opt)
                # copy.DrawCopy("same")

        pad.Modified()
        pad.Update()

    def set_logplot(self, log):
        self.__logplot = log

    def set_title(self, title):
        self.__title = title

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
    '2012C': '2012C',
    '2012Cext': '2012C 200ns',
    '2012Cext2': '2012C 300ns',
    'front': '2012C front',
    'back': '2012C back'
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

    # XXX ugly hack to correct rechit labelling
    if 'transverse' not in basedir and 'rechit' in basedir:
        hist.GetYaxis().SetTitle(
                hist.GetYaxis().GetTitle().replace("E_{T}", "E"))
        hist.GetXaxis().SetTitle(
                hist.GetXaxis().GetTitle().replace("E_{T}", "E"))

    m = re.search(r'plots_([a-zA-Z0-9]+)(?:_([^_]+))?_(?:([a-zA-Z0-9+]+)-)(\w+).root$', f)
    if m:
        (label, mod, tier, pu) = m.groups()
        if label == 'mc':
            label = label.upper()
            if f not in mc_files:
                mc_files.append(f)
            if isinstance(hist, r.TProfile):
                hist.SetOption("PE")
            hist.SetLineColor(mc_colors[mc_files.index(f)])
            hist.SetMarkerColor(mc_colors[mc_files.index(f)])
            if 'reemul' in basedir:
                hist.SetMarkerStyle(r.kOpenDiamond)
            elif 'reweighted' in basedir and reweighed and unweighed:
                hist.SetMarkerStyle(r.kOpenCross)
            else:
                hist.SetMarkerStyle(r.kOpenSquare)
            hist.SetMarkerSize(.8)
        elif label == 'data':
            label = label.capitalize()
            if isinstance(hist, r.TProfile):
                hist.SetOption("PE")
            # else:
                # hist.SetOption("P")
            if f not in data_files:
                data_files.append(f)
            hist.SetLineColor(data_colors[data_files.index(f)])
            hist.SetMarkerColor(data_colors[data_files.index(f)])
            if 'reemul' in basedir:
                hist.SetMarkerStyle(r.kFullTriangleUp)
            elif 'reweighted' in basedir:
                hist.SetMarkerStyle(r.kFullSquare)
            else:
                hist.SetMarkerStyle(r.kFullDotLarge)
            hist.SetMarkerSize(.5)
        else:
            raise

        label += ' ' + pileup[pu]

        if mod:
            label += ' {m}'.format(m=modifiers[mod] if mod in modifiers else mod)
    else:
        sys.stderr.write('filename does not match expected pattern: \
                {f}\n'.format(f=f))
        raise

    if 'reemul' in basedir:
        basedir = basedir.replace('reemul', '')
        hist.SetLineStyle(r.kDotted)
        label += ' reemul.'

    if 'reweighted' in basedir:
        basedir = basedir.replace('reweighted', '')
        label += ' rw.'
        if reweighed and unweighed:
            hist.SetLineStyle(r.kDashed)

    n = counts[f][0]
    # Hack to get the right normalization for pileup histograms
    if 'pileup' in f:
        hist.Scale(1. / hist.Integral())
        n = 1

    return label, n, basedir, hist

def get_num_events(fn):
    """
    Determine the number of events and sum of weights in file ``fn``.  Uses
    L1 energy sums or number of vertices for this.
    """
    c, c_rw = (0, 0)

    hist = r.gDirectory.Get('{f}:trackPlotter/vertices'.format(f=fn))
    hist_rw = r.gDirectory.Get('{f}:reWeightedTrackPlotter/vertices'.format(f=fn))
    if hist:
        c = hist.GetEntries()
    if hist_rw:
        c_rw = hist.Integral()
    
    return (c, c_rw)
    
    hist = r.gDirectory.Get('{f}:gctPlotter/et_tot'.format(f=fn))
    hist_rw = r.gDirectory.Get('{f}:reWeightedGctPlotter/et_tot'.format(f=fn))
    if hist:
        c = hist.GetEntries()
    if hist_rw:
        c_rw = hist.Integral()

    if c != 0:
        return (c, c_rw)

def which_plots(filename):
    """Returns whether regular and logplots should be done.

    >>> which_plots('digiplotter', 'hcal_digi')
    LOGPLOT
    """
    if 'digi' in filename or 'rechit' in filename:
        if 'dist' in filename or 'tot' in filename:
            return REGPLOT
        elif 'time' in filename:
            return LOGPLOT
        elif 'all' in filename.lower() or re.search(r'\d\d_\d', filename):
            return NOPLOT
        return LOGPLOT
    return LOGPLOT|REGPLOT

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

                mode = which_plots(pdffile.format(d=path.lower().split(':', 1)[1], p=key))
                if mode == NOPLOT:
                    continue
                if 'reweighted' in path.lower():
                    if not reweighed:
                        continue
                else:
                    if not unweighed and '_mc_' in path.lower():
                        continue

                obj = k.ReadObj()
                leg, norm, basedir, obj = legend(path, obj)

                if not re.match(plot_only, basedir, re.IGNORECASE):
                    continue

                if obj.GetEntries() == 0:
                    print "{k} in {p} empty!".format(k=key, p=path)
                    continue

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
        mode = which_plots(pdffile.format(d=basedir, p=key))
        if mode == NOPLOT:
            continue

        ps, ls, ns = zip(*objs) # unzip
        if len(ps) == 0 or type(ps[0]) not in [r.TH1D, r.TH1F, r.TProfile]:
            continue

        norm = not isinstance(ps[0], r.TProfile)
        if key in override_limits:
            s = create_stack(ps, ls, ns, limits=override_limits[key],
                    normalized=norm)
        else:
            s = create_stack(ps, ls, ns, normalized=norm)

        if mode & REGPLOT:
            plot_stacks([s], pdffile.format(p=key, d=basedir))
        if mode & LOGPLOT:
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
                mode = which_plots(pdffile.format(d=basedir, p=real_key))
                if mode == NOPLOT:
                    continue

                real_key = '_'.join([key, subkey])
                ps, ls, ns = zip(*objs) # unzip
                if len(ps) == 0 or type(ps[0]) not in [r.TH1D, r.TH1F]:
                    continue
                s = create_stack(ps, ls, ns)
                if mode & REGPLOT:
                    plot_stacks([s], pdffile.format(p=real_key, d=basedir))
                if mode & LOGPLOT:
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
                mode = which_plots(pdffile.format(d=basedir, p=key + '_' + subkey))
                if mode == NOPLOT:
                    continue

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
                if mode & REGPLOT:
                    plot_stacks([s], pdffile.format(p=real_key, d=basedir))
                if mode & LOGPLOT:
                    s.set_logplot(True)
                    plot_stacks([s], pdffile.format(p=real_key + '_log', d=basedir))

if len(new_args) < 2:
    sys.stderr.write(
            "usage: {p} output file...\n".format(p=sys.argv[0]))
    sys.exit(1)

summarize(new_args[0], new_args[1:])
