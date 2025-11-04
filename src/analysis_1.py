
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

                ]

        return branchList
