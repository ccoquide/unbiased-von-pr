import os
import sys
import Stats
'''
From PageRanks we build a table with Items name (1st col), 1stON PR values (2nd col), VON PR values (3rd col), Biased 1stON PR values (4th col), Unbiased VON PR values (5th col), Nrep (6th col) and VisitRank (7th col)

Command to run this script: python3 getFinal.py input_sequences_filename alpha
'''
#################################################################
def PRfile(sequences_file, opt, model, alpha):
	'''
	Create the right PR file name from input sequences file name, option, model and a given alpha.
	'''
	if opt == "1stON":
		if model == "standard":
			prname="1stON-PR"
		if model == "biased":
			prname="Biased-1stON-PR"
	if opt == "VON":
		if model == "standard":
			prname="VON-PR"
		if model == "forder":
			prname="Unbiased-VON-PR"
	file_name = sequences_file.replace(".csv","")+"-"+opt+"-"+prname+"-"+alpha.replace(".","")+".dat"
	return file_name

##########
## MAIN ##
##########

## init reading file (Item information, PageRanks and Stats)
sequences_file = sys.argv[1]
alpha=sys.argv[2]
PRfiles={}
PRfiles["1stON PR"]=PRfile(sequences_file, "1stON", "standard", alpha)
PRfiles["VON PR"]=PRfile(sequences_file, "VON", "standard", alpha)
PRfiles["Biased 1stON PR"]=PRfile(sequences_file, "1stON", "biased", alpha)
PRfiles["Unbiased VON PR"]=PRfile(sequences_file, "VON", "forder", alpha)

Items={} ## Dict of item ID (Tuple) -> Item name (string)
f=open(sequences_file.replace(".csv", "-info.csv"), 'r').read() ## Item information related file (table of Item (tuple) and Item name (string)
f=f.split("\n")
f.remove(f[0]) ## Header
f.remove("")
for line in f:
	tmp=line.split("\t")
	item=Stats.getTuplefromString(tmp[0])
	Items[item]=tmp[1]

stats=open(sequences_file.replace(".csv","")+"-Stats.dat",'r').read()
stats=stats.split("\n")
stats.remove("")
stats.remove(stats[0]) ## Header
ST={}
ST["Nrep"]={}
ST["Visit Rank"]={}
for i in stats:
	tmp=i.split("\t")
	item=Stats.getTuplefromString(tmp[0])
	ST["Nrep"][item]=int(tmp[1])
	ST["Visit Rank"][item]=tmp[2]

## Building output containing all PageRank values / Ranks related to 4 PR models + Visit Ranks and Nrep Rank
P={} ## Dict of Dict of PageRank values: PR model (str) -> Item (tuple) -> PageRank probability (float)
RK={} ## Dict of Dict of Rankings: PR model(str) -> Item (tuple) -> PageRank Rank
print("Starting processing output file")
for model in ["1stON PR", "VON PR", "Biased 1stON PR", "Unbiased VON PR"]:
	P[model]={}
	RK[model]={}
	f=open(PRfiles[model],"r").read()
	f=f.split("\n")
	f.remove("")
	f.remove(f[0]) ## Header
	for line in f:
		tmp=line.split("\t")
		item=Stats.getTuplefromString(tmp[3])
		P[model][item]=float(tmp[1])
		RK[model][item]=int(tmp[0])
	norm=sum(P[model].values())
	for i in P[model]:
		P[model][i]=P[model][i]/norm

## Writing output files
print("Writing files")
out1=open(sequences_file.replace(".csv","")+"-scores-"+alpha.replace(".","")+".dat","w")
out2=open(sequences_file.replace(".csv","")+"-ranks-"+alpha.replace(".","")+".dat","w")
out1.write("Item\t1stON PR\tVON PR\tBiased 1stON PR\tUnbiased VON PR\tNrep-Rank\tVisit-Rank\n")
out2.write("Item\t1stON K\tVON K\tBiased 1stON K\tUnbiased VON K\tNrep-Rank\tVisit-Rank\n")
sort_items=sorted(ST["Nrep"].items(), key = lambda x :x[1], reverse=False)
for i in sort_items:
	item=i[0]
	if item not in Items.keys(): ## If item is present in sequences but not in information file
		name=str(item[0])
	else:
		name=Items[item]
	out1.write(name)
	out2.write(name)
	for model in ["1stON PR", "VON PR", "Biased 1stON PR", "Unbiased VON PR"]:
		out1.write("\t"+str(P[model][item]))
		out2.write("\t"+str(RK[model][item]))
	out1.write("\t"+str(i[1])+"\t"+ST["Visit Rank"][item]+"\n")
	out2.write("\t"+str(i[1])+"\t"+ST["Visit Rank"][item]+"\n")
out1.close()
out2.close()
