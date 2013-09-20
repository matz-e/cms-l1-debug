#!/usr/bin/env python

reemulated = True
reweighed = True
unweighed = True
unemulated = True
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
import random
import re
import ROOT as r
import yaml

r.gROOT.SetBatch()
r.gErrorIgnoreLevel = 1001
r.gROOT.SetStyle('Modern')

r.gStyle.SetTitleBorderSize(0)
r.gStyle.SetOptStat(0)
# r.gStyle.SetTitleAlign(22)

def rebin(fn):
    """Determine if a plot saved with filename `fn` should be rebinned."""
    if re.search(r'_en_tot_vtx_[be]', fn):
        return False
    return True

class CustomLimits:
    def __init__(self, map):
        self.__dict = map
    def __contains__(self, key):
        if self.__getitem__(key):
            return True
        return False
    def __getitem__(self, key):
        for (k, v) in self.__dict.items():
            if k.search(key.lower()):
                return v
        return None

override_limits = CustomLimits({
    re.compile('ecal_en_tot'): (0, 750),
    re.compile('cal_time'): (-100, 100)
    })
override_ratio_limits = CustomLimits({
    re.compile('gct'): (0.1, 7.2),
    re.compile('caloregion'): (0.1, 7.2)
    })

class Plots:
    def __init__(self, title='', legend=None, logplot=False,
            limits=None, ratio_limits=None, adjust=False):
        self.__adjust = adjust or (limits is None)
        if legend:
            self.__legend = legend
        else:
            self.__legend = r.TLegend(.12, .9, .88, 1.)
        self.__limits = limits
        self.__logplot = logplot
        self.__plots = []
        self.__ratio_limits = ratio_limits
        self.__title = title

    def __del__(self):
        for p in self.__plots:
            del p
        del self.__legend

    def __len__(self):
        return len(self.__plots)

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
            if upper:
                index.append(bin > pmin and bins[i + 1] > pmin)
            else:
                index.append(bin > pmin)

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

    def draw(self, pad=r.gPad, rebin=True):
        # find optimal legend column count: between 4 and 2, optimally
        # higher and all rows as full as possible
        mods = {}
        for i in range(3, 1, -1):
            m = len(self.__plots) % i
            if m != 0:
                m = 3 - m # number of empty legend slots
            if m not in mods:
                mods[m] = i
        width = mods[min(mods.keys())]
        self.__legend.SetNColumns(width)
        height = math.ceil(len(self.__plots) / float(width))
        self.__legend.SetY1(self.__legend.GetY2() - (0.1, .085, .07)[width - 1] * height)

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
        if rebin:
            drawn_plots = []
            first = True
            for plt in self.__plots:
                if first:
                    xaxis = plt.GetXaxis()
                    if self.__limits:
                        ratio = xaxis.GetNbins() * \
                                float.__rsub__(*map(float, self.__limits)) / \
                                (xaxis.GetXmax() - xaxis.GetXmin()) / \
                                80.
                    else:
                        ratio = xaxis.GetNbins() / 80.

                    ratio = max(1, int(ratio))

                    while xaxis.GetNbins() % ratio != 0:
                        ratio += 1

                    drawn_plots.append(plt.Rebin(ratio))
                    first = False
                else:
                    drawn_plots.append(plt.Rebin(ratio))
        else:
            drawn_plots = self.__plots

        # now determine y-axis plotting range
        ymax, ymin = 0., float("inf")
        for plt in drawn_plots:
            ymin = min(self.get_min(plt), ymin)
            ymax = max(self.get_max(plt), ymax)

        if not self.__logplot:
            ymin = 0.
        else:
            ymax *= 10.

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
                yaxis_up.SetRangeUser(ymin * .5, ymax * 1.3)

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

        # if ymax / ymin > 10. and ymax > 20.:
            # r.gPad.SetLogy(True)
            # ymax *= 2.
            # ymin *= .7
        # else:
            # ymax *= 1.1
            # ymin *= 0.9

        if not self.__ratio_limits:
            ymax = 5
            ymin = 0.45
        else:
            ymin, ymax = self.__ratio_limits

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
            del copy

        pad.Modified()
        pad.Update()

    def set_logplot(self, log):
        self.__logplot = log

    def set_title(self, title):
        self.__title = title

def create_stack(hists, files, norms=None, adjustlimits=True, limits=None,
        ratio_limits=None, logplot=False, normalized=True, title=''):
    # l.SetNColumns(min(len(files), 3 if not mc_cmp else 4))

    stack = Plots(logplot=logplot, limits=limits, ratio_limits=ratio_limits)

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

    if len(stacks[0]) == 0:
        return

    for (n, s) in enumerate(stacks, 1):
        c.cd(n)
        s.draw(c.GetPad(n), rebin=rebin(filename))
    c.SaveAs(filename)

