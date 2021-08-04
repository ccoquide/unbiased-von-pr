# unbiased-von-pr

# Source Code and Datasets for submission "PageRank computation for Higher-Order Networks" (Complex Network Conference 2021)

**Note:** This folder does not contain a main script for all experiments but different ones explained below 

## Dependencies and Setup

1. Python, version >=3 (experiments made with version 3.8.5)
2. [NumPy](https://numpy.org/) python library (command `pip install numpy`) (experiments made with version 1.19.4)

**The experiments' scripts also use third party codes.**

- Files `BuildRulesFast.py` and `BuildNetwork.py` are used for extracting relevant extensions (see Section III of the paper) from an input data set, and to build VON networks (or 1stON networks). The original scripts are available at https://github.com/xyjprc/hon (last check June 2021), moreover, we have made minor modifications in these scripts.

## Datasets

The three datasets used in the paper are available here. An explanation of each dataset is given in Section V of the paper.

1. `maritime.csv`: Maritime sequences dataset (default dataset used in the script below)
2. `maritime-info.csv` : Maritime sequences' items related information (Ports name)
3. `airports.tar.gz` Airports sequences + Items related information (compressed). 
4. `taxis.tar.gz` Taxis sequences dataset + Items related information compressed). 

The structure of input files is described at the end of the document. 

## Reproducing the experiments

### Building Networks and Extracting statistics (Nrep-Rank and Visit-Rank) from input files

run `python3 getNetwork.py maritime.csv` creates file containing list of memory-nodes (`.titles` file extension) sorted arbitrarly and table of links (`.txt` file extension) for each network model.

1. `maritime-1stON.titles` : List of nodes in case of 1stON (equivalent to the list of items) 
2. `maritime-VON.titles` : Lis of nodes (memory-nodes) for VON
3. `maritime-1stON.txt` : Table of links for 1stON
4. `maritime-VON.txt` : Table of links for VON

The structure of the files related tables of links is described at the end of the document.

Statistics about Nrep and Item Visits is recorded in `maritime-Stats.dat`where the 1st column is related to the item label (tuple of int), 2nd column is for corresponding Nrep-Rank (int) and last one for Visit-Rank (int). 
### Computing PageRanks for a given damping factor alpha (default is 0.85)

`buildPR.py` generates for each chosen alpha (change alpha into a list of values at line 53 permits to generate several files) one PageRank related file for each PR model presented in section IV.
Run command `python3 buildPR.py maritime.csv` to automatically obtain all PR files. Note that the name of the input sequences is always used as argument since each output file name is based on it.

Output files are the following

1. `maritime-1stON-1stON-PR-085.dat` : 1stONPR in case of maritime data set and alpha=0.85
2. `maritime-1stON-Biased-1stON-PR-085.dat` : Obtained with Biased 1stONPR model
3. `maritime-VON-VON-PR-085.dat` : VONPR model obtained with Standard PR model applied on VON
4. `maritime-VON-Unbiased-VON-PR-085.dat` : Obtained with Unbiased VONPR model

The structure of these files is detailed at the end of this docuement.

### Generate final output containing all PageRank probabilities (or ranks) and statistic based rankings

The command `python3 getFinal.py maritime.csv 0.85` gives all PageRank computed with alpha = 0.85 and statistics related to maritime data set. Two files are created: `maritime-scores-085.dat` (PageRank values) and `maritime-ranks-085.dat` (PageRank Ranks).

The structure of these files is detailed at the end of this document.

*Warning:** All output file are created at the location than the input sequences file.
### Using other data sets
All input sequences file has to be formated as following

        ID1 i1 i2 i3 ...
        ID2 i5 i6 i2 ...
        ID3 i2 i4 ...
        ...

Where `IDX` is the X-th sequence ID (if there is no sequence identificator, please change `ID=True` into `ID=False` at line 21 in `getNetwork.py` python script. Separator are simple space " ", please change `sep` variable at line 20 if the script for an other column separator. The first element of each line is the ID of the sequence. The next elements or the sequence of items label (int) 'iX'.

In case of an other data set, with corresponding filename `dataset.csv`, just replace maritime.csv with data.csv while running the python script. All output filenames will start with `dataset`.

### Structure of output files

Table of links `dataset-netmodel.txt`, with `dataset` being one of maritime, airports or taxis and `netmodel` being either `1stON` (first-order network model) or `VON` (variable-order network model) :

       N_nodes
       N_links
       S1 T1 W1
       S2 T2 W2
       ...

Where `N_nodes` and `N_links` are the number of nodes and links, `SX` is the source node ID for the X-th link, and `TX` the corresponding target node's ID and the weight of this link is `WX`. For the i-th node (from the top) present in the list of nodes (file with `.titles` extension), its ID is simply `i`. As such, the entry `1 2 0.5` in the table of links means that a link going from the 1st node of the list of nodes to the second one of the same list, exists and has a weight of `0.5`. The column separator is `\t`.

PageRank files `dataset-netmodel-PRmodel-alpha.dat`, with PRmodel being either `1stON-PR`, `VON-PR`, `Biased-1stON-PR` or `Unbiased-VON-PR`, and  alpha, the damping factor, being such as in case of a value of 0.85 the filename will have `085` in its name :

      1 PR1 n1 N1
      2 PR2 n2 N2
      3 PR3 n3 N3
      ...

Where thirs element of each lin (1,2, ...) is the rank, `PRX` is the PageRank value related to the item ranked `X` with the corresponding PageRank model, `nX` is the node's ID (int) and `NX` the node label (tuple of ints). The column separator is `\t`.

`dataset-scores-alpha.dat` :

     I1 PR1a PR1b PR1c PR1d RR1 VR1
     I2 PR2a PR2b PR2c PR2d RR2 VR2
     I3 PR3a PR2b PR3c PR3d RR3 VR3
     ...

Where `IX` is the item name (found from the item related information in `dataset-info.csv`), `PRXa` is the corresponding PageRank value computed with 1stON PR model, `PRXb` is related to VON PR model, `PRXc` to Biased 1stON PR and `PRXd` is for the Unbiased VON PR model. Finally, `RRX` and `VRX` are respectivly the Nrep ranking and Visit Ranking ranks. The column separator is `\t`.

`dataset-ranks-alpha.dat` :

    I1 K1a K1b K1c K1d RR1 VR1
    I2 K2a K2b K2c K2d RR2 VR2
    I3 K3a K3b K3c K3d RR3 VR3
    ...

Where 'KX' refers for the PageRank rank of the item Xth item, `a`, `b`, `c` and `d` have the same meaning than in `dataset-scores-alpha.dat` file. The column separator is `\t`.
