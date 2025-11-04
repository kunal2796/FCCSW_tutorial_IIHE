
import os, copy

#Mandatory: List of processes  
processList = {
    'p8_ee_Zqq_ecm91':{'fraction':1.0},
}

#Mandatory: Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics
# prodTag     = "FCCee/winter2023/IDEA/"

#Optional: output directory, default is local running directory
outputDir   = "./outputs/"

# Define the input dir (optional)
inputDir    = "./localSamples/"

#Optional: ncpus, default is 4
# nCPUS       = 8
# nCPUS       = 1

#Optional running on HTCondor, default is False
# runBatch    = True

#Optional batch queue name when running on HTCondor, default is workday  
# batchQueue = "longlunch"

#Optional computing account when running on HTCondor, default is group_u_FCC.local_gen
# compGroup = "group_u_FCC.local_gen"




# additional/custom C++ functions, defined in header files (optional)
includePaths = ["functions.h"]

# Jet clustering wrapper
jetClusteringHelper = None



## latest particle transformer model, trained on 9M jets in winter2023 samples
model_name = "fccee_flavtagging_edm4hep_wc_v1"

## model files needed for unit testing in CI
url_model_dir = "https://fccsw.web.cern.ch/fccsw/testsamples/jet_flavour_tagging/winter2023/wc_pt_13_01_2022/"
url_preproc = "{}/{}.json".format(url_model_dir, model_name)
url_model = "{}/{}.onnx".format(url_model_dir, model_name)

## model files locally stored on /eos
model_dir = (
    "/eos/experiment/fcc/ee/jet_flavour_tagging/winter2023/wc_pt_13_01_2022/"
)
local_preproc = "{}/{}.json".format(model_dir, model_name)
local_model = "{}/{}.onnx".format(model_dir, model_name)

## get local file, else download from url
def get_file_path(url, filename):
    if os.path.exists(filename):
        return os.path.abspath(filename)
    else:
        urllib.request.urlretrieve(url, os.path.basename(url))
        return os.path.basename(url)


weaver_preproc = get_file_path(url_preproc, local_preproc)
weaver_model = get_file_path(url_model, local_model)

from addons.ONNXRuntime.jetFlavourHelper import JetFlavourHelper
from addons.FastJet.jetClusteringHelper import (
    ExclusiveJetClusteringHelper,
)

jetFlavourHelper = None


