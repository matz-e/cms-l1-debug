#!/usr/bin/env python

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

    return new_h

def hist_ratio(p1, p2, filter):
    print p1
    print p2
    f1 = r.TFile(p1.split(':')[0])
    f2 = r.TFile(p2.split(':')[0])
    h1 = r.gDirectory.Get(p1).Clone()
    h2 = r.gDirectory.Get(p2).Clone()

    for bin in range(1, h1.GetNbinsX() + 1):
        if h1.GetXaxis().GetBinLabel(bin) == "L1_SingleEG20":
            break
    else:
        raise
    print bin

    i = 1 #74
    print h1.GetXaxis().GetBinLabel(i), h1.GetBinContent(i)
    print h2.GetXaxis().GetBinLabel(i), h2.GetBinContent(i)

    h1.Scale(1 / h1.GetBinContent(bin))
    h2.Scale(1 / h2.GetBinContent(bin))
    h2.Divide(h1)
    h2.SetDirectory(0)
    return filter_histo(h2, filter)

def plot_ratios(filename, files, data_path, mc_path, filter, logscale=False):
    ts = []
    hs = []
    for (df, mcf, title) in files:
        hs.append(hist_ratio(":".join([df, data_path]), ":".join([mcf, mc_path]), filter))
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
    r.gPad.SetLeftMargin(.025)

    hs[0].SetTitle("")
    if not logscale:
        hs[0].GetYaxis().SetRangeUser(0, 10)
    hs[0].GetXaxis().SetTitle("")

    opt = 'bar2'
    for (h, c, t) in zip(hs, [r.kGreen + 3, r.kRed, r.kRed + 2, r.kBlue + 1, r.kBlue + 3], ts):
        h.SetFillColor(c)
        h.SetBarWidth(width)
        h.SetBarOffset(offset)
        h.Draw(opt)
        legend.AddEntry(h, t, "f")

        offset += 5 * dx
        if 'same' not in opt:
            opt += 'same'

    legend.Draw()
    canvas.SetLogy(logscale)
    canvas.SaveAs(filename)

files_vlpu = [
        ("plots_data_raw+reco-none.root", "plots_mc_raw+reco-none.root", "VLPU"),
        ("plots_data_raw+reco-none.root", "plots_mc_raw+reco-nonehf.root", "VLPU mod HF"),
        ]

files = [
        ("plots_data_raw+reco-2012C.root", "plots_mc_raw+reco-2012C.root", "2012C"),
        ("plots_data_raw+reco-2012C.root", "plots_mc_raw+reco-2012Cext.root", "2012C 200ns"),
        ("plots_data_raw+reco-2012C.root", "plots_mc_raw+reco-2012Cext2.root", "2012C 300ns"),
        ("plots_data_raw+reco-45.root", "plots_mc_raw+reco-45.root", "PU 45"),
        ("plots_data_raw+reco-66.root", "plots_mc_raw+reco-66.root", "PU 66"),
        ]

plot_ratios("cmp/pu_reweighed.eps", files, "/trigPlotter/trig_bits", "/reWeightedTrigPlotter/trig_bits", lambda (n, l): l.count("_") < 2)
plot_ratios("cmp/pu_reemulated.eps", files, "/reEmulTrigPlotter/trig_bits", "/reWeightedReEmulTrigPlotter/trig_bits", lambda (n, l): l.count("_") < 2)
plot_ratios("cmp/vlpu.eps", files_vlpu, "/trigPlotter/trig_bits", "/trigPlotter/trig_bits", lambda (n, l): True)
plot_ratios("cmp/vlpu_log.eps", files_vlpu, "/trigPlotter/trig_bits", "/trigPlotter/trig_bits", lambda (n, l): True, True)
# plot_ratios("vlpu_reemulated.png", files_vlpu, "/reEmulTrigPlotter/trig_bits", "/reEmulTrigPlotter/trig_bits", lambda (n, l): True)
