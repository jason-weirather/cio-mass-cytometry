# cio-mass-cytometry

This pipeline helps streamline the workflow of CATALYST (1)

1. Nowicka M et. al. CyTOF workflow: differential discovery in high-throughput high-dimensional cytometry datasets. F1000Res. 2017 May 26;6:748. doi: 10.12688/f1000research.11622.3.

### Input: 

1. FCS files (one file per sample, already cleaned for dead cells and debris)
2. Sample annotations

### Output:

1. Figures including QC, UMAPs, heatmaps, and stacked bar plots
2. Data from labeled cell-type clusters and the marker expression on each cell type

## Quickstart

Get the docker image and start a jupyter lab server, example on Linux running the jupyter lab server as yourself:

```bash
docker pull vacation/cio-mass-cytometry:latest
docker run --user $(id -u):$(id -g) -v /your/working/directory:/your/working/directory -w /your/working/directory --rm -p 8888:8888 vacation/cio-mass-cytometry:latest
```

Look for the jupyter lab server address and paste it into your browser:

*Example (don't copy this, find the address in your terminal):* `http://127.0.0.1:8888/lab?token=404afbf16b8a48c6a40c860aad2ad494`

# Example

I used the `cytomulate` package (2) to create a synthetic dataset with attributes similar to a 13 marker Levine et. al. 2015 dataset (3).

2. Yang Y et al. Cytomulate: accurate and efficient simulation of CyTOF data. Genome Biol. 2023 Nov 16;24(1):262. doi: 10.1186/s13059-023-03099-1.
3. Levine JH et al. Data-Driven Phenotypic Dissection of AML Reveals Progenitor-like Cells that Correlate with Prognosis. Cell. 2015 Jul 2;162(1):184-97. doi: 10.1016/j.cell.2015.05.047.

I generated 10 samples, with half of those samples being tampored with to reduce the amount of naive T cells by 75%, this was to simulate an increase in T cells from a pre-treatment to post-treatment condition.  These samples are saved in `cio_mass_cyometry/data` and should be included with the python package.  This folder also contains a fully-completed metadata example suitable for ingesting and running the pipeline, and a fully-labled clustering spreadsheet example, suitable for running out final stages of the pipeline.

This gives us a simulated cohort with:

1. A 13 marker panel
2. 10 samples
3. 5 patients
4. Pre/Post timepoints
5. An expected increase in naive CD8+ T cells

## Following the example

Jupyter notebooks saved in `notebooks/` contain all the steps to work through a CyTOF project in your working directory.  I'll describe and link each step in the analysis here:

### [notebooks/00 - Python - Stage example data.ipynb](https://github.com/jason-weirather/cio-mass-cytometry/blob/main/notebooks/00%20-%20Python%20-%20Stage%20example%20data.ipynb)

This non-step will copy the FCS files to a `data/` file in your local environment, set up the `WORKFLOW/` directory where files used and created will reside, and the `scripts/` directory where the R script used for ingesting the project metadata resides.

## Stage 1 (To run CATALYST and get unlabeled clusters)

### [notebooks/01 - R - Get Panel details.ipynb](https://github.com/jason-weirather/cio-mass-cytometry/blob/main/notebooks/01%20-%20R%20-%20Get%20Panel%20details.ipynb)

This will get information about the panel run out of the FCS file and ensure that panel details are consistent across FCS files, this will be used to fill in the metadata accurately.

### [notebooks/02 - Python - Create metadata template.ipynb](https://github.com/jason-weirather/cio-mass-cytometry/blob/main/notebooks/02%20-%20Python%20-%20Create%20metadata%20template.ipynb)

We use a python CLI created here to generate a new blank metadata template sheet, and then add on the sample names and file paths programatically.  

### [notebooks/03 - Python - Ingest the filled-in metadata.ipynb](https://github.com/jason-weirather/cio-mass-cytometry/blob/main/notebooks/03%20-%20Python%20-%20Ingest%20the%20filled-in%20metadata.ipynb)

Take the completed metadata spreadsheet and ingest it making a validated json format of all the input data.

### [notebooks/04 - R - Run CATALYST stage 1.ipynb](https://github.com/jason-weirather/cio-mass-cytometry/blob/main/notebooks/04%20-%20R%20-%20Run%20CATALYST%20stage%201.ipynb)

Use the metadata json you created to run CATALYST for the first stage of the pipeline and over-clustering.

### [notebooks/05 - Python - Generate cluster template.ipynb](https://github.com/jason-weirather/cio-mass-cytometry/blob/main/notebooks/05%20-%20Python%20-%20Generate%20cluster%20template.ipynb)

Take the CATALYST outputs and produce a worksheet of unlabled clusters and generating figures.

## Stage 2 (To run CATALYST and with labeled clusters)

### [notebooks/06 - Python - Ingest labeled clusters.ipynb](https://github.com/jason-weirather/cio-mass-cytometry/blob/main/notebooks/06%20-%20Python%20-%20Ingest%20labeled%20clusters.ipynb)

Ingest the Excel spreadsheet with cluster labels and save it as a json.

### [notebooks/07 - R - Run CATALYST stage 2.ipynb](https://github.com/jason-weirather/cio-mass-cytometry/blob/main/notebooks/07%20-%20R%20-%20Run%20CATALYST%20stage%202.ipynb)

Use the cluster label json and the previous run of CATALYST to run the rest of the CATALYST pipeline, now with known cell labels generating figures.

### [notebooks/08 - Python - Output data.ipynb](https://github.com/jason-weirather/cio-mass-cytometry/blob/main/notebooks/08%20-%20Python%20-%20Output%20data.ipynb)

Save primary per-cell data and cell-type frequency, cell-type expression, and pseudobulk expression data out.

# CLI description

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
