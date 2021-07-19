### Cleaning of the code written by Jian Xu, Apr 2017
### See https://arxiv.org/abs/1712.09658

from collections import defaultdict, Counter
import math
import numpy as np
import HONUtils

class FastHONRulesBuilder():
  ###########################################
  def __init__(self,trajectories,max_order,min_support):
    self.ThresholdMultiplier = 1.
    self.Count = defaultdict(lambda: defaultdict(int))
    self.Rules = defaultdict(dict)
    self.Distribution = defaultdict(dict)
    self.SourceToExtSource = defaultdict(set)
    self.StartingPoints = defaultdict(set)
    self.Trajectory = trajectories
    self.MinSupport = min_support
    self.MaxOrder   = max_order

  def ExtractRules(self):
    self.BuildObservations()
    self.BuildDistributions()
    self.GenerateAllRules()
    return self.Rules

  def BuildObservations(self):
    for Tindex in range(len(self.Trajectory)):        
        trajectory = self.Trajectory[Tindex]
        for index in range(len(trajectory) - 1):
            Source = tuple(trajectory[index:index + 1])
            Target = trajectory[index + 1]
            self.Count[Source][Target] += 1
            self.StartingPoints[Source].add((Tindex, index))

  def BuildDistributions(self):
    for Source in self.Count:
        for Target in self.Count[Source].keys():
            if self.Count[Source][Target] < self.MinSupport:
                self.Count[Source][Target] = 0
        for Target in self.Count[Source]:
          if self.Count[Source][Target] > 0:
              self.Distribution[Source][Target] = 1.0 * self.Count[Source][Target] / sum(self.Count[Source].values())


  def GenerateAllRules(self):
    for Source in tuple(self.Distribution.keys()):
        self.AddToRules(Source)
        self.ExtendRule(Source, Source, 1)

  def ExtendRule(self,Valid, Curr, order):
    if order >= self.MaxOrder:
        self.AddToRules(Valid)
    else:
        Distr = self.Distribution[Valid]
        supp_curr = sum([x for x in self.Count[Curr].values()])
        # test if divergence has no chance exceeding the threshold when going for higher order
#        if HONUtils.KLD(HONUtils.MaxDivergence(self.Distribution[Curr]), Distr) < HONUtils.KLDThreshold(order + 1, supp_curr):
        if -np.log2(min(Distr.values())) < HONUtils.KLDThreshold(order + 1, supp_curr):
            self.AddToRules(Valid)
        else:
            #if order + 1 not in ObservationBuiltForOrder:
            Extended = self.ExtendSourceFast(Curr)
            if len(Extended) == 0:
                self.AddToRules(Valid)
            else:
                for ExtSource in Extended:
                    ExtDistr = self.Distribution[ExtSource]  # Pseudocode in Algorithm 1 has a typo here
                    supp_ext = sum([x for x in self.Count[ExtSource].values()])
                    divergence = HONUtils.KLD(ExtDistr, Distr)
                    if divergence > HONUtils.KLDThreshold(order + 1, supp_ext):
                        # higher-order dependencies exist for order order + 1
                        # keep comparing probability distribution of higher orders with current order
                        self.ExtendRule(ExtSource, ExtSource, order + 1)
                    else:
                        # higher-order dependencies do not exist for current order
                        # keep comparing probability distribution of higher orders with known order
                        self.ExtendRule(Valid, ExtSource, order + 1)

  def AddToRules(self,Source):
    for order in range(1, len(Source)+1):
        s = Source[0:order]
        #print(s, Source)
        if not s in self.Distribution or len(self.Distribution[s]) == 0:
            self.ExtendSourceFast(s[1:])
        for t in self.Distribution[s]:
            if self.Distribution[s][t] > 0:
                self.Rules[s][t] = self.Distribution[s][t]

  ###########################################
  # Auxiliary functions
  ###########################################

  def ExtendSourceFast(self,Curr):
    if Curr in self.SourceToExtSource:
        return self.SourceToExtSource[Curr]
    else:
        self.ExtendObservation(Curr)
        if Curr in self.SourceToExtSource:
            return self.SourceToExtSource[Curr]
        else:
            return []


  def ExtendObservation(self,Source):
    if len(Source) > 1:
        if (not Source[1:] in self.Count) or (len(self.Count[Source]) == 0):
            self.ExtendObservation(Source[1:])
    order = len(Source)
    C = defaultdict(lambda: defaultdict(int))
    
    for Tindex,index in self.StartingPoints[Source]:
        if index - 1 >= 0 and index + order < len(self.Trajectory[Tindex]):
            ExtSource = tuple(self.Trajectory[Tindex][index - 1:index + order])
            Target = self.Trajectory[Tindex][index + order]
            C[ExtSource][Target] += 1
            self.StartingPoints[ExtSource].add((Tindex, index - 1))

    if len(C) == 0:
        return
    for s in C:
        for t in C[s]:
            if C[s][t] < self.MinSupport:
                C[s][t] = 0
            self.Count[s][t] += C[s][t]
        CsSupport = sum(C[s].values())
        for t in C[s]:
            if C[s][t] > 0:
                self.Distribution[s][t] = 1.0 * C[s][t] / CsSupport
                self.SourceToExtSource[s[1:]].add(s)
