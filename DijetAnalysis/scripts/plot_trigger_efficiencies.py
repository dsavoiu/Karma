import ROOT

ROOT.gROOT.SetBatch(True)


triggers = [
   "HLT_PFJet40",
   "HLT_PFJet60",
   "HLT_PFJet80",
   "HLT_PFJet140",
   "HLT_PFJet200",
   "HLT_PFJet260",
   "HLT_PFJet320",
   "HLT_PFJet400",
   "HLT_PFJet450",
   "HLT_PFJet500",
]

thres_map = {
    "HLT_PFJet40"  : (0, 40),
    "HLT_PFJet60"  : (35, 60),
    "HLT_PFJet80"  : (60, 80),
    "HLT_PFJet140" : (90, 140),
    "HLT_PFJet200" : (120, 200),
    "HLT_PFJet260" : (170, 260),
    "HLT_PFJet320" : (170, 320),
    "HLT_PFJet400" : (170, 400),
    "HLT_PFJet450" : (170, 450),
    "HLT_PFJet500" : (170, 500),
}


def plot_trigger_efficiencies_from_file(file_path, x_title, x_range):
    print "Opening File '{}'...".format(file_path)
    _file = ROOT.TFile(file_path)

    _cg = ROOT.TCanvas("cg")
    _legend = ROOT.TLegend(.5, .1, .9, .4)
    for _i, _t in enumerate(triggers):
            print "Getting '{}'...".format(_t)
            _h = _file.Get(_t)
#            if not isinstance(_h, ROOT.TEfficiency):
#                raise TypeError("Expecting TEfficiency, got {}".format(type(_h)))
            _g = _h.CreateGraph()

            _g.SetName("g_{}".format(_t))

            _opt = "PL"
            if _i == 0:
                _opt = "AL"

            _color = _i + 1
            if _color == 10: _color = 11
            print _t, _color

            _g.SetMarkerColor(_color)
            _g.SetLineColor(_color)
            _g.SetLineWidth(3)

            _g.GetXaxis().SetTitle(x_title)
            _g.GetYaxis().SetTitle("Efficiency")
            _g.GetXaxis().SetLimits(x_range[0], x_range[1])
            _g.GetYaxis().SetLimits(0.0, 1.1)

            _l_Unity = ROOT.TLine(x_range[0], .99, x_range[1], .99)
            _l_Unity.SetLineColor(1)

            # draw in global canvas
            _cg.cd()
            _g.Draw(_opt+" SAME")
            _l_Unity.Draw()
            _legend.AddEntry("g_{}".format(_t), "{}".format(_t), "LEP")

    _legend.Draw()
    _cg.SaveAs("all_triggers.png")

    # draw each trigger to own canvas
    for _i, _t in enumerate(triggers):
            _c = ROOT.TCanvas("c{}".format(_i))
            _h = _file.Get("{}".format(_t))
            _g = _h.CreateGraph()
            _g.SetTitle("{}".format(_t))

            _opt = "APL"
            _color = _i + 1
            if _color == 10: _color = 11
            print _t, _color

            _g.SetMarkerColor(_color)
            _g.SetLineColor(_color)
            _g.SetLineWidth(3)

            _g.GetXaxis().SetTitle(x_title)
            _g.GetYaxis().SetTitle("Efficiency")
            _g.GetXaxis().SetLimits(x_range[0], x_range[1])
            _g.GetYaxis().SetLimits(0.0, 1.1)

            _x_L1, _x_HLT = thres_map[_t]
            _l_L1 = ROOT.TLine(_x_L1, 0, _x_L1, 1)
            _l_HLT = ROOT.TLine(_x_HLT, 0, _x_HLT, 1)
            _l_Unity = ROOT.TLine(x_range[0], .99, x_range[1], .99)
            _l_L1.SetLineColor(_color)
            _l_HLT.SetLineColor(_color)
            _l_Unity.SetLineColor(1)
            _l_L1.SetLineStyle(7)  # dashed

            # draw in global canvas
            _g.Draw(_opt)
            _l_L1.Draw()
            _l_HLT.Draw()
            _l_Unity.Draw()
            _c.SaveAs("{}.png".format(_t))


if __name__ == "__main__":
    import sys

    plot_trigger_efficiencies_from_file(sys.argv[1], "pT_j / GeV", (0, 700))
