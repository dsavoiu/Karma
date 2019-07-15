// this file contains C++ functions intended to be used in 'Define' statements on the RDataFrame

//unsigned long getAssignedHLTPathPtAve(const double& jet12yboost, const double& jet12ystar, const double& jet12ptave) {
//
//}

/*
 * Event weight used for stitching together all QCD Pt-binned samples
 */
double getWeightForStitching(const double& binningValue) {

    if (binningValue < 15)          return 0.0;
    else if (binningValue < 30)     return 45.6157956973778;
    else if (binningValue < 50)     return 13.9177659430564;
    else if (binningValue < 80)     return 1.91875528034421;
    else if (binningValue < 120)    return 0.391455814872172;
    else if (binningValue < 170)    return 0.06968696169617;
    else if (binningValue < 300)    return 0.016870947882854;
    else if (binningValue < 470)    return 0.001867928110427;
    else if (binningValue < 600)    return 0.000162147037894;
    else if (binningValue < 800)    return 4.77105603822183E-05;
    else if (binningValue < 1000)   return 8.02833187044852E-06;
    else if (binningValue < 1400)   return 3.12263572461987E-06;
    else if (binningValue < 1800)   return 2.11851900436166E-06;
    else if (binningValue < 2400)   return 2.82653523110195E-07;
    else if (binningValue < 3200)   return 1.6912726125052E-08;
    else                            return 4.150765185648461e-10;
}

#define IDX_HLT_IsoMu24          0

#define IDX_HLT_PFJet40          1
#define IDX_HLT_PFJet60          2
#define IDX_HLT_PFJet80          3
#define IDX_HLT_PFJet140         4
#define IDX_HLT_PFJet200         5
#define IDX_HLT_PFJet260         6
#define IDX_HLT_PFJet320         7
#define IDX_HLT_PFJet400         8
#define IDX_HLT_PFJet450         9
#define IDX_HLT_PFJet500        10

#define IDX_HLT_AK8PFJet40      11
#define IDX_HLT_AK8PFJet60      12
#define IDX_HLT_AK8PFJet80      13
#define IDX_HLT_AK8PFJet140     14
#define IDX_HLT_AK8PFJet200     15
#define IDX_HLT_AK8PFJet260     16
#define IDX_HLT_AK8PFJet320     17
#define IDX_HLT_AK8PFJet400     18
#define IDX_HLT_AK8PFJet450     19
#define IDX_HLT_AK8PFJet500     20

#define IDX_HLT_DiPFJetAve40    21
#define IDX_HLT_DiPFJetAve60    22
#define IDX_HLT_DiPFJetAve80    23
#define IDX_HLT_DiPFJetAve140   24
#define IDX_HLT_DiPFJetAve200   25
#define IDX_HLT_DiPFJetAve260   26
#define IDX_HLT_DiPFJetAve320   27
#define IDX_HLT_DiPFJetAve400   28
#define IDX_HLT_DiPFJetAve500   29

// -- convenience function
#define FIRED(TRIGGER_INDEX)    ((hltBits & (1 << TRIGGER_INDEX)) > 0)

// -- active phase space regions

#define PTAVE_THRESHOLD_AK4_HLT_PFJet40         100
#define PTAVE_THRESHOLD_AK4_HLT_PFJet60         100
#define PTAVE_THRESHOLD_AK4_HLT_PFJet80         147
#define PTAVE_THRESHOLD_AK4_HLT_PFJet140        207
#define PTAVE_THRESHOLD_AK4_HLT_PFJet200        284
#define PTAVE_THRESHOLD_AK4_HLT_PFJet260        437
#define PTAVE_THRESHOLD_AK4_HLT_PFJet320        499
#define PTAVE_THRESHOLD_AK4_HLT_PFJet400        499
#define PTAVE_THRESHOLD_AK4_HLT_PFJet450        499
#define PTAVE_THRESHOLD_AK4_HLT_PFJet500        569

#define PTAVE_THRESHOLD_AK8_HLT_AK8PFJet40      100
#define PTAVE_THRESHOLD_AK8_HLT_AK8PFJet60      100
#define PTAVE_THRESHOLD_AK8_HLT_AK8PFJet80      147
#define PTAVE_THRESHOLD_AK8_HLT_AK8PFJet140     243
#define PTAVE_THRESHOLD_AK8_HLT_AK8PFJet200     284
#define PTAVE_THRESHOLD_AK8_HLT_AK8PFJet260     437
#define PTAVE_THRESHOLD_AK8_HLT_AK8PFJet320     437
#define PTAVE_THRESHOLD_AK8_HLT_AK8PFJet400     499
#define PTAVE_THRESHOLD_AK8_HLT_AK8PFJet450     569
#define PTAVE_THRESHOLD_AK8_HLT_AK8PFJet500     569