#Mandatory: RDFanalysis class where the use defines the operations on the TTree
class RDFanalysis:

    #__________________________________________________________
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
        
        #build psedo-jets with the Reconstructed final particles
        df = df.Define("pseudo_jets", "JetClusteringUtils::set_pseudoJets(RP_px, RP_py, RP_pz, RP_e)")

        #EE-KT ALGORITHM
        # jet clustering (ee-kt) before reconstructing SVs in event
        #run jet clustering with all reco particles. ee_kt_algorithm, exclusive clustering, exactly 2 jets, E-scheme
        df = df.Define("FCCAnalysesJets_ee_kt", "JetClustering::clustering_ee_kt(2, 2, 1, 0)(pseudo_jets)")
        #get the jets out of the structure
        df = df.Define("jet_ee_kt", "JetClusteringUtils::get_pseudoJets(FCCAnalysesJets_ee_kt)")
        #get the jet constituents out of the structure
	    # df = df.Define("jetconstituents_ee_kt", "JetClusteringUtils::get_constituents(FCCAnalysesJets_ee_kt)")
        #get some variables
        df = df.Define("jet_ee_kt_px",         "JetClusteringUtils::get_px(jet_ee_kt)")
        df = df.Define("jet_ee_kt_py",         "JetClusteringUtils::get_py(jet_ee_kt)")
        df = df.Define("jet_ee_kt_pz",         "JetClusteringUtils::get_pz(jet_ee_kt)")
        df = df.Define("jet_ee_kt_e",          "JetClusteringUtils::get_e(jet_ee_kt)")
        
        #ANTI-KT ALGORITHM
        #run jet clustering with all MC particles. kt_algorithm, R=0.5, exclusive clustering, exactly 4 jets, E-scheme
        df = df.Define("FCCAnalysesJets_antikt", "JetClustering::clustering_antikt(0.5, 0, 0, 1, 0)(pseudo_jets)")
        #get the jets out of the structure
        df = df.Define("jet_antikt", "JetClusteringUtils::get_pseudoJets(FCCAnalysesJets_antikt)")
        #get the jet constituents out of the structure
        # df = df.Define("jetconstituents_antikt", "JetClusteringUtils::get_constituents(FCCAnalysesJets_antikt)")
        #get some jet variables
        df = df.Define("jet_antikt_e",  "JetClusteringUtils::get_e(jet_antikt)")
        df = df.Define("jet_antikt_px", "JetClusteringUtils::get_px(jet_antikt)")
        df = df.Define("jet_antikt_py", "JetClusteringUtils::get_py(jet_antikt)")
        df = df.Define("jet_antikt_pz", "JetClusteringUtils::get_pz(jet_antikt)")
        
        #EE-GENKT ALGORITHM
        #run jet clustering with all reconstructed particles. ee_genkt_algorithm, R=0.5, inclusive clustering, E-scheme 
        df = df.Define("FCCAnalysesJets_ee_genkt", "JetClustering::clustering_ee_genkt(0.5, 0, 0, 1, 0, 1)(pseudo_jets)")
        #get the jets out of the struct
        df = df.Define("jet_ee_genkt",           "JetClusteringUtils::get_pseudoJets(FCCAnalysesJets_ee_genkt)")
        #get the jets constituents out of the struct
        # df = df.Define("jetconstituents_ee_genkt","JetClusteringUtils::get_constituents(FCCAnalysesJets_ee_genkt)")
        #get some variables
        df = df.Define("jet_ee_genkt_e",         "JetClusteringUtils::get_e(jet_ee_genkt)")
        df = df.Define("jet_ee_genkt_px",        "JetClusteringUtils::get_px(jet_ee_genkt)")
        df = df.Define("jet_ee_genkt_py",        "JetClusteringUtils::get_py(jet_ee_genkt)")
        df = df.Define("jet_ee_genkt_pz",        "JetClusteringUtils::get_pz(jet_ee_genkt)")
        

        # Calculate invariant mass of jet pair using jet kinematic variables
        df = df.Define("Z_invM_ee_kt",          "fastjet::PseudoJet event; for (auto &jet : jet_ee_kt){event += jet;} return event.m();")



        # Computing the MC flavour of each jet
        df = df.Define("Z_flavour_MC",          "FCCAnalyses::AddFunctions::get_Z_flavour(jet_ee_kt.size(), Particle)")


        ## perform N=2 jet clustering using wrapper
        global jetClusteringHelper
        jetClusteringHelper = ExclusiveJetClusteringHelper(
            "ReconstructedParticles", 2
        )

        df = jetClusteringHelper.define(df)

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




        # Should add a filtering of events according to Z invariant mass +-20 GeV
        df = df.Filter("Z_invM_ee_kt >= 71.2 && Z_invM_ee_kt<=111.2")

        
        return df

    #__________________________________________________________
    #Mandatory: output function, please make sure you return the branchlist as a python list
    def output():
        branchList = [

            # EE-KT
            "jet_ee_kt_px",
            "jet_ee_kt_py",
            "jet_ee_kt_pz",
            "jet_ee_kt_e",

            # EE-GENKT
            "jet_ee_genkt_px",
            "jet_ee_genkt_py",
            "jet_ee_genkt_pz",
            "jet_ee_genkt_e",

            # ANTI-KT
            "jet_antikt_px",
            "jet_antikt_py",
            "jet_antikt_pz",
            "jet_antikt_e",

            # To be added in some exercise
            "Z_invM_ee_kt",

            # Flavour
            "Z_flavour_MC",

                ]

        ##  outputs jet properties
        branchList += jetClusteringHelper.outputBranches()

        ## outputs jet scores and constituent breakdown
        branchList += jetFlavourHelper.outputBranches()

        return branchList
