import requests
import pandas as pd
import numpy as np
from os import path
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import label_binarize
from sklearn.preprocessing import StandardScaler

# Suppressing warnings on dataframe overwrites
pd.options.mode.chained_assignment = None

# Defining function to extract data from fishbase
def extract_fishbase(table):

    tablename = "https://fishbase.ropensci.org/" + table
    query = requests.get(tablename + "?limit=5000")
    n_obs = query.json()['count']
    df = pd.DataFrame(query.json()['data'])

    while(df.shape[0] < n_obs):
        query = requests.get(tablename + "?limit=5000&offset=" + str(df.shape[0]))
        tempdf = pd.DataFrame(query.json()['data'])
        df = df.append(tempdf)

    print("Table '%s' - Returned %s rows of %s features" % (table, df.shape[0], df.shape[1]))
    return(df)


# All available species
taxaTable = extract_fishbase("taxa")

# General species characteristics
speciesTable = extract_fishbase("species")

# Species ecology (habitat type, prey, etc.)
ecologyTable = extract_fishbase("ecology")

# Ecosystem characteristics
ecosystemTable = extract_fishbase("ecosystem")

# Maturity / reproduction
reproTable = extract_fishbase("maturity")


# Aggregating ecosystem table
ecosys_cols = ["Speccode", "Salinity", "Area", "SizeRef", "Climate", "AverageDepth", "MaxDepth", "TempSurface", "TempDepth"]

# Meaningful predictors
ecosys_subset = ecosystemTable[ecosys_cols]

# Aggregating across populations to get mean depth, surface temp, and depth at temperature
area_agg = ecosys_subset.groupby("Speccode")["Area"].sum()
ecosys_subset[["AverageDepth", "TempSurface", "TempDepth"]] = ecosys_subset[["AverageDepth", "TempSurface", "TempDepth"]].apply(pd.to_numeric, errors='coerce')
ATT_agg = ecosys_subset.groupby("Speccode")["AverageDepth", "TempSurface", "TempDepth"].mean()

# Convert climate to one-hot variables and aggregating for each species
ecosys_subset["Climate"] = ecosys_subset["Climate"].str.lower().fillna("None")
climate_onehot = label_binarize(ecosys_subset["Climate"], classes = ecosys_subset["Climate"].unique()[0:5])
climate_agg =  pd.DataFrame(climate_onehot, columns=ecosys_subset["Climate"].unique()[[0,1,2,3,4]])

 # Converting salinity to one-hot variables and aggregating by each variable
ecosys_subset['Salinity'] = ecosys_subset['Salinity'].str.lower().fillna("None")
salinity_onehot = label_binarize(ecosys_subset['Salinity'], classes = ecosys_subset['Salinity'].unique()[0:3])
salinity_agg =  pd.DataFrame(salinity_onehot, columns=ecosys_subset['Salinity'].unique()[0:3])

# Establishing a 1/0 dataset for each of the categorical variables, wherein each climate or salinity where a species is present is given a 1
cat_full = pd.DataFrame(ecosys_subset["Speccode"]).join([salinity_agg, climate_agg]).groupby('Speccode').sum()
cat_full = (cat_full > 1) * 1

ecosys_full = cat_full.join([area_agg, ATT_agg])
ecosys_full.reset_index(inplace = True)

# Subsetting and aggregating other tables

# Columns for the taxonomy dataset
taxa_cols = ["SpecCode", "Genus", "Species", "Family", "Order", "Class"]
taxa_subset = taxaTable[taxa_cols].set_index("SpecCode")

# Columns for the species dataset
spec_cols = ["SpecCode", "Vulnerability", "Length", "Weight", "Importance", "UsedforAquaculture",
             "UsedasBait", "Aquarium", "GameFish", "Dangerous"]

# Columns for the reproduction dataset
reproTable.rename(columns={"Speccode": "SpecCode"}, inplace = True)
repro_cols = ["SpecCode", "AgeMatMin", "AgeMatMin2", "LengthMatMin", "LengthMatMin2"]
repro_subset = reproTable[repro_cols].set_index("SpecCode")

# Standardizing length and age characteristics
repro_subset = repro_subset.groupby("SpecCode").mean()
AgeMin = repro_subset[["AgeMatMin","AgeMatMin2"]].min(axis = 1)
LengthMin = repro_subset[["LengthMatMin","LengthMatMin2"]].min(axis = 1)
repro_subset = pd.concat([pd.Series(AgeMin), pd.Series(LengthMin)],axis = 1)
repro_subset.columns = ["Age_Maturity", "Length_Maturity"]

# Columns for the ecology dataset
eco_cols = ["SpecCode","Neritic", "SupraLittoralZone", "Saltmarshes", "LittoralZone", "TidePools", "Intertidal", "SubLittoral",
"Caves", "Oceanic","Epipelagic", "Mesopelagic", "Bathypelagic", "Abyssopelagic", "Hadopelagic", "Estuaries", "Mangroves",
"MarshesSwamps", "CaveAnchialine", "Stream", "Lakes","Cave",'DietTLu']

# Binaries are coded as -1,0 in this data - converting to 1,0
eco_subset = ecologyTable[eco_cols].set_index("SpecCode")
eco_subset[eco_cols[1:-1]] = (eco_subset[eco_cols[1:-1]] == -1) * 1
eco_subset = eco_subset.groupby("SpecCode").sum()

spec_subset = speciesTable[spec_cols]
spec_subset["GameFish"] = (speciesTable["GameFish"] == -1) * 1

# Binarizing labels
spec_bin = pd.concat(
    [pd.get_dummies(spec_subset["Importance"], prefix='Imp'),
     pd.get_dummies(spec_subset["Aquarium"], prefix='Aquarium'),
     pd.get_dummies(spec_subset["UsedforAquaculture"], prefix='Aquaculture'),
     pd.get_dummies(spec_subset["UsedasBait"], prefix='Bait').iloc[:,1:],
     pd.get_dummies(spec_subset["Dangerous"], prefix='Danger')],
    axis = 1)

spec_subset = pd.concat([spec_subset.drop(columns = ["Importance", "Aquarium", "UsedforAquaculture", "UsedasBait", "Dangerous"]),
           spec_bin],
          axis = 1).set_index("SpecCode")

# Joining into a full tables
features = taxa_subset.join([spec_subset, eco_subset, repro_subset, ecosys_full])
features.to_csv("../data/fishbase_features.csv")
