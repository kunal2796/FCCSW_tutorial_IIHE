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
*Did everything run correctly? Inspect the `outputs/p8_ee_Zqq_ecm91.root` file and make sure the branches contain what you expect.*



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
*Did everything run correctly? Are you able to see the jet variables in the tree?*

### Exercise 2:

Try to also implement the additional jet algorithms in your code:
1. Anti-kT with the following parameters: (0.5, 0, 0, 1, 0)
2. ee-genkT with the following parameters: (0.5, 0, 0, 1, 0, 1)
In both cases you should save kinematic variables for each jet. You will find the source code [here](https://github.com/HEP-FCC/FCCAnalyses/blob/master/addons/FastJet/src/JetClustering.cc), where you can find the correct function.

Using your favourite method (e.g. uproot, PyROOT, native ROOT), read the relevant branches from the output .root file and compute the invariant mass of the Z boson by adding the 4-momenta of the jets in each event. 
*What do you see? Which jet clustering method seems to perform best?*


### Exercise 3:

It can be convenient to compute simple quantities such as the invariant mass within FCCAnalyses itself. Defining a dedicated function can be somewhat overkill (though we will see how later). For now try to compute the invariant mass using the `Define` function of the dataframe. The syntax is the following
```
df = df.Define("Z_invM_ee_kt",          "int result; for (size_t i=0; i<10; ++i){result += i;} return result;")
```
Hints:
 - You can freely call other previously defined columns in the dataframe
 - `pseudo_jets` can be added using the `+` operator
 - The invariant mass of a `pseudo_jet` can be computed using `.m()`

***Note: At this point you should feel free to copy over the `analysis_1.py` file from the `src` directory of this repo to your `tutorial` folder if you have struggled with any of the previous exercises but still wish to follow along.***



## Adding functions to FCCAnalyses

In this section we will extend our `analysis.py` file to include a `functions.h` file where we will define functions to be compiled at runtime. Let's begin by adding the following line to our configuration block
```
# additional/custom C++ functions, defined in header files (optional)
includePaths = ["functions.h"]
```

Next let's actually define our `functions.h` file. For simplicity you will find the `functions.h` file in the `src` directory with some helpful boilerplate. Copy it over to your `tutorial` directory.
The file already contains the a function called `get_Z_flavour` that we will use to compute the flavour of the quarks each Z boson decayed to. Some parts of the function are missing. 


### Exercise 4:

Can you fill in the missing parts of `get_Z_flavour`?



Now that we have fixed `get_Z_flavour` we can call in from our `analysers` function. Include the following line (and don't forget to add the flavour to the `branchList`
```
# Computing the MC flavour of each jet
df = df.Define("Z_flavour_MC",          "FCCAnalyses::AddFunctions::get_Z_flavour(jet_ee_kt.size(), Particle)")
```

Test the added function by running 
```
fccanalysis run analysis_1.py
```
*Did everything run correctly? Are the MC flavours of each jet defined?*

## Jet flavour tagging

In this part of the tutorial we will see how to perform inference on our jets within FCCAnalyses. Before proceeding, it is worth noting that FCCAnalyes provides a wrapper for the jet clustering steps that implements the ee-kt algorithm, which was found to be the most appropriate for FCC-ee studies.

Start by including the following line in the configuration block of your `analysis.py` file
```
# Jet clustering wrapper
jetClusteringHelper = None
```

Next, within the `analysers` function we call the jet clustering helper 
```
## perform N=2 jet clustering using wrapper
global jetClusteringHelper
jetClusteringHelper = ExclusiveJetClusteringHelper(
    "ReconstructedParticles", 2
)
df = jetClusteringHelper.define(df)
```
Note that the arguments are a string describing the particle collection we wish to cluster, as well as the number of jets per event.

The jet clustering helper provides the following syntax for printing kinematic variables of jets
```
##  outputs jet properties
branchList += jetClusteringHelper.outputBranches()
```
which should appear within `output()`.



***Note: At this point you should copy over the `analysis_2.py` file from the `src` directory of this repo to your `tutorial` folder. The jet flavour inference contains considerable boilerplate that has been included in `analysis_2.py`***


The jet flavour helper within FCCAnalyses requires an `.onnx` model file to be provided. These are often centrally provided and are specified in the configuration block of the `analysis.py` file
```
## latest particle transformer model, trained on 9M jets in winter2023 samples
model_name = "fccee_flavtagging_edm4hep_wc_v1"
...
## model files locally stored on /eos
model_dir = (
    "/eos/experiment/fcc/ee/jet_flavour_tagging/winter2023/wc_pt_13_01_2022/"
)
local_preproc = "{}/{}.json".format(model_dir, model_name)
local_model = "{}/{}.onnx".format(model_dir, model_name)
```

As the neural network input consists of several distinct particle classes, a dictionary mapping the various classes to their counterparts in the EDM4hep file must be provided
```
# Here we start the tagging stuff
collections = {
    "GenParticles": "Particle",
    "PFParticles": "ReconstructedParticles",
    "PFTracks": "EFlowTrack",
    "PFPhotons": "EFlowPhoton",
    "PFNeutralHadrons": "EFlowNeutralHadron",
    "TrackState": "EFlowTrack_1",
    "TrackerHits": "TrackerHits",
    "CalorimeterHits": "CalorimeterHits",
    "dNdx": "EFlowTrack_2",
    "PathLength": "EFlowTrack_L",
    "Bz": "magFieldBz",
}
```
and should appear in the `analysers` function.

















