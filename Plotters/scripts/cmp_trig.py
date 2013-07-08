#!/usr/bin/env python

import math
import random
import ROOT as r
import sys

r.gROOT.SetBatch()

def filter_histo(h, fct):
    labels = sorted(
            filter(fct, [(b, h.GetXaxis().GetBinLabel(b)) for b in range(1, h.GetNbinsX() + 1)]),
            key=lambda t: t[1])

    new_h = r.TH1F("new_h_{c}".format(c=random.randrange(1, 1000)), "", len(labels), 0., 1.)
    new_h.SetDirectory(0)

    for (i, (n, l)) in enumerate(labels, 1):
        new_h.GetXaxis().SetBinLabel(i, l)
        new_h.SetBinContent(i, h.GetBinContent(n))
        new_h.SetBinError(i, h.GetBinError(n))

    new_h.SetTitle(";;MC / Data")

    return new_h

def hist_ratio(p1, p2, filter, key):
    print p1
    print p2
    f1 = r.TFile(p1.split(':')[0])
    f2 = r.TFile(p2.split(':')[0])
    h1 = r.gDirectory.Get(p1).Clone()
    h2 = r.gDirectory.Get(p2).Clone()

    for bin in range(1, h1.GetNbinsX() + 1):
        if h1.GetXaxis().GetBinLabel(bin) == key:
            break
    else:
        raise
    print bin

    i = 1 #74
    print h1.GetXaxis().GetBinLabel(i), h1.GetBinContent(i)
    print h2.GetXaxis().GetBinLabel(i), h2.GetBinContent(i)
    print h1.GetXaxis().GetBinLabel(bin), h1.GetBinContent(bin)
    print h2.GetXaxis().GetBinLabel(bin), h2.GetBinContent(bin)

    for i in range(1, h1.GetNbinsX() + 1):
        h1.SetBinError(i, math.sqrt(h1.GetBinContent(i)))
        h2.SetBinError(i, math.sqrt(h2.GetBinContent(i)))

    h1.Scale(1 / h1.GetBinContent(bin))
    h2.Scale(1 / h2.GetBinContent(bin))
    h2.Divide(h1)
    h2.SetDirectory(0)
    return filter_histo(h2, filter)

def plot_ratios(filename, files, data_path, mc_path, filter, logscale=False, key="L1_AlwaysTrue"):
    ts = []
    hs = []
    for (df, mcf, title) in files:
        hs.append(hist_ratio(":".join([df, data_path]), ":".join([mcf, mc_path]), filter, key))
        ts.append(title)

    offset = .05
    n = len(hs)
    dx = .9 / (5 * n)
    width = 4 * dx

    canvas = r.TCanvas("c", "", 3200, 1000)
    legend = r.TLegend(0.3, 0.93, 0.7, 0.98)
    legend.SetNColumns(n)

    r.gPad.SetGrid()
    r.gPad.SetBottomMargin(.4)
    r.gPad.SetRightMargin(.025)
    r.gPad.SetLeftMargin(.05)

    hs[0].SetTitle("")
    if not logscale:
        hs[0].GetYaxis().SetRangeUser(0, 10)
    hs[0].GetXaxis().SetTitle("")
    hs[0].GetYaxis().SetTitle("MC / Data")
    canvas.Range(0, 0, 1, 10)

    ls = []
    rng = range(len(hs))
    mid = rng[-1] * 0.5
    opt = ''
    for (h, c, t, n) in zip(hs, [r.kGreen + 3, r.kRed, r.kRed + 2, r.kBlue + 1, r.kBlue + 3], ts, rng):
        h.SetFillColor(c)
        h.SetBarWidth(width)
        h.SetBarOffset(offset)
        h.SetYTitle("MC / Data")
        h.GetXaxis().LabelsOption("v")
        # h.GetXaxis().SetLabelSize(2 * h.GetXaxis().GetLabelSize())
        h.Draw('hist bar2' + opt)
        legend.AddEntry(h, t, "f")

        for bin in range(h.GetNbinsX() + 1):
            x = h.GetXaxis().GetBinCenter(bin) + (n - mid) * h.GetBinWidth(bin) / len(rng) * 0.9
            y = h.GetBinContent(bin)
            err = h.GetBinError(bin)

            l = r.TLine(x, min(y - err, 10), x, min(y + err, 10))
            l.Draw()
            ls.append(l)

        offset += 5 * dx
        if 'same' not in opt:
            opt += 'same'

    line = r.TLine(0, 1, 1, 1)
    line.SetLineWidth(1)
    line.Draw()

    legend.Draw()
    canvas.SetLogy(logscale)
    canvas.SaveAs(filename)

