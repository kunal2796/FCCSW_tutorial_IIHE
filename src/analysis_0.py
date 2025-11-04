
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
        



        return df

    #__________________________________________________________
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
