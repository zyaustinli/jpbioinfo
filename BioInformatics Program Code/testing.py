from cmath import nan
from operator import length_hint
from sys import builtin_module_names
import pandas as pd
import csv
import numpy as np
import re
df = pd.read_csv('data.csv') 
df_template = pd.read_csv('template.csv')
df.columns = df.columns.str.replace(' ','_')
df.columns = df.columns.str.replace('/','_')
df.columns = df.columns.str.replace('?','_')

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None


#if contain mouse, replace with \ADME In Vivo\Bioanalysis\Mouse, if contain rat, replace with \ADME In Vivo\Bioanalysis\Rat

df.loc[df['Request_Type'].str.contains('Mouse').fillna(False), 'Request_Type'] = '\ADME In Vivo\Bioanalysis\Mouse'
df.loc[df['Request_Type'].str.contains('R').fillna(False), 'Request_Type'] = '\ADME In Vivo\Bioanalysis\Rat'

#if request type is rat, sprague dawley strain

for i in range(len(df)):
    if df.iat[i, 9] == '\ADME In Vivo\Bioanalysis\Rat':
        df['Strain'] = df['Strain'].replace(df.iat[i, 12], 'Sprague Dawley')


#strain = Sprague Dawley, C57BL/6, CF-1, NMR1, C57BL, DBA1/LacJ, Wistar, Human, MDR-, PGP KO, Cynomolgus, Beagle, RAG -/-


df.loc[df['Strain'].str.contains('C5').fillna(False), 'Strain'] = 'C57BI/6'
df.loc[df['Strain'].str.contains('CS').fillna(False), 'Strain'] = 'C57BI/6'
df.loc[df['Strain'].str.contains('Cc').fillna(False), 'Strain'] = 'C57BI/6'

df.loc[df['Type_of_Study'].str.contains('Dose').fillna(False), 'Type_of_Study'] = 'Dose Linearity'
df.loc[df['Type_of_Study'].str.contains('PKIPD').fillna(False), 'Type_of_Study'] = 'PK/PD'


    
file = df['File'].tolist()

for i in range(len(file)):
    split = re.split("-|_", str(file[i]))
    ID = split[1]
    df.loc[i, 'Request_ID'] = ID
    #replace ID from file to column

df['J&J_Salt'].str.replace("t", "")
#J_J_Salt only AAA or AAC or AFP







df['Submitter'] = df['Submitter'].str.replace('[^\w\s]', '')
df['Anti-coagulant'] = df['Anti-coagulant'].str.replace('[^\w\s]', '')
df['Regimen'] = "Non-Fasted"

df['J&J_Batch_ID'].astype(str).str.replace("S", "5")
df['J&J_Batch_ID'].astype(str).str.replace("O", "0")
df['J&J_Batch_ID'].astype(str).str.replace("s", "5")
df['J&J_Batch_ID'].astype(str).str.replace("o", "5")
df['J&J_Batch_ID'].astype(str).str.replace("$", "5")
df['J&J_Batch_ID'].astype(str).str.replace(r'\D+', "")

df['J&J_Salt'].astype(str).str.replace("S", "5")
df['J&J_Salt'].astype(str).str.replace("O", "0")
df['J&J_Salt'].astype(str).str.replace("s", "5")
df['J&J_Salt'].astype(str).str.replace("o", "5")
df['J&J_Salt'].astype(str).str.replace("$", "5")


JJ_Salt = df['J&J_Salt'].tolist()

for i in range(len(df)):
    split = re.split("-", str(JJ_Salt[i]))
    num = split[0]
    if df.iat[i, 7] == 1:
        df.loc[i, 'J&J_Salt'] = num + "-AAA"
#if CS = 1, JJ Salt end with AAA

df.drop_duplicates


df.to_csv("datafinal1.csv")

print(df)



#if only one cell is empty for dose concentrate stuff it is possible to actually get the data by calculations!!!! but its possible it will not always be correct?
#can use variable to see if only one cell is empty (x =0, if one column is NaN, x+1, if two are empty, x+1 again. If x<=1, it shld work)
#molecular forumla S for 5? idk