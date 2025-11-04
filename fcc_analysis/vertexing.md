FCCAnalyses: Vertex Reconstruction
===================================================================================

Vertex reconstruction in FCCAnalyses follows the vertexing module of the LCFIPlus framework.

## Finding the Primary Vertex (PV)

First, we determine the tracks which are associated with the primary vertex.

```
df = df.Define("RecoedPrimaryTracks", "VertexFitterSimple::get_PrimaryTracks( EFlowTrack_1, true, 4.5, 20e-3, 300, 0., 0., 0.)")
```

Here, `EFlowTrack_1` is the collection of tracks, while the rest of the arguments specify the beam spot constraint.

These "primary" tracks can be used to fit the primary vertex and extract the vertex object:

```
df = df.Define("PrimaryVertexObject", "VertexFitterSimple::VertexFitter_Tk ( 1, RecoedPrimaryTracks, true, 4.5, 20e-3, 300) ")
df = df.Define("PrimaryVertex", "VertexingUtils::get_VertexData( PrimaryVertexObject )")
```

## Finding Secondary Vertices (SVs)

After reconstructing the primary vertex, the tracks forming the primary vertex must be removed from the collection of tracks. We refer to these as the "secondary" tracks.

```
df = df.Define("SecondaryTracks", "VertexFitterSimple::get_NonPrimaryTracks( EFlowTrack_1, RecoedPrimaryTracks )")
```

### Reconstructing SVs without jet clustering

SVs can be reconstructed before jet clustering, using all of the tracks from the event.

```
df = df.Define("SV_evt1", "VertexFinderLCFIPlus::get_SV_event(SecondaryTracks, EFlowTrack_1, PrimaryVertexObject)")
```

The same SV reconstruction can be done with a different interface:

```
df = df.Define("IsPrimary_based_on_reco",  "VertexFitterSimple::IsPrimary_forTracks( EFlowTrack_1,  RecoedPrimaryTracks )")
df = df.Define("SV_evt2", "VertexFinderLCFIPlus::get_SV_event(ReconstructedParticles, EFlowTrack_1, PrimaryVertexObject, IsPrimary_based_on_reco)")
```

### Reconstructing SVs with jet clustering

SVs can also be reconstructed after performing the jet clustering step. In this case, SVs are reconstructed separately with tracks from each jet of the event.

First, we perform jet clustering and extract the clustered jets and the collections of jet constituents:

```
df = df.Define("RP_px",  "ReconstructedParticle::get_px(ReconstructedParticles)")
df = df.Define("RP_py",  "ReconstructedParticle::get_py(ReconstructedParticles)")
df = df.Define("RP_pz",  "ReconstructedParticle::get_pz(ReconstructedParticles)")
df = df.Define("RP_e",   "ReconstructedParticle::get_e(ReconstructedParticles)")

df = df.Define("pseudo_jets", "JetClusteringUtils::set_pseudoJets(RP_px, RP_py, RP_pz, RP_e)")         # define pseudojets
df = df.Define("FCCAnalysesJets_ee_kt", "JetClustering::clustering_ee_kt(2, 2, 1, 0)(pseudo_jets)")    # perform jet clustering

df = df.Define("jets_ee_kt", "JetClusteringUtils::get_pseudoJets(FCCAnalysesJets_ee_kt)")              # extract jet objects
df = df.Define("jetconstituents_ee_kt", "JetClusteringUtils::get_constituents(FCCAnalysesJets_ee_kt)") # extract jet constituents       
```

Now, we can find SVs in the jets of the events as:

```
df = df.Define("SV_jet", "VertexFinderLCFIPlus::get_SV_jets(ReconstructedParticles, EFlowTrack_1, PrimaryVertexObject, IsPrimary_based_on_reco, jets_ee_kt, jetconstituents_ee_kt)")
```

## Extracting Properties of the SVs

Several functions exist in the library `VertexingUtils`, which can be used to calculate various properties of the SVs. A few examples are shown below:

```
df = df.Define("SV_jet_n",        "VertexingUtils::get_n_SV(SV_jet)")           # Number of SVs
df = df.Define("SV_jet_position", "VertexingUtils::get_position_SV( SV_jet )")  # SV position
df = df.Define("sv_mass",         "VertexingUtils::get_invM(SV_jet)")           # SV mass
df = df.Define("sv_p",            "VertexingUtils::get_pMag_SV(SV_jet)")        # SV momentum
```

All of these functions can also run on the objects `SV_evt1` and `SV_evt2`, which are the reconstructed SVs without jet clustering.
