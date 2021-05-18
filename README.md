# cio-mass-cytometry

The Mass Cytometry pipeline works in the stages of 

## Stage 0 - Template Ingestion

Read in an Excel sheet that defines the Panel, The samples, And annotations for analysis.

## Stage 1 - QC and overclustering

### Process the FCS files and generate QC metrics

* Generate cell counts
* Generate distribution plots of marker intensities

#### Future:
* Generate spillover plots
* Generate batch effect plots (i.e. CellMixS)

### Generate FlowSOM clusters and MEM annotations

### Generate template for cluster annototation

## Stage 2 - Read annotated clusters and execute analysis