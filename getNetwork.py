# -*- coding: utf-8 -*-
'''
Build a variable-network (option = "VON") or first-order network (option = "1stON") from input sequences
Command to execute this script: python3 getNetwork.py input_sequences_filename option
'''

import sys
import os
from BuildRulesFast import *
from BuildNetwork import *
from HONUtils import *
#PARAM : Python *.py seq.dat opt (opt is either 1 or +, if opt = 1, build 1stON, if opt = +, build HON using buildhon+ algorithm)

#####################
## INPUT SEQUENCES ##
#####################

##File name and separator type
sequences_file=sys.argv[1]
sep=","
ID=True ## if first item of each sequence is an id then ID=True 
SEQs=readSequenceFile(sequences_file,ID,sep)
Items=[] ## List of items
MemNodes=[] ## List of Memory-nodes
for opt in ['1stON', 'VON']:
	if opt == '1stON':
		kmax = 1
	if opt == 'VON':
		kmax = 20 ## Arbitrary large max order
	out1=open(sequences_file.replace(".csv", "")+"-"+opt+".titles","w") ## list of memory-nodes 
	out2=open(sequences_file.replace(".csv","")+"-"+opt+".txt","w") ## table of links
	###################
	## BUILD NETWORK ##
	###################
	print("Extracting relevant extensions from sequences")
	R=FastHONRulesBuilder(SEQs,kmax,1)
	R.ExtractRules() ## Relevent extensions extraction from sequences
	
	print("Building Network from extensions")
	G=BuildNetwork(R.Rules)
	
	print("Writing output files")
	Nodes={} ## dict: Item representations (tuple) -> Nodes ID (int)
	Links=[] ## Table of links
	Nl=0
	nID=1 ## Node IDs
	for i in G:
		if i not in Nodes.keys():
			Nodes[i]=nID
			out1.write(str(i)+"\n")
			nID+=1
		for j in G[i]:
			if j not in Nodes.keys():
				Nodes[j]=nID
				out1.write(str(j)+"\n")
				nID+=1
			Nl+=1
			Links.append(str(Nodes[i])+"\t"+str(Nodes[j])+"\t"+str(G[i][j])+"\n")
	if opt == "1stON":
		Items = list(Nodes.keys())
	if opt == "VON":
		MemNodes = list(Nodes.keys()) 
	####################
	## TABLE OF LINKS ##
	####################
	'''
	First two lines are number of nodes and number of links, then each line is formated as follows:
	source node ID \t target node ID \t transition probability
	'''
	out2.write(str(nID-1)+"\n") ## Number of nodes
	out2.write(str(Nl)+"\n") ## Number of links
	for l in Links:
		out2.write(l)
	out1.close()
	out2.close()

#################
## STATS FILES ##
#################
'''
Stats about Nrep distribution and Visit-Rank
'''
print("Computing stats: RepRank and Visit-Rank")
Rep={} ## Dict of Nrep Rank: Item (tuple) -> Rank (int)
V={} ## Dict of Visit Rank: Item (tuple) -> Rank (int)
tmpRep={} ## Dict of Nrep Rank: Nrep (int) -> Rank (int)
tmpV={} ## Dict of Visit Rank: Visit rate (float) -> Rank (int)
for i in Items:
	Rep[i]=0
	V[i]=0

## Visit Ranking
cnt=0
for seq in SEQs:
	for i in seq:
		V[(i,)]+=1
		cnt+=1
for i in Items:
	V[i]=(1.0*V[i])/cnt
for i in V:
	tmpV[V[i]]=1
tmpv=list(tmpV.keys())
tmpv_sorted=sorted(range(len(tmpv)), key = lambda k : tmpv[k], reverse=True)
for k in range(len(tmpv_sorted)):
	tmpV[tmpv[tmpv_sorted[k]]]=k+1 ## Permits ties
for i in V:
	V[i]=tmpV[V[i]]

## Nrep Ranking
for n in MemNodes:
	Rep[n[-1:]] += 1
for i in Rep:
	tmpRep[Rep[i]]=1
tmpr=list(tmpRep.keys())
tmpr_sorted=sorted(range(len(tmpr)), key = lambda k : tmpr[k], reverse=True)
for k in range(len(tmpr_sorted)):
	tmpRep[tmpr[tmpr_sorted[k]]]=k+1 ## Permits ties
for i in Rep:
	Rep[i]=tmpRep[Rep[i]]
RepRank=Rep
VisitRank=V
out=open(sequences_file.replace(".csv","")+"-Stats.dat","w")
out.write("Item\tNrep-Rank\tVisit-Rank\n")
for i in Items:
	out.write(str(i)+"\t"+str(RepRank[i])+"\t"+str(VisitRank[i])+"\n")
out.close()

