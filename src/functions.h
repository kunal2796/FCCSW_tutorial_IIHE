#ifndef AddFunctions_H
#define AddFunctions_H

#include <iostream>
#include <cmath>
#include <vector>
#include <math.h>

#include "TLorentzVector.h"
#include "ROOT/RVec.hxx"
#include "edm4hep/ReconstructedParticleData.h"
#include "edm4hep/MCParticleData.h"
#include "edm4hep/ParticleIDData.h"
#include "ReconstructedParticle2MC.h"


namespace FCCAnalyses { namespace AddFunctions {


  
 
 
ROOT::VecOps::RVec<int> get_Z_flavour(size_t nJets, ROOT::VecOps::RVec<edm4hep::MCParticleData> MCin){
  int flav = 0;
  for(auto& p : ?){
    if(p.generatorStatus == 23){
      ? = std::abs(p.PDG);
      break;
    }
  }
  ROOT::VecOps::RVec<int> result(?, ?);
  return result;
} 




 
 

}}

#endif
