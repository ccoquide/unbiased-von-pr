import os
import sys
import numpy as np
import Stats
import time
'''
Computing all PageRanks issued from 1stON, Biased 1stON, VON and Unbiased VON PR models, from table of links and list of nodes from both 1stON and VON.
Command to execute this script: python3 buildPR.py sequences_filename
'''
###################################################################
def getRep(nodes_file):
	'''
	Return distribution of the number of representations of items as dict: Item (tuple) -> Nrep (int)
	'''
	F=open(nodes_file,"r").read()
	F=F.split("\n")
	F.remove("")
	REP={}
	for i in range(len(F)):
		node=Stats.getTuplefromString(F[i])
		if node[-1:] not in REP.keys(): ## node[-1:] returns the item the memory-node represents
			REP[node[-1:]]=0
		REP[node[-1:]]+=1
	return REP
def IsConverged(conv,v1,v2,N):
	'''
	Convergence tests for the power method computation of PageRank
	'''
	eps1=10**-13
	eps2=10**-10
	c1=0.0
	c2=0.0
	for i in range(N):
		c1+=(v1[i]-v2[i])**2
	c1=c1**0.5
	for i in range(N):
		tmp=(v1[i]-v2[i])/v1[i]
		if tmp>=c2:
			c2=tmp
	conv=((c1<eps1)&(c2<eps2))
	return ("||"+str(c1)+":"+str(eps1)+"||\n"+"||"+str(c2)+":"+str(eps2)+"||",conv)
def BuildPR(sequences_filename,REP,opt):
	'''
	Build PageRanks related to 1stON and Biased 1stON models (opt = "1stON"), and, VON and Unbiased VON models
	(opt = "VON"). For both VON and Unbiased VON PRs, the returned PageRanks are mapped onto the item space.

	'''

	################
	## PARAMETERS ##
	################

	alpha = [0.85]
	## Multiple alpha can be used
#	amin = 0.5
#	amax = 0.9
#	dalpha = 0.005
#	alpha = np.arange(amin,amax+dalpha,dalpha):

	##########
	## INIT ##
	##########

	Nodes={} ## Memory-nodes info as dict: node ID (int) -> [is a first-order node (1 or 0), node name (tuple)]
	Sources={} ## Sum of outgoing links weight as dict: node ID (int) -> (float)
	Dnode=[] ## List of dangling nodes
	## Reading links file
	F=open(sequences_filename.replace(".csv","")+"-"+opt+".txt","r").read()
	F=F.split("\n")
	F.remove("")
	Links=[]
	N=int(F[0])
	F.remove(F[0])
	NL=int(F[0])
	F.remove(F[0])

	N1=0 ## Numer of first-order nodes
	output=[]
	for n in range(N):
		Nodes[n+1]=[0,""]# 1 or 0 if it is a dangling node or not, name of the node, Nrep (Nrep = -1 is a default value, this value is non negative only for first order nodes
		Sources[n+1]=0.0
	for i in range(NL):
		Links.append([])
		tmp=F[i].split("\t")
		source=int(tmp[0])
		target=int(tmp[1])
		Sources[source]+=float(tmp[2])
		Links[i]=[float(source), float(target), float(tmp[2])]
	for l in range(NL):
		tmp=Links[l]
		tmp[2]=tmp[2]/Sources[tmp[0]]
	for s in Sources.keys():
		if Sources[s]==0:
			Dnode.append(s)

	print("there are ", len(Dnode), "dangling nodes")

	## Reading nodes file
	F=open(sequences_filename.replace(".csv","")+"-"+opt+".titles","r").read()#List of Nodes Name
	F=F.split("\n")
	F.remove("")
	for n in range(len(F)):
		name=Stats.getTuplefromString(F[n])
		Nodes[n+1]=[int(len(name)==1),name]
		if len(name)==1:
			N1+=1
	## Init Preferential teleportation vector
	PVec=np.zeros(N)
	if(opt=="1stON"):
		## Teleportation towards high represented nodes (Biased 1stON PR model)
		for n in range(N):
			PVec[n]=REP[Nodes[n+1][1]]
		PVec=PVec/PVec.sum()

	#################
	## COMPUTE PRs ##
	#################

	if opt =="1stON":
		print("Building 1stON and Biased 1stON PRs")
		for model in ["standard", "biased"]:
			for a in alpha:
				start_time = time.time()
				P=PR(Links,Nodes,Dnode,PVec,N,N1,NL,round(a,3),model)
				print("Running time for ",model,opt,"=",time.time()-start_time,"seconds\n")

				## Generate rankings
				tmp=sorted(range(len(P)), key=lambda x:P[x], reverse=True)

				##################
				## WRITE OUTPUT ##
				##################

				## Complete output
				if model == "standard" :
					prname="1stON-PR"
				if model == "biased" :
					prname="Biased-1stON-PR"
				out=open(sequences_filename.replace(".csv","")+"-"+opt+"-"+prname+"-"+str(round(a,3)).replace(".","")+".dat","w")
				print("writing output")
				out.write("K\tPR\tItem ID\tItem\n")
				for i in range(len(tmp)):
					p=tmp[i]
					out.write(str(i+1)+"\t"+str(P[p])+"\t"+str(p+1)+"\t"+str(Nodes[p+1][1])+"\n")
				out.close()
	if opt == "VON":
		print("Buiding VON and Unbiased VON PRs")
		for model in ["standard", "forder"]:
#			for a in np.arange(amin,amax+dalpha,dalpha):
			for a in alpha:
				start_time2=time.time()
				P=PR(Links,Nodes,Dnode,PVec,N,N1,NL,round(a,3),model)
				print("Running time for",model,opt,"=",(time.time()-start_time2),"seconds\n")

				## Generate rankings
				tmp=sorted(range(len(P)), key=lambda x:P[x], reverse=True)

				#############
				## MAPPING ##
				#############

				pP=projectedPR(P, sequences_filename, round(a,3),model) ## Mapping PR onto item space
	return output
def PR(Links,Nodes,Dnode,PVec,N,N1,NL,alpha,model):
	'''
	Compute PageRank from a list of links and nodes, with a power method. PVec is the preferential teleportation
	vector used for the random walk through the network.
	'''
	##########
	## INIT ##
	##########
	it = 0
	conv = False
	Phi=np.zeros(N) ## PageRank initialization
	Phi2=np.zeros(N) ## Temporary PageRank
	for i in range(N):
		Phi[i]=1.0/N

	##################
	## POWER METHOD ##
	##################

	print("Starting computing PageRank, with alpha =", alpha)
	while((conv==False)):
		k=0.0 ## Contribution from dangling nodes
		norm=0.0 ## 1-norm of PageRank vector
		for l in range(NL):
			tmp=Links[l]
			j=int(tmp[0]-1) ## Source node index in [0,N-1]
			i=int(tmp[1]-1) ## Target node index
			w=tmp[2] ## Weight
			Phi2[i]+=Phi[j]*w

		###################################
		## 1stON, BIASED 1stON AND VON PR##
		###################################

		if((model == "standard") | (model == "biased")):
			for dn in Dnode:
				k+=Phi[dn-1] ## In these models random walker teleports uniformly to one node from dangling node
			if(model == "standard"): ## 1stON PR or VON PR
				for i in range(N):
					Phi2[i]=alpha*(Phi2[i]+k/N)+(1.0-alpha)/N ## Uniform teleportation at each step depending on the dampig factor alpha
			if(model == "biased"): ## Biased 1stON PR
				for i in range(N):
					Phi2[i]=alpha*(Phi2[i]+(k*PVec[i]))+(1.0-alpha)*PVec[i] ## Biased 1stON PR uses a Nrep-biased preferential teleportation vector

		#####################
		## UNBIASED VON PR ##
		#####################

		if model == "forder": ## Unbiased VON PR
			for dn in Dnode:
				k+=Phi[dn-1]
			for i in range(N):
				Phi2[i]=alpha*(Phi2[i]+(Nodes[i+1][0]*k)/N1) ## Random walker teleports uniformly towards first-order nodes from any dangling node
			for i in range(N):
				Phi2[i]+=Nodes[i+1][0]*((1.0-alpha)/N1) ## First-order-node teleportation at each step depending on alpha

		######################
		## CONVERGENCE TEST ##
		###################### 

		norm=np.sum(Phi2)
		it+=1
		info,conv=IsConverged(conv,Phi,Phi2,N)

		####################
		## NEXT ITERATION ##
		####################

		for i in range(len(Phi)):
			tmp=Phi2[i]
			Phi[i]=tmp
			Phi2[i]=0.0
	print("PageRank has been computed in ", it, "iterations")
	return Phi
def projectedPR(pr, sequences_file, alpha,model):
	'''
	Mapping PR vector onto items space. PR value associated to item "i" is the sum of PR values associated to its
	memory-node representations
	'''
	##########
	## INIT ##
	##########

	Items=open(sequences_file.replace(".csv","")+"-1stON.titles","r").read() ## Name of items are equivalent to name of nodes in case of 1stON
	Items=Items.split("\n")
	Items.remove("")
	ItemID={}
	cnt=0
	pPR=np.zeros(len(Items)) #Mapped PageRank initialization
	for i in range(len(Items)):
		name=Stats.getTuplefromString(Items[i])
		ItemID[name]=i+1

	#############
	## MAPPING ##
	#############

	Mapping={}

	## Reading memory-nodes file
	memNodes=open(sequences_file.replace(".csv","")+"-VON.titles","r").read()
	memNodes=memNodes.split("\n")
	memNodes.remove("")

	## Mapping 
	for n in range(len(pr)):
		node=Stats.getTuplefromString(memNodes[n])
		item=node[-1:]
		if item not in Mapping.keys():
			Mapping[item]={}
		Mapping[item][node]=pr[n]
	for i in Mapping:
		pPR[ItemID[i]-1]=sum(Mapping[i].values())

	##Normalization
	norm=sum(pPR)
	for i in range(len(pPR)):
		pPR[i]=pPR[i]/norm

	## Ranking
	sortPR=sorted(range(len(pPR)), key=lambda k : pPR[k], reverse=True)
	if model == "standard":
		prname="VON-PR"
	if model == "forder":
		prname="Unbiased-VON-PR"
	out=open(sequences_file.replace(".csv","")+"-VON-"+prname+"-"+str(alpha).replace(".","")+".dat","w")
	out.write("K\tPR\tItem ID\tItem\n")
	rank=1
	for i in sortPR:
		out.write(str(rank)+"\t"+str(pPR[i])+"\t"+str(ItemID[Stats.getTuplefromString(Items[i])])+"\t"+Items[i]+"\n")
		rank+=1
	out.close()
	return pPR

##########
## MAIN ##
##########

sequences_file=sys.argv[1] ## Input sequences file name

## Nrep distribution
print("Computing Nrep distribution from", sequences_file)
dRep=getRep(sequences_file.replace(".csv","")+"-VON.titles")

## Computing PageRanks
print("Computing PageRanks related to 1stON models")
BuildPR(sequences_file,dRep,"1stON")
print("Computing PageRanks related to VON models")
BuildPR(sequences_file,dRep,"VON")
print("done")