#define PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve40    100
#define PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve60    100
#define PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve80    100
#define PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve140   207
#define PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve200   284
#define PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve260   499
#define PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve320   380
#define PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve400   646
#define PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve500   569

#define PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve40    100
#define PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve60    100
#define PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve80    122
#define PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve140   243
#define PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve200   284
#define PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve260   499
#define PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve320   437
#define PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve400   499
#define PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve500   732


// -- trigger path luminosity weights

// -- Run2016BCDEFGH
#define LUMI_WEIGHT_HLT_PFJet40       1.0e6/260677.932
#define LUMI_WEIGHT_HLT_PFJet60       1.0e6/707712.615
#define LUMI_WEIGHT_HLT_PFJet80       1.0e6/2668536.141
#define LUMI_WEIGHT_HLT_PFJet140      1.0e6/23567425.728
#define LUMI_WEIGHT_HLT_PFJet200      1.0e6/100514584.674
#define LUMI_WEIGHT_HLT_PFJet260      1.0e6/578212671.073
#define LUMI_WEIGHT_HLT_PFJet320      1.0e6/1726061109.457
#define LUMI_WEIGHT_HLT_PFJet400      1.0e6/5059889399.017
#define LUMI_WEIGHT_HLT_PFJet450      1.0e6/35505301212.254
#define LUMI_WEIGHT_HLT_PFJet500      1.0e6/35505301212.254

#define LUMI_WEIGHT_HLT_AK8PFJet40    1.0e6/48619.385
#define LUMI_WEIGHT_HLT_AK8PFJet60    1.0e6/320737.623
#define LUMI_WEIGHT_HLT_AK8PFJet80    1.0e6/981722.646
#define LUMI_WEIGHT_HLT_AK8PFJet140   1.0e6/9876193.532
#define LUMI_WEIGHT_HLT_AK8PFJet200   1.0e6/83586318.803
#define LUMI_WEIGHT_HLT_AK8PFJet260   1.0e6/506681445.79
#define LUMI_WEIGHT_HLT_AK8PFJet320   1.0e6/1492934157.56
#define LUMI_WEIGHT_HLT_AK8PFJet400   1.0e6/4492395633.725
#define LUMI_WEIGHT_HLT_AK8PFJet450   1.0e6/32924756955.684
#define LUMI_WEIGHT_HLT_AK8PFJet500   1.0e6/32924756955.684

#define LUMI_WEIGHT_HLT_DiPFJetAve40  1.0e6/98401.53
#define LUMI_WEIGHT_HLT_DiPFJetAve60  1.0e6/1674378.33
#define LUMI_WEIGHT_HLT_DiPFJetAve80  1.0e6/4067809.231
#define LUMI_WEIGHT_HLT_DiPFJetAve140 1.0e6/27127635.87
#define LUMI_WEIGHT_HLT_DiPFJetAve200 1.0e6/137076056.753
#define LUMI_WEIGHT_HLT_DiPFJetAve260 1.0e6/515715025.496
#define LUMI_WEIGHT_HLT_DiPFJetAve320 1.0e6/2928445716.012
#define LUMI_WEIGHT_HLT_DiPFJetAve400 1.0e6/8899311397.709
#define LUMI_WEIGHT_HLT_DiPFJetAve500 1.0e6/28879668652.344


/*
 * Returns the luminosity weight for a trigger path determined based on reco. jet pt average
 */
int getActiveAK4TriggerPathByPtAve(const double& ptave) {

    if      ((499 <= ptave)                 ) return IDX_HLT_PFJet450 ;
    else if ((437 <= ptave) && (ptave < 499)) return IDX_HLT_PFJet400 ;
    else if ((380 <= ptave) && (ptave < 437)) return IDX_HLT_PFJet320 ;
    else if ((329 <= ptave) && (ptave < 380)) return IDX_HLT_PFJet260 ;
    else if ((284 <= ptave) && (ptave < 329)) return IDX_HLT_PFJet200 ;
    else if ((174 <= ptave) && (ptave < 284)) return IDX_HLT_PFJet140 ;
    else if ((147 <= ptave) && (ptave < 174)) return IDX_HLT_PFJet80  ;
    else if ((100 <= ptave) && (ptave < 147)) return IDX_HLT_PFJet60  ;
    else                                      return 0;

}