files_vlpu = [
        ("plots_data_raw+reco-none.root", "plots_mc_raw+reco-none.root", "VLPU"),
        ("plots_data_raw+reco-none.root", "plots_mc_raw+reco-nonehf.root", "VLPU mod HF"),
        ]

files_noE = [
        ("plots_data_raw+reco-2012CnoE.root", "plots_mc_raw+reco-2012CnoE.root", "2012C"),
        # ("plots_data_raw+reco-2012CnoE.root", "plots_mc_raw+reco-2012CextnoE.root", "2012C 200ns"),
        ("plots_data_raw+reco-2012CnoE.root", "plots_mc_raw+reco-2012Cext2noE.root", "2012C 300ns"),
        ("plots_data_raw+reco-2012CnoE.root", "plots_mc_raw+reco-2012Cext3noE.root", "2012C 300ns (new noise model)"),
        ]

files_noH = [
        ("plots_data_raw+reco-2012CnoH.root", "plots_mc_raw+reco-2012CnoH.root", "2012C"),
        # ("plots_data_raw+reco-2012CnoH.root", "plots_mc_raw+reco-2012CextnoH.root", "2012C 200ns"),
        ("plots_data_raw+reco-2012CnoH.root", "plots_mc_raw+reco-2012Cext2noH.root", "2012C 300ns"),
        ("plots_data_raw+reco-2012CnoH.root", "plots_mc_raw+reco-2012Cext3noH.root", "2012C 300ns (new noise model)"),
        ("plots_data_raw+reco-2012C.root", "plots_mc_raw+reco-2012Cext3_clean.root", "2012C 300ns (new noise model, cleaned)"),
        ]

files = [
        ("plots_data_raw+reco-2012C.root", "plots_mc_raw+reco-2012C.root", "2012C"),
        # ("plots_data_raw+reco-2012C.root", "plots_mc_raw+reco-2012Cext.root", "2012C 200ns"),
        ("plots_data_raw+reco-2012C.root", "plots_mc_raw+reco-2012Cext2.root", "2012C 300ns"),
        ("plots_data_raw+reco-2012C.root", "plots_mc_raw+reco-2012Cext3.root", "2012C 300ns (new noise model)"),
        ("plots_data_raw+reco-2012C.root", "plots_mc_raw+reco-2012Cext3_clean.root", "2012C 300ns (new noise model, cleaned)"),
        # ("plots_data_raw+reco-45.root", "plots_mc_raw+reco-45.root", "PU 45"),
        # ("plots_data_raw+reco-66.root", "plots_mc_raw+reco-66.root", "PU 66"),
        ]

r.gStyle.SetOptStat(False)

reg_filter = lambda (n, l): (l.count("_") < 2 or "jet" in l.lower()) and not (l.endswith("er") or "SingleMu" in l.lower() or ("SingleEG" in l and not "EG20" in l))

plot_ratios("cmp/pu_reweighed.eps", files, "/trigPlotter/trig_bits", "/reWeightedTrigPlotter/trig_bits", reg_filter)
plot_ratios("cmp/pu_reemulated.eps", files, "/reEmulTrigPlotter/trig_bits", "/reWeightedReEmulTrigPlotter/trig_bits", reg_filter)
plot_ratios("cmp/pu_noE_reemulated.eps", files_noE, "/reEmulTrigPlotter/trig_bits", "/reWeightedReEmulTrigPlotter/trig_bits", reg_filter)
plot_ratios("cmp/pu_noH_reemulated.eps", files_noH, "/reEmulTrigPlotter/trig_bits", "/reWeightedReEmulTrigPlotter/trig_bits", reg_filter)
plot_ratios("cmp/pu_reweighed_full.eps", files, "/trigPlotter/trig_bits", "/reWeightedTrigPlotter/trig_bits", lambda (n, l): True)
plot_ratios("cmp/pu_reemulated_full.eps", files, "/reEmulTrigPlotter/trig_bits", "/reWeightedReEmulTrigPlotter/trig_bits", lambda (n, l): True)
# plot_ratios("cmp/vlpu.eps", files_vlpu, "/trigPlotter/trig_bits", "/trigPlotter/trig_bits", lambda (n, l): True)
# plot_ratios("cmp/vlpu_log.eps", files_vlpu, "/trigPlotter/trig_bits", "/trigPlotter/trig_bits", lambda (n, l): True, True)
# plot_ratios("vlpu_reemulated.png", files_vlpu, "/reEmulTrigPlotter/trig_bits", "/reEmulTrigPlotter/trig_bits", lambda (n, l): True)
