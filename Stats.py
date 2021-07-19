from scipy import stats as st
def getTuplefromString(string):
	tmp=string
	rez=[]
	tmp=tmp.replace("(","")
	tmp=tmp.replace(")","")
	tmp=tmp.split(",")
	for e in tmp:
		if e != "":
			if "\'" in e:
				rez.append(e.split("\'")[1])
			else:
				rez.append(int(e))
	return tuple(rez[0:])
def getCorr(t1,t2,col):
	C={}
	for i in range(len(t1)):
		tmp=t1[i].split("\t")
		C[tmp[col-1]]=[i+1,-1]
	for i in range(len(t2)):
		tmp=t2[i].split("\t")
		C[tmp[col-1]][1]=i+1
	return C
def getOlap(t1,t2,col,opt):
	C=[]
	T1=[]
	T2=[]
	for i in t1:
		T1.append(i.split("\t")[col-1])
	for i in t2:
		T2.append(i.split("\t")[col-1])
	if opt=='N':#Exact Overlap
		for i in range(len(T1)):
			z=0.0
			for j in range(i):
				if T2[j]==T1[j]:
					z+=1
			C.append(z/(i+1))
	if opt == 'O':#Include Overlap
		for i in range(len(T1)):
			z=0.0
			for j in range(i):
				if T2[j] in T1[:i+1]:
					z+=1
			C.append(z/(i+1))
			
	return C
def InitList(n):
	C=[]
	for i in range(n):
		C.append([])
	return C
def getMaxSwitch(f1,f2,col):
	t1=open(f1,"r").read()
	t1=t1.split("\n")
	t2=open(f2,"r").read()
	t2=t2.split("\n")
	t1.remove("")
	t2.remove("")
	Corr=getCorr(t1,t2,col)
	C=0
	for i in Corr.keys():
		switch=Corr[i][0]-Corr[i][1]
		if abs(switch)>=C:
			C=abs(switch)
	return C
def getSpearmanCoeff(f1,f2,col):
	t1=open(f1,"r").read()
	t2=open(f2,"r").read()
	t1=t1.split("\n")
	t2=t2.split("\n")
	t1.remove("")
	t2.remove("")
	Corr=getCorr(t1,t2,col)
	X=[]
	Y=[]
	for i in Corr:
		X.append(Corr[i][0])
		Y.append(Corr[i][1])
	s1=0.0
	s2=0.0
	s3=0.0
	M1=sum(list(range(1,len(X)+1)))/len(X)
	M2=sum(list(range(1,len(Y)+1)))/len(Y)
	for i in range(len(X)):
		s1+=(X[i]-M1)*(Y[i]-M2)
		s2+=(X[i]-M1)**2
		s3+=(Y[i]-M2)**2
	sp=s1/((s2)**0.5*(s3)**0.5)
	return sp
def getKendall(f1, f2):
        t1=Read(f1)
        t2=Read(f2)
        size=len(t1)
        x1=[0]*size
        x2=[0]*size
        for i in range(size):
                tmp1=t1[i].split("\t")
                tmp2=t2[i].split("\t")
                x1[int(tmp1[2])-1]=i+1#List of Ranks
                x2[int(tmp2[2])-1]=i+1#List of Ranks
        tau, p_value=st.kendalltau(x1,x2)
        return tau, p_value