/*
 * Returns the luminosity weight for a trigger path determined based on reco. jet pt average
 */
int getActiveAK8TriggerPathByPtAve(const double& ptave) {

    if      ((569 <= ptave)                 ) return IDX_HLT_AK8PFJet500 ;
    else if ((499 <= ptave) && (ptave < 569)) return IDX_HLT_AK8PFJet450 ;
    else if ((437 <= ptave) && (ptave < 499)) return IDX_HLT_AK8PFJet400 ;
    else if ((380 <= ptave) && (ptave < 437)) return IDX_HLT_AK8PFJet320 ;
    else if ((329 <= ptave) && (ptave < 380)) return IDX_HLT_AK8PFJet260 ;
    else if ((284 <= ptave) && (ptave < 329)) return IDX_HLT_AK8PFJet200 ;
    else if ((207 <= ptave) && (ptave < 284)) return IDX_HLT_AK8PFJet140 ;
    else if ((175 <= ptave) && (ptave < 207)) return IDX_HLT_AK8PFJet80  ;
    else                                      return 0;

}
/*
 * Returns the luminosity weight for a trigger path determined based on reco. jet pt average
 */
int getActiveDijetTriggerPathByPtAve(const double& ptave) {

    if      ((499 <= ptave)                 ) return IDX_HLT_DiPFJetAve500 ;
    else if ((437 <= ptave) && (ptave < 499)) return IDX_HLT_DiPFJetAve400 ;
    else if ((380 <= ptave) && (ptave < 437)) return IDX_HLT_DiPFJetAve320 ;
    else if ((329 <= ptave) && (ptave < 380)) return IDX_HLT_DiPFJetAve260 ;
    else if ((284 <= ptave) && (ptave < 329)) return IDX_HLT_DiPFJetAve200 ;
    else if ((174 <= ptave) && (ptave < 284)) return IDX_HLT_DiPFJetAve140 ;
    else if ((147 <= ptave) && (ptave < 174)) return IDX_HLT_DiPFJetAve80  ;
    else if ((100 <= ptave) && (ptave < 147)) return IDX_HLT_DiPFJetAve60  ;
    else                                      return 0;

}

/*
 * Returns the luminosity weight for an event based on trigger decisions and reco. jet pt average
 */
double getAK4EventLuminosityWeightByPtAve_PFJetTriggers(const double& ptave, const unsigned long& hltBits) {

    if      (PTAVE_THRESHOLD_AK4_HLT_PFJet450 <= ptave) return FIRED(IDX_HLT_PFJet450) ? LUMI_WEIGHT_HLT_PFJet450 : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_PFJet400 <= ptave) return FIRED(IDX_HLT_PFJet400) ? LUMI_WEIGHT_HLT_PFJet400 : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_PFJet320 <= ptave) return FIRED(IDX_HLT_PFJet320) ? LUMI_WEIGHT_HLT_PFJet320 : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_PFJet260 <= ptave) return FIRED(IDX_HLT_PFJet260) ? LUMI_WEIGHT_HLT_PFJet260 : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_PFJet200 <= ptave) return FIRED(IDX_HLT_PFJet200) ? LUMI_WEIGHT_HLT_PFJet200 : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_PFJet140 <= ptave) return FIRED(IDX_HLT_PFJet140) ? LUMI_WEIGHT_HLT_PFJet140 : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_PFJet80  <= ptave) return FIRED(IDX_HLT_PFJet80 ) ? LUMI_WEIGHT_HLT_PFJet80  : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_PFJet60  <= ptave) return FIRED(IDX_HLT_PFJet60 ) ? LUMI_WEIGHT_HLT_PFJet60  : 0.0;
    else                                                return 0.0;
}

/*
 * Returns the luminosity weight for an event based on trigger decisions and reco. jet pt average
 */
