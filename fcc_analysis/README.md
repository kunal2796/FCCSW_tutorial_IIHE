FCC: Producing flat root trees using FCCAnalyses
===================================================================================

In this part of the tutorial we will use FCCAnalyses to read EDM4hep files and process events using RDataFrame. We will start by printing the kinematics of individual particles, before clustering Z->qq events into jets. We will compute the invariant mass and MC flavour of these jets, before using ParT to perform inference on our jets.

## Building FCCAnalyses

Let's start by building FCCAnalyses. 

```
git clone --branch pre-edm4hep1 https://github.com/HEP-FCC/FCCAnalyses.git
cd FCCAnalyses
source ./setup.sh
mkdir build install && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
make install -j $(($(nproc)-1))
cd ..
mkdir tutorial && cd tutorial
```

## Samples

We will now make a directory `localSamples` where we will copy our source file to. 

```
mkdir localSamples && cd localSamples
wget -O p8_ee_Zqq_ecm91.root https://cernbox.cern.ch/s/MyokoucLtrH6l9y/download
cd ..
```

## Anatomy of an analysis.py file

In this directory you should find a bare-bones `analysis.py` file which should run as is and output some kinematic variables for the set of reconstructed particles.
Note that the top of the file contains the configuration block where we will define what samples we wish to run over, as well as other computing parameters.

In this tutorial we will run over the Z->qq sample we downloaded earlier, so we specify the file in the `processList`
```
#Mandatory: List of processes
processList = {
     'p8_ee_Zqq_ecm91':{'fraction':1.0},
}
```




