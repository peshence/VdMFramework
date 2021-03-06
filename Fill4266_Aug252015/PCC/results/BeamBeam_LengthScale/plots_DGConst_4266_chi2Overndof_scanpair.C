{
//=========Macro generated from canvas: c1_n2/c1_n2
//=========  (Sun Feb  7 16:36:17 2016) by ROOT version5.34/32
   TCanvas *c1_n2 = new TCanvas("c1_n2", "c1_n2",0,0,700,500);
   gStyle->SetOptFit(1);
   gStyle->SetOptStat(0);
   c1_n2->SetHighLightColor(2);
   c1_n2->Range(-1.25,0.3815534,12.25,5.416546);
   c1_n2->SetFillColor(0);
   c1_n2->SetBorderMode(0);
   c1_n2->SetBorderSize(2);
   c1_n2->SetFrameBorderMode(0);
   c1_n2->SetFrameBorderMode(0);
   
   TGraphErrors *gre = new TGraphErrors(50);
   gre->SetName("");
   gre->SetTitle("4266 PCC DGConst chi2Overndof");
   gre->SetFillColor(1);
   gre->SetMarkerStyle(8);
   gre->SetMarkerSize(0.4);
   gre->SetPoint(0,10,2.042726);
   gre->SetPointError(0,0,0);
   gre->SetPoint(1,10,1.888095);
   gre->SetPointError(1,0,0);
   gre->SetPoint(2,10,2.204442);
   gre->SetPointError(2,0,0);
   gre->SetPoint(3,10,1.220719);
   gre->SetPointError(3,0,0);
   gre->SetPoint(4,10,3.557431);
   gre->SetPointError(4,0,0);
   gre->SetPoint(5,4,1.755624);
   gre->SetPointError(5,0,0);
   gre->SetPoint(6,4,1.763967);
   gre->SetPointError(6,0,0);
   gre->SetPoint(7,4,4.274719);
   gre->SetPointError(7,0,0);
   gre->SetPoint(8,4,2.22027);
   gre->SetPointError(8,0,0);
   gre->SetPoint(9,4,1.62331);
   gre->SetPointError(9,0,0);
   gre->SetPoint(10,5,2.646529);
   gre->SetPointError(10,0,0);
   gre->SetPoint(11,5,1.865803);
   gre->SetPointError(11,0,0);
   gre->SetPoint(12,5,3.198888);
   gre->SetPointError(12,0,0);
   gre->SetPoint(13,5,2.408262);
   gre->SetPointError(13,0,0);
   gre->SetPoint(14,5,1.498237);
   gre->SetPointError(14,0,0);
   gre->SetPoint(15,6,1.920528);
   gre->SetPointError(15,0,0);
   gre->SetPoint(16,6,2.773427);
   gre->SetPointError(16,0,0);
   gre->SetPoint(17,6,2.081392);
   gre->SetPointError(17,0,0);
   gre->SetPoint(18,6,1.389961);
   gre->SetPointError(18,0,0);
   gre->SetPoint(19,6,2.826773);
   gre->SetPointError(19,0,0);
   gre->SetPoint(20,7,1.432477);
   gre->SetPointError(20,0,0);
   gre->SetPoint(21,7,2.502976);
   gre->SetPointError(21,0,0);
   gre->SetPoint(22,7,2.009262);
   gre->SetPointError(22,0,0);
   gre->SetPoint(23,7,2.085643);
   gre->SetPointError(23,0,0);
   gre->SetPoint(24,7,1.97951);
   gre->SetPointError(24,0,0);
   gre->SetPoint(25,1,1.700368);
   gre->SetPointError(25,0,0);
   gre->SetPoint(26,1,2.94338);
   gre->SetPointError(26,0,0);
   gre->SetPoint(27,1,2.00792);
   gre->SetPointError(27,0,0);
   gre->SetPoint(28,1,2.201473);
   gre->SetPointError(28,0,0);
   gre->SetPoint(29,1,2.602758);
   gre->SetPointError(29,0,0);
   gre->SetPoint(30,2,2.196589);
   gre->SetPointError(30,0,0);
   gre->SetPoint(31,2,2.32282);
   gre->SetPointError(31,0,0);
   gre->SetPoint(32,2,2.451323);
   gre->SetPointError(32,0,0);
   gre->SetPoint(33,2,1.306985);
   gre->SetPointError(33,0,0);
   gre->SetPoint(34,2,4.11221);
   gre->SetPointError(34,0,0);
   gre->SetPoint(35,3,1.401615);
   gre->SetPointError(35,0,0);
   gre->SetPoint(36,3,1.502301);
   gre->SetPointError(36,0,0);
   gre->SetPoint(37,3,1.482582);
   gre->SetPointError(37,0,0);
   gre->SetPoint(38,3,1.970321);
   gre->SetPointError(38,0,0);
   gre->SetPoint(39,3,1.739645);
   gre->SetPointError(39,0,0);
   gre->SetPoint(40,8,3.123323);
   gre->SetPointError(40,0,0);
   gre->SetPoint(41,8,2.826876);
   gre->SetPointError(41,0,0);
   gre->SetPoint(42,8,4.577381);
   gre->SetPointError(42,0,0);
   gre->SetPoint(43,8,2.772666);
   gre->SetPointError(43,0,0);
   gre->SetPoint(44,8,3.193344);
   gre->SetPointError(44,0,0);
   gre->SetPoint(45,9,1.585087);
   gre->SetPointError(45,0,0);
   gre->SetPoint(46,9,1.573821);
   gre->SetPointError(46,0,0);
   gre->SetPoint(47,9,2.055686);
   gre->SetPointError(47,0,0);
   gre->SetPoint(48,9,1.292863);
   gre->SetPointError(48,0,0);
   gre->SetPoint(49,9,2.516159);
   gre->SetPointError(49,0,0);
   
   TH1F *Graph_Graph139 = new TH1F("Graph_Graph139","4266 PCC DGConst chi2Overndof",100,0.1,10.9);
   Graph_Graph139->SetMinimum(0.8850528);
   Graph_Graph139->SetMaximum(4.913047);
   Graph_Graph139->SetDirectory(0);
   Graph_Graph139->SetStats(0);

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#000099");
   Graph_Graph139->SetLineColor(ci);
   Graph_Graph139->GetXaxis()->SetTitle("Scan");
   Graph_Graph139->GetXaxis()->SetLabelFont(42);
   Graph_Graph139->GetXaxis()->SetLabelSize(0.035);
   Graph_Graph139->GetXaxis()->SetTitleSize(0.035);
   Graph_Graph139->GetXaxis()->SetTitleFont(42);
   Graph_Graph139->GetYaxis()->SetTitle("chi2Overndof");
   Graph_Graph139->GetYaxis()->SetLabelFont(42);
   Graph_Graph139->GetYaxis()->SetLabelSize(0.035);
   Graph_Graph139->GetYaxis()->SetTitleSize(0.035);
   Graph_Graph139->GetYaxis()->SetTitleFont(42);
   Graph_Graph139->GetZaxis()->SetLabelFont(42);
   Graph_Graph139->GetZaxis()->SetLabelSize(0.035);
   Graph_Graph139->GetZaxis()->SetTitleSize(0.035);
   Graph_Graph139->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_Graph139);
   
   gre->Draw("ap");
   
   TPaveText *pt = new TPaveText(0.2148563,0.94,0.7851437,0.995,"blNDC");
   pt->SetName("title");
   pt->SetBorderSize(0);
   pt->SetFillColor(0);
   pt->SetFillStyle(0);
   pt->SetTextFont(42);
   TText *text = pt->AddText("4266 PCC DGConst chi2Overndof");
   pt->Draw();
   c1_n2->Modified();
   c1_n2->cd();
   c1_n2->SetSelected(c1_n2);
}