double getAK8EventLuminosityWeightByPtAve_AK8PFJetTriggers(const double& ptave, const unsigned long& hltBits) {

    if      (PTAVE_THRESHOLD_AK8_HLT_AK8PFJet450 <= ptave) return FIRED(IDX_HLT_AK8PFJet450) ? LUMI_WEIGHT_HLT_AK8PFJet450 : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_AK8PFJet400 <= ptave) return FIRED(IDX_HLT_AK8PFJet400) ? LUMI_WEIGHT_HLT_AK8PFJet400 : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_AK8PFJet320 <= ptave) return FIRED(IDX_HLT_AK8PFJet320) ? LUMI_WEIGHT_HLT_AK8PFJet320 : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_AK8PFJet260 <= ptave) return FIRED(IDX_HLT_AK8PFJet260) ? LUMI_WEIGHT_HLT_AK8PFJet260 : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_AK8PFJet200 <= ptave) return FIRED(IDX_HLT_AK8PFJet200) ? LUMI_WEIGHT_HLT_AK8PFJet200 : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_AK8PFJet140 <= ptave) return FIRED(IDX_HLT_AK8PFJet140) ? LUMI_WEIGHT_HLT_AK8PFJet140 : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_AK8PFJet80  <= ptave) return FIRED(IDX_HLT_AK8PFJet80 ) ? LUMI_WEIGHT_HLT_AK8PFJet80  : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_AK8PFJet60  <= ptave) return FIRED(IDX_HLT_AK8PFJet60 ) ? LUMI_WEIGHT_HLT_AK8PFJet60  : 0.0;
    else                                                   return 0.0;

}

/*
 * Returns the luminosity weight for an event based on trigger decisions and reco. jet pt average
 */
double getAK4EventLuminosityWeightByPtAve_DiPFJetAveTriggers(const double& ptave, const unsigned long& hltBits) {

    if      (PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve500 <= ptave) return FIRED(IDX_HLT_DiPFJetAve500) ? LUMI_WEIGHT_HLT_DiPFJetAve500 : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve400 <= ptave) return FIRED(IDX_HLT_DiPFJetAve400) ? LUMI_WEIGHT_HLT_DiPFJetAve400 : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve320 <= ptave) return FIRED(IDX_HLT_DiPFJetAve320) ? LUMI_WEIGHT_HLT_DiPFJetAve320 : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve260 <= ptave) return FIRED(IDX_HLT_DiPFJetAve260) ? LUMI_WEIGHT_HLT_DiPFJetAve260 : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve200 <= ptave) return FIRED(IDX_HLT_DiPFJetAve200) ? LUMI_WEIGHT_HLT_DiPFJetAve200 : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve140 <= ptave) return FIRED(IDX_HLT_DiPFJetAve140) ? LUMI_WEIGHT_HLT_DiPFJetAve140 : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve80  <= ptave) return FIRED(IDX_HLT_DiPFJetAve80 ) ? LUMI_WEIGHT_HLT_DiPFJetAve80  : 0.0;
    else if (PTAVE_THRESHOLD_AK4_HLT_DiPFJetAve60  <= ptave) return FIRED(IDX_HLT_DiPFJetAve60 ) ? LUMI_WEIGHT_HLT_DiPFJetAve60  : 0.0;
    else                                                     return 0.0;
}

/*
 * Returns the luminosity weight for an event based on trigger decisions and reco. jet pt average
 */
double getAK8EventLuminosityWeightByPtAve_DiPFJetAveTriggers(const double& ptave, const unsigned long& hltBits) {

    if      (PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve500 <= ptave) return FIRED(IDX_HLT_DiPFJetAve500) ? LUMI_WEIGHT_HLT_DiPFJetAve500 : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve400 <= ptave) return FIRED(IDX_HLT_DiPFJetAve400) ? LUMI_WEIGHT_HLT_DiPFJetAve400 : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve320 <= ptave) return FIRED(IDX_HLT_DiPFJetAve320) ? LUMI_WEIGHT_HLT_DiPFJetAve320 : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve260 <= ptave) return FIRED(IDX_HLT_DiPFJetAve260) ? LUMI_WEIGHT_HLT_DiPFJetAve260 : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve200 <= ptave) return FIRED(IDX_HLT_DiPFJetAve200) ? LUMI_WEIGHT_HLT_DiPFJetAve200 : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve140 <= ptave) return FIRED(IDX_HLT_DiPFJetAve140) ? LUMI_WEIGHT_HLT_DiPFJetAve140 : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve80  <= ptave) return FIRED(IDX_HLT_DiPFJetAve80 ) ? LUMI_WEIGHT_HLT_DiPFJetAve80  : 0.0;
    else if (PTAVE_THRESHOLD_AK8_HLT_DiPFJetAve60  <= ptave) return FIRED(IDX_HLT_DiPFJetAve60 ) ? LUMI_WEIGHT_HLT_DiPFJetAve60  : 0.0;
    else                                                     return 0.0;
}
