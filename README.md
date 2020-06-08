# STA208-Final-Project
__Author:__ Evan Batzer 

__Date:__ 6/7/2020

## Project Overview
As biodiversity loss continues to accelerate in the 21st century, modern approaches to conservation policy emphasize the protection of species which are most likely to go extinct. Global databases, such as the IUCN Red List, are used to set prioritize efforts and funding for species conservation. However, evaluation of a species' conservation status on the IUCN Red List is a time-intensive process that requires input from a team of experts.

In this project, I use existing data on species characteristics from a global database, Fishbase, to classify species based on their IUCN categorization. In doing so, I aim to establish how well IUCN categories can be predicted by the ecological characteristics of fish species without detailed knowledge of their current and projected population trends.

## Contents and Organization
_images:_ Image files used in notebooks and presentations

_code:_ .py files that contain scripts to extract and pre-process remote datasets available from Fishbase and other online sources. When run, will generate files in the `/data/` directory for use in analysis

_presentation:_ Jupyter notebook and associated files used to generate React.js slides for in-class presentation on 6/2/2020

_data:_ Datasets used in analysis, containing both raw datafiles and intermediate data products during data processing and feature engineering

_notebooks:_ Jupyter notebooks documenting analysis
1. DataProcessing - Cleaning and aggregating datasets, exploratory data analysis, missing data imputation
2. BinaryClassification - Classification of species conservation categories as a binary task ('Least Concern' vs others) using gradient boosted classification methods (XGBoost)
3. OrdinalClassification - Classification of species conservation status as an ordinal task using custom modeling framework
