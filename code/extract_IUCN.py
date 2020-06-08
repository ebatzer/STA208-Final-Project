import pandas as pd
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

urlretrieve('https://drive.google.com/u/0/uc?id=0B9_zEbZIPqtIVXJ1VVpEMGNxdnc&export=download',
'../data/IUCN_full.csv')

# Reading in dataset -- correcting some encoding errors
IUCN_labels = pd.read_csv('../data/IUCN_full.csv', encoding = "ISO-8859-1", engine='python')

# Subsetting to meaningful columns
IUCN_labels = IUCN_labels[["Class", 'Order', 'Family', 'Genus', 'Species', 'Red List status']]

# Extracting revelant fish species (by family / order / class)
IUCN_labels[["Class", 'Order', 'Family']] = IUCN_labels[["Class", 'Order', 'Family']].apply(lambda x: x.astype(str).str.capitalize())
fish_classes = ['Actinopterygii', 'Chondrichthyes','Sarcopterygii','Cephalaspidomorphi']
IUCN_subset = IUCN_labels.loc[IUCN_labels['Class'].isin(fish_classes)]

# Writing to new dataframe
IUCN_subset.to_csv("../data/IUCN_subset.csv")
