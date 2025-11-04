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

In this directory you should find a bare-bones `analysis_0.py` file which should run as is and output some kinematic variables for the set of reconstructed particles. Start by copying the file over to your `tutorial` directory, and opening it in your favourite text editor.
Note that the top of the file contains the **configuration block** where we will define what samples we wish to run over, as well as other computing parameters.

In this tutorial we will run over the Z->qq sample we downloaded earlier, so we specify the file in the `processList`
```
#Mandatory: List of processes
processList = {
     'p8_ee_Zqq_ecm91':{'fraction':1.0},
}
```

The `outputDir` defines where our flat root tree will be output, while the `inputDir` specifies the directory where our EDM4hep file is located.
```
#Optional: output directory, default is local running directory
outputDir   = "./outputs/"

# Define the input dir (optional)
inputDir    = "./localSamples/"
```

It is worth noting that for this tutorial we will be using a locally saved file, but in general we may use to use one of the many centrally-produced files documented [here](https://fcc-physics-events.web.cern.ch/fcc-ee/rec/winter2023). In that case we should specify the respective `prodTag`
```
#Mandatory: Production tag when running over EDM4hep centrally produced events, this points to the yaml files for getting sample statistics
prodTag     = "FCCee/winter2023/IDEA/"
```

The **RDFAnalysis** class defines how the EDM4hep file should be processed. In particular, the `analysers` function defines what operations should be performed and what branches should be defined in the dataframe 
```
    #Mandatory: analysers funtion to define the analysers to process, please make sure you return the last dataframe, in this example it is df2
    def analysers(df):
        
        # Gen particles
        # .Alias("Particle0", "Particle#0.index")
        # .Alias("Particle1", "Particle#1.index")

        # Reco'd particles
        df = df.Define("RP_px",        "ReconstructedParticle::get_px(ReconstructedParticles)")
        df = df.Define("RP_py",        "ReconstructedParticle::get_py(ReconstructedParticles)")
        df = df.Define("RP_pz",        "ReconstructedParticle::get_pz(ReconstructedParticles)")               
        df = df.Define("RP_e",         "ReconstructedParticle::get_e(ReconstructedParticles)")
        df = df.Define("RP_charge",    "ReconstructedParticle::get_charge(ReconstructedParticles)")
        
        
        return df
```
In this case we are simply using helper functions to retrieve the reconstructed particle kinematics.

The `output` function defines the branches that will be saved to the output root tree
```
    #Mandatory: output function, please make sure you return the branchlist as a python list
    def output():
        branchList = [

            "RP_px",
            "RP_py",
            "RP_pz",
            "RP_e",
            "RP_charge",


                ]

        return branchList
```

### Exercise 1:
Having seen the basic elements of an `analysis.py` file, it is worth trying to run `analysis_0.py` in order to verify our setup. Try the following command
```
fccanalysis run analysis_0.py
```
Did everything run correctly? Inspect the `outputs/p8_ee_Zqq_ecm91.root` file and make sure the branches contain what you expect.



## Clustering jets

Having seen how to print basic variables, we now turn our attention to clustering jets. FCCAnalyses implements a variety of jet clustering algorithms using FastJet as defined [here](https://github.com/HEP-FCC/FCCAnalyses/blob/master/addons/FastJet/src/JetClustering.cc). 

The first step in any of the available jet clustering algorithms is to define a set of `pseudo_jets`. These are purely kinematic objects on which the jet clustering algorithm acts. Add the following line to your `analysers` function
```
#build psedo-jets with the Reconstructed final particles
df = df.Define("pseudo_jets", "JetClusteringUtils::set_pseudoJets(RP_px, RP_py, RP_pz, RP_e)")
```
As an example we will cluster jets using the ee-kt algorithm. Include the following line in your `analysers` function
```
#run jet clustering with all reco particles. ee_kt_algorithm, exclusive clustering, exactly 2 jets, E-scheme
df = df.Define("FCCAnalysesJets_ee_kt", "JetClustering::clustering_ee_kt(2, 2, 1, 0)(pseudo_jets)")
```

Next we can retrieve the `pseudo_jets` as well as some useful kinematic variables. Include the following lines in your `analysers` function
```
#get the jet constituents out of the structure
df = df.Define("jet_ee_kt", "JetClusteringUtils::get_pseudoJets(FCCAnalysesJets_ee_kt)")
#get some variables
df = df.Define("jet_ee_kt_px",         "JetClusteringUtils::get_px(jet_ee_kt)")
df = df.Define("jet_ee_kt_py",         "JetClusteringUtils::get_py(jet_ee_kt)")
df = df.Define("jet_ee_kt_pz",         "JetClusteringUtils::get_pz(jet_ee_kt)")
df = df.Define("jet_ee_kt_e",          "JetClusteringUtils::get_e(jet_ee_kt)")
```

Finally, we add the jet variables to our `branchList`
```
# EE-KT
"jet_ee_kt_px",
"jet_ee_kt_py",
"jet_ee_kt_pz",
"jet_ee_kt_e",
```

Try re-running the code using 
```
fccanalysis run analysis_0.py
```
Did everything run correctly? Are you able to see the jet variables in the tree?

### Exercise 2:

Try to also implement the additional jet algorithms in your code:
1. Anti-kT with the following parameters: (0.5, 0, 0, 1, 0)
2. ee-genkT with the following parameters: (0.5, 0, 0, 1, 0, 1)
In both cases you should save kinematic variables for each jet.

Using your favourite method (e.g. uproot, PyROOT, native ROOT), read the relevant branches from the output .root file and compute the invariant mass of the Z boson by adding the 4-momenta of the jets in each event. What do you see? Which jet clustering method seems to perform best?




