def save_single_plot(hists, legends, filename, ranges):
    c = r.TCanvas("c", "", 600 * len(hists), 600)
    c.Divide(len(hists), 1)

    max = None
    for (reg, val) in ranges:
        if re.search(reg, filename):
            max = val
            break

    for (n, l, h) in zip(range(len(hists)), legends, hists):
        c.cd(n + 1)
        h.SetTitle(l)
        # max = 300
        # if "data" in l.lower() or "mc" in l.lower():
            # max = 200
        # if "num" in filename.lower():
            # max = 30
        if max:
            h.GetXaxis().SetRangeUser(0, max)
            h.GetYaxis().SetRangeUser(0, max)
        c.GetPad(n + 1).SetLogz()
        h.Draw("COLZ")

        if max:
            f = r.TF1("f" + str(n), "x", 0, max)
            f.DrawCopy("same")
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    c.SaveAs(filename)

last_color = 0
colors = {}
counts = {}
modifiers = {
    'hf': 'mod HF',
    '1pv': '1 PV'
}

data_files = []
data_markers = [r.kFullDotLarge, r.kFullSquare, r.kFullTriangleUp, r.kFullTriangleDown]
mc_files = []

def fix_histo(path, hist):
    """
    Create and return a legend label, normalization, and modified histogram
    based on the latter's path.
    """
    f, dir = path.split(':', 1)
    basedir = dir.lower().strip('/')

    # XXX ugly hack to correct rechit labelling
    if 'transverse' in basedir and 'rechit' in basedir:
        hist.GetYaxis().SetTitle(
                hist.GetYaxis().GetTitle().replace("E", "E_{T}"))
        hist.GetXaxis().SetTitle(
                hist.GetXaxis().GetTitle().replace("E", "E_{T}"))

    m = re.search(r'(?:standalone_)?plots_([a-zA-Z0-9]+)[_.]', f)
    if m:
        (label,) = m.groups()
        if label == 'mc':
            label = label.upper()
            if f not in mc_files:
                mc_files.append(f)
            if isinstance(hist, r.TProfile):
                hist.SetOption("PE")
            if 'reemul' in basedir and unemulated:
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
            hist.SetMarkerStyle(data_markers[data_files.index(f) % len(data_markers)])
            # if 'reemul' in basedir:
                # hist.SetMarkerStyle(r.kFullTriangleUp)
            # else:
                # hist.SetMarkerStyle(r.kFullDotLarge)
            hist.SetMarkerSize(.5)
        else:
            raise


    else:
        sys.stderr.write('filename does not match expected pattern: \
                {f}\n'.format(f=f))
        raise

    if 'reemul' in basedir:
        if unemulated:
            hist.SetLineStyle(r.kDotted)

    if 'reweighted' in basedir:
        if reweighed and unweighed and unemulated:
            hist.SetLineStyle(r.kDashed)

    if 'reemul' in basedir and 'reweighted' in basedir and reweighed and unweighed and unemulated:
        hist.SetLineStyle(r.kDashDotted)


    return hist

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
        c_rw = hist_rw.Integral()

    return (c, c_rw)

    hist = r.gDirectory.Get('{f}:gctPlotter/et_tot'.format(f=fn))
    hist_rw = r.gDirectory.Get('{f}:reWeightedGctPlotter/et_tot'.format(f=fn))
    if hist:
        c = hist.GetEntries()
    if hist_rw:
        c_rw = hist_rw.Integral()

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
        elif 'digi' in filename and 'vtx' in filename:
            return NOPLOT
        elif 'all' in filename.lower() or re.search(r'\d\d_\d', filename):
            return NOPLOT
        return LOGPLOT
    return LOGPLOT|REGPLOT

class FixedProj:
    def __init__(self, proj):
        self.__proj = proj
    def __call__(self, hist):
        p = self.__proj(hist).Clone()
        p.SetYTitle(hist.GetZaxis().GetTitle())
        return p

projs = {'ieta': FixedProj(r.TH2.ProjectionX),
         'iphi': FixedProj(r.TH2.ProjectionY)}

