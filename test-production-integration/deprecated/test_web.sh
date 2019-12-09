#Doing Metabolomics V1:

wget "http://localhost:5051/process?task=55230cf0fbd14b95bc0eced5bb61353f"

#Doing Metabolomics V2:

wget "http://localhost:5051/process?task=a9cb57ff8dfb4eeba04d73ba1ff3bcfd"

#Standard from MolNetEnhancer

wget "http://localhost:5051/process?task=bda30509c61347fba19ff8c6064d7801"

#Standard from MS2LDA

wget "http://localhost:5051/process?task=aa63a632d3c24c338e7a5ed046678564"

#Doing Tag Tracker

wget "http://localhost:5051/process?task=a9cb57ff8dfb4eeba04d73ba1ff3bcfd&filter=tagtracker&source=drugs"

#Doing Mol Net Enhancer input

wget "http://localhost:5051/process?task=bda30509c61347fba19ff8c6064d7801&molnetenhancer_superclass=Lipids%20and%20lipid-like%20molecules&filter=molnetenhancer"


### Error Cases

#Too large network
wget "http://localhost:5051/process?task=2385676aea054d0689de6c839e5d6633"

