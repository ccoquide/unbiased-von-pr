### This file: line-by-line translation from Algorithm 2
### in the paper "Representing higher-order dependencies in networks"
### Code written by Jian Xu, Jan 2017

### Technical questions? Please contact i[at]jianxu[dot]net
### Demo of HON: please visit http://www.HigherOrderNetwork.com
### Latest code: please visit https://github.com/xyjprc/hon

### Call BuildNetwork()
### Input: Higher-order dependency rules
### Output: HON network
### See details in README


### Removing global variables


from collections import defaultdict, Counter

def BuildNetwork(Rules):
    #VPrint('Building network')
    Graph = defaultdict(dict)
    SortedSource = sorted(Rules, key=lambda x: len(x))
    for source in SortedSource:
        for target in Rules[source]:
            Graph[source][(target,)] = Rules[source][target]
            #print "Add "+str(source)+" -> "+str((target,))+" : "+str(Rules[source][target])
            # following operations are destructive to Rules
            if len(source) > 1:
                Rewire(Graph,source, (target,))
    #print("Rewire Tails")
    RewireTails(Graph)
    return Graph

def Rewire(Graph,source, target):
    PrevSource = source[:-1]
    PrevTarget = (source[-1],)
    if not PrevSource in Graph or not source in Graph[PrevSource]:
        Graph[PrevSource][source] = Graph[PrevSource][PrevTarget]        
        del(Graph[PrevSource][PrevTarget])
        #print " rewire "+str(PrevSource)+" to "+str(source)

def RewireTails(Graph):
    ToAdd = []
    ToRemove = []
    for source in Graph:
        for target in Graph[source]:
            if len(target) == 1:
                NewTarget = source + target
                while len(NewTarget) > 1:
                    if NewTarget in Graph:
                        #print " To add "+str(source)+" -> "+str(NewTarget)+" : "+str(Graph[source][target])
                        ToAdd.append((source, NewTarget, Graph[source][target]))
                        ToRemove.append((source, target))
                        break
                    else:
                        NewTarget = NewTarget[1:]
    for (source, target, weight) in ToAdd:
        Graph[source][target] = weight
    for (source, target) in ToRemove:
        del(Graph[source][target])