def plot_directory(pattern, basepath, files, ranges=None):
    nfiles = []
    for tpl in files:
        f = r.TFile(tpl[0])
        if not f.IsOpen():
            continue
        nfiles.append([f] + tpl)
    files = nfiles

    counts = {}
    for (file, fn, leg, col, paths) in files:
        counts[fn] = get_num_events(fn)

    idx = 0
    paths = []

    while idx < len(files) and basepath not in paths:
        (file, basefile, leg, col, paths) = files[idx]
        idx += 1
    if idx > len(files) or basepath not in paths:
        return

    basedir = file.Get(paths[basepath])
    for k in basedir.GetListOfKeys():
        key = k.GetName()

        mode = which_plots(pattern.format(d=basepath.lower(), p=key))
        if mode == NOPLOT:
            continue

        hists, legends, norms = [], [], []
        for (file, fn, leg, col, paths) in files:
            if basepath not in paths:
                sys.stderr.write("Skipping path {0} for file {1}\n".format(basepath, fn))
                continue

            obj = file.Get(paths[basepath] + "/" + key)
            if not obj:
                sys.stderr.write("Can't find {p}/{k} in {f}\n".format(p=paths[basepath], k=key, f=fn))
                continue

            o = fix_histo(fn + ':' + basepath, obj)
            o.SetMarkerColor(col)
            o.SetLineColor(col)
            # o.SetFillColor(col)
            norms.append(counts[fn][0])
            hists.append(o)
            legends.append(leg)

        # trigger stuff is dealt with in `cmp_trig.py`
        if key == 'trig_bits':
            continue

        if len(hists) == 0:
            sys.stderr.write("No histograms for: {p}/{k}\n".format(p=path, k=key))
            continue

        if not isinstance(hists[0], r.TH2):
            s = create_stack(hists, legends, norms,
                    normalized=not isinstance(hists[0], r.TProfile),
                    limits=override_limits[key] if key in override_limits else None,
                    ratio_limits=override_ratio_limits[basepath] if basepath in override_ratio_limits else None)
            if mode & REGPLOT:
                plot_stacks([s], pattern.format(p=key, d=basepath.lower()))
            if mode & LOGPLOT:
                s.set_logplot(True)
                plot_stacks([s], pattern.format(p=key + "_log", d=basepath.lower()))
        else:
            if not key.endswith("_mp"):
                newkey = "_".join([key.rsplit("_", 1)[0], "mp"])
                norm_hists = []
                for (file, fn, leg, col, paths) in files:
                    if basepath not in paths:
                        continue

                    obj = file.Get(paths[basepath] + "/" + newkey)
                    if not obj:
                        sys.stderr.write("Can't find {p}/{k} in {f}\n".format(p=paths[basepath], k=newkey, f=fn))
                        continue
                    norm_hists.append(obj)

                if len(norm_hists) == 0:
                    save_single_plot(
                            hists,
                            legends,
                            pattern.format(p=key, d=basepath.lower()),
                            ranges)
                    continue

                for (axis, proj) in projs.items():
                    if 'calo' in basepath.lower() or basepath == 'cr':
                        quant = 'Region'
                    elif 'digi' in basepath.lower() or 'trigprim' in basepath.lower() or basepath == 'tpd':
                        quant = 'Digi'
                    elif 'jet' in basepath.lower():
                        quant = 'Jet'
                    elif 'rechit' in basepath.lower() or 'rh' in basepath:
                        quant = 'RecHit'
                    elif 'track' in basepath.lower():
                        quant = 'Track'
                    else:
                        sys.stderr.write('Please add a quantity assignment for "{k}"\n.'.format(k=basepath))
                        raise

                    nhists = []
                    for (h, n) in zip(map(proj, hists), map(proj, norm_hists)):
                        h.Divide(n)
                        # h.SetYTitle(val.GetZaxis().GetTitle() + ' / ' + quant)
                        nhists.append(h)

                    s = create_stack(nhists, legends, norms, normalized=False,
                            limits=override_limits[key] if key in override_limits else None,
                            ratio_limits=override_ratio_limits[basepath] if basepath in override_ratio_limits else None)
                    if mode & REGPLOT:
                        plot_stacks([s], pattern.format(p=key + "_" + axis + "_mp", d=basepath.lower()))
                    if mode & LOGPLOT:
                        s.set_logplot(True)
                        plot_stacks([s], pattern.format(p=key + "_" + axis + "_mp_log", d=basepath.lower()))

            for (axis, proj) in projs.items():
                phists = map(proj, hists)
                s = create_stack(phists, legends, norms, normalized=True,
                        limits=override_limits[key] if key in override_limits else None,
                        ratio_limits=override_ratio_limits[basepath] if basepath in override_ratio_limits else None)
                if mode & REGPLOT:
                    plot_stacks([s], pattern.format(p=key + "_" + axis, d=basepath.lower()))
                if mode & LOGPLOT:
                    s.set_logplot(True)
                    plot_stacks([s], pattern.format(p=key + "_" + axis + "_log", d=basepath.lower()))

def get_color(o):
    if isinstance(o, str):
        for c in r.gROOT.GetListOfColors():
            if c.GetName() == o:
                return c.GetNumber()
        # FIXME throw proper exception
        sys.stderr.write(o + "\n")
        raise
    elif isinstance(o, int):
        return o
    else:
        # FIXME throw proper exception
        raise

import optparse
parser = optparse.OptionParser(usage="%prog [options] file")
parser.add_option("-n", metavar="N", action="store", default=None,
        type="int", dest="n", help="only process configuration part N")
(opts, args) = parser.parse_args()

if len(args) != 1:
    parser.error("need to specifiy exactly one configuration file")

configs = yaml.load_all(open(args[0]))

if opts.n:
    configs = [list(configs)[opts.n]]

for config in configs:
    if not "custom ranges" in config:
        config["custom ranges"] = []

    # convert colors
    for tpl in config['files']:
        tpl[2] = get_color(tpl[2])
    for p in config['paths']:
        plot_directory(config['output pattern'], p, config['files'],
                config['custom ranges'])
