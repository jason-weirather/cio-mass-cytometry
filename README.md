# cio-mass-cytometry

The Mass Cytometry pipeline works in the stages of 

## Stage 0 - Template Ingestion

Create/read in an Excel sheet that defines the Panel, The samples, And annotations for analysis.

#### 1. Create a template.

`$ masscytometry-templates create ./template.xlsx`

#### 2. (optional) Automatically populate the sample nfile paths and sample names

`$ masscytometry-templates add_samples  --samples_path /my/FCS/storage/directory/ --output_path myproject-with-samples.xlsx --sample_name_regex '(\d+_T\d)' template.xlsx`

#### 3. Fill in the template with project details

##### a. The Panel Parameters

This is a simple description of 

##### b. The Panel Definition

If you're not sure what is included in your panel you can export the panel parameters from any of your FCS files with the following R snippit:

```R
library(flowCore)
fcs <- read.FCS('/my/files/filename.fcs')
df <- pData(parameters(fcs))
write.csv(df,'markers.csv')
df
```

##### c. The Sample Annotations

##### d. The Meta data

#### 4. Concert the excel template to a input json file

`$ masscytometry-templates ingest --output_ingested_json inputs.json annotated-labeled.xlsx`

The generated json file will serve as the Stage 1 pipeline input.

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