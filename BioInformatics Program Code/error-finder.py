from sys import builtin_module_names
import pandas as pd
import csv
import numpy as np
df = pd.read_csv('datatest.csv') 
df_template = pd.read_csv('template.csv')
df.columns = df.columns.str.replace(' ','_')
df.columns = df.columns.str.replace('/','_')
df.columns = df.columns.str.replace('?','_')
df.columns = df.columns.str.replace('&','_')
df_template.columns = df_template.columns.str.replace(' ','_')
df_template.columns = df_template.columns.str.replace('/','_')
df['Project'] = df['Project'].str.replace('$', 'dollar_sign', regex = True)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None


df1 = df[~df['Request_ID'].apply(lambda x: str(x).isdigit())] #only #s

df2 = df[~df['Request_Set_ID'].apply(lambda x: str(x).isdigit())] #only #s

df3 = df[~df['J_J_Batch_ID'].apply(lambda x: str(x).isdigit())] #only #s

df4 = (df[df.Project.str.contains('dollar_sign')]) #there are TONS of errors in "Project"

df4['Project'] = df4['Project'].str.replace('dollar_sign', '$', regex = True)

df5= (df[df.Request_Type.str.contains('lB')]) #misread slashes

#df6 = (df[~df.Strain.str.contains('Sprague Dawley') & ~df.Strain.str.contains('/')]) #strains check (assume Sprague Dawley is only exception (may need to change later))

df7 = (df[df.Dose_volume_ml_kg.astype(str).str.contains('jesus', na = True) | df.Dose_volume_ml_kg.astype(str).str.contains('O', na = False)]) #only numbers/empty spaces

df8 = df[~df['Number_of_animals'].apply(lambda x: str(x).isdigit())] #only nums

df9 = (df[~df.Route_of_admin.str.contains('PO', na=False) & ~df.Route_of_admin.str.contains('SC', na=False) & ~df.Route_of_admin.str.contains('Po', na=False) & ~df.Route_of_admin.str.contains('pO', na=False) & ~df.Route_of_admin.str.contains('Sc', na=False) & ~df.Route_of_admin.str.contains('sC', na=False)])
#if not contain po or sc

df10 = df['Timepoints'].astype(str).str.contains('jesus', na = True) #empty

df11 = df_template
with open('datatest.csv') as f:
    molecular_weight = [line.split(',')[11] for line in f]
with open('datatest.csv') as f:
    molecular_weight_batch = [line.split(',')[12] for line in f]
pd.to_numeric(molecular_weight_batch[1:], downcast ='integer')
pd.to_numeric(molecular_weight[1:],  downcast ='integer')
range_low = [x-2.5 for x in pd.to_numeric(molecular_weight[1:], downcast ='integer')]
range_high = [x+2.5 for x in pd.to_numeric(molecular_weight[1:], downcast ='integer')]
for i in range(0, len(df)):
    if range_low[i] >= pd.to_numeric(molecular_weight_batch[i+1]):
        df11.loc[df.index[i]] = df.iloc[i]
    elif range_high[i] <= pd.to_numeric(molecular_weight_batch[i+1]):
        df11.loc[df.index[i]] = df.iloc[i]
#if molecular weight and batch are close

df12 = (df[~df['Dose_group'].apply(lambda x: str(x).isdigit()) | df.Dose_group.str.contains('O') | df.Dose_group.str.contains('S') | df.Dose_group.str.contains('o') | df.Dose_group.str.contains('s')])
#only nums

df13 = (df[~df.Sex.str.contains('Male') & ~df.Sex.str.contains('Female')]) #only male/female

df14 = (df[~df.Is_this_a_Prodrug_.str.contains('Yes', na=False) & ~df.Is_this_a_Prodrug_.str.contains('No',na=False)]) #only yes/no

df15 = (df[~df.Does_this_compound_have_a_carboxylic_acid_group_.str.contains('Yes', na=False) & ~df.Does_this_compound_have_a_carboxylic_acid_group_.str.contains('No', na=False)]) #only yes/no

df16 = df_template
df_16_1 = pd.to_numeric(df['Dose_mg_kg'], errors='coerce').notna()
df_16_2 = pd.to_numeric(df['Dose_volume_ml_kg'], errors='coerce').notna()
df_16_3 = pd.to_numeric(df['Dosing_solution_concentration_mg_ml'], errors='coerce').notna()

for i in range(0,len(df)):
    if df_16_1[i] == df_16_2[i] == df_16_3[i]:
        if (int(float(df.iat[i,22])) // int(float(df.iat[i,23]))) != int(df.iat[i,24]):
            df16 = df16.append(df.iloc[i])
#division dose / dose volume = concentrate

df17 = df_template
for i in range(0,len(df)):
    if df_16_1[i] == False:
        df17 = df17.append(df.iloc[i])
#dose mg/kg NaN

df_18_1 = df['File'].tolist()
df_18_2 = df['Request_ID'].tolist()
df18 = df_template
for i in range(0, len(df)):
    if str(df_18_2[i]) not in str(df_18_1[i]):
        df18 = df18.append(df.iloc[i])
#request ID in file name


def main():
    df1.to_csv('Request_ID_check.csv')
    print("There are no program found issues in Request ID: " + str(df1.empty))
    df2.to_csv('Request_Set_ID_check.csv')
    print("There are no program found issues in Request Set ID: " + str(df2.empty))
    df3.to_csv('J&J_Batch_ID_check.csv')
    print("There are no program found issues in J&J Batch ID: " + str(df3.empty))
    df4.to_csv('Project_check.csv')
    print("There are no program found issues in Project: " + str(df4.empty))
    df5.to_csv('Request_Type_check.csv')
    print("There are no program found issues in Request Type: " + str(df5.empty))
    #df6.to_csv('Strain_check.csv')
    print("There are no program found issues in Strain: " + str(df6.empty))
    df7.to_csv('Dose_volume_ml_kg_check.csv')
    print("There are no program found issues in Dose Volume ml/kg: " + str(df7.empty))
    df8.to_csv('Number_of_animals_check.csv')
    print("There are no program found issues in Number of animals: " + str(df8.empty))
    df9.to_csv('Route_of_admin_check.csv')
    print("There are no program found issues in Route of admin: " + str(df9.empty))
    df10.to_csv('Timepoints_check.csv')
    print("There are no program found issues in Timepoints: " + str(df10.empty))
    df11.to_csv('Molecular_Weight_Discrepancy.csv')
    print("There are no program found issues in Molecular weight discrepancy: " + str(df11.empty))
    df12.to_csv('Dose_group_check.csv')
    print("There are no program found issues in Dose group: " + str(df12.empty))
    df13.to_csv('Sex_check.csv')
    print("There are no program found issues in Sex: " + str(df13.empty))
    df14.to_csv('Prodrug.csv')
    print("There are no program found issues in Prodrug(Y/N): " + str(df14.empty))
    df15.to_csv('Carboxylic_acid.csv')
    print("There are no program found issues in Carboxylic acid group(Y/N): " + str(df15.empty))
    df16.to_csv('Dosing_solution_concentration_check.csv')
    print("There are no program found issues in Dosing solution concentration by division(Y/N): " + str(df16.empty))
    df17.to_csv("Dose_mg_kg.csv")
    print("There are no program found issues in Dose mg/kg(Y/N): " + str(df17.empty))
    df18.to_csv("ID_in_File.csv")
    if len(df_18_1) != len(df_18_2):
        print("Request ID and File are not equal in size")
    else:
        print("There are no program found issues in Request and File(Y/N): " + str(df18.empty))

def missing_nan():
    df_edit = df.drop(['Molecular_Formula', 'Comments', 'Any_expected_side_effects_and_safety_data_', 'Overall_Comments'], axis=1)

    df_File = df_edit[df_edit['File'].isnull()]
    print("No missing data in Files: " + str(df_File.empty))
    if df_File.empty == False:
        df_File.to_csv("File_missing.csv")

    df_Request_ID = df_edit[df_edit['Request_ID'].isnull()]
    print("No missing data in Request ID: " + str(df_Request_ID.empty))
    if df_Request_ID.empty == False:
        df_Request_ID.to_csv("Request_ID_missing.csv")

    df_Request_Set_ID = df_edit[df_edit['Request_Set_ID'].isnull()]
    print("No missing data in Request Set ID: " + str(df_Request_Set_ID.empty))
    if df_Request_Set_ID.empty == False:
        df_Request_Set_ID.to_csv("Request_Set_ID_missing.csv")

    df_J_J_Batch_ID = df_edit[df_edit['J_J_Batch_ID'].isnull()]
    print("No missing data in J_J_Batch_ID: " + str(df_J_J_Batch_ID.empty))
    if df_J_J_Batch_ID.empty == False:
        df_J_J_Batch_ID.to_csv("J_J_Batch_ID_missing.csv")

    df_J_J_Salt = df_edit[df_edit['J_J_Salt'].isnull()]
    print("No missing data in J_J_Salt: " + str(df_J_J_Salt.empty))
    if df_J_J_Salt.empty == False:
        df_J_J_Salt.to_csv("J_J_Salt_missing.csv")

    df_Submitter = df_edit[df_edit['Submitter'].isnull()]
    print("No missing data in Submitter: " + str(df_Submitter.empty))
    if df_Submitter.empty == False:
        df_Submitter.to_csv("Submitter_missing.csv")

    df_CS = df_edit[df_edit['CS'].isnull()]
    print("No missing data in CS: " + str(df_CS.empty))
    if df_CS.empty == False:
        df_CS.to_csv("CS.csv")

    df_Project = df_edit[df_edit['Project'].isnull()]
    print("No missing data in Project: " + str(df_Project.empty))
    if df_Project.empty == False:
        df_Project.to_csv("Project.csv")

    df_Request_Type = df_edit[df_edit['Request_Type'].isnull()]
    print("No missing data in Request Type: " + str(df_Request_Type.empty))
    if df_Request_Type.empty == False:
        df_Request_Type.to_csv("Request_Type.csv")

    df_Molecular_Weight = df_edit[df_edit['Molecular_Weight'].isnull()]
    print("No missing data in Molecular Weight: " + str(df_Molecular_Weight.empty))
    if df_Molecular_Weight.empty == False:
        df_Molecular_Weight.to_csv("Molecular_Weight.csv")
        
    df_Batch_Molecular_Weight = df_edit[df_edit['Batch_Molecular_Weight'].isnull()]
    print("No missing data in Batch_Molecular_Weight: " + str(df_Batch_Molecular_Weight.empty))
    if df_Batch_Molecular_Weight.empty == False:
        df_Batch_Molecular_Weight.to_csv("Batch_Molecular_Weight.csv")

    df_Type_of_Study = df_edit[df_edit['Type_of_Study'].isnull()]
    print("No missing data in Type_of_Study: " + str(df_Type_of_Study.empty))
    if df_Type_of_Study.empty == False:
        df_Type_of_Study.to_csv("Type_of_Study.csv")

    df_Sex = df_edit[df_edit['Sex'].isnull()]
    print("No missing data in Sex: " + str(df_Sex.empty))
    if df_Sex.empty == False:
        df_Sex.to_csv("Sex.csv")

    df_Strain = df_edit[df_edit['Strain'].isnull()]
    print("No missing data in Strain: " + str(df_Strain.empty))
    if df_Strain.empty == False:
        df_Strain.to_csv("Strain.csv")

    df_Anti_coagulant = df_edit[df_edit['Anti-coagulant'].isnull()]
    print("No missing data in Anti-coagulant: " + str(df_Anti_coagulant.empty))
    if df_Anti_coagulant.empty == False:
        df_Anti_coagulant.to_csv("Anti_coagulant.csv")

    df_Dose_mg_kg = df_edit[df_edit['Dose_mg_kg'].isnull()]
    print("No missing data in Dose mg/kg: " + str(df_Dose_mg_kg.empty))
    if df_Dose_mg_kg.empty == False:
        df_Dose_mg_kg.to_csv("Dose_mg_kg.csv")

    df_Dose_volume_ml_kg = df_edit[df_edit['Dose_volume_ml_kg'].isnull()]
    print("No missing data in Dose_volume_ml_kg: " + str(df_Dose_volume_ml_kg.empty))
    if df_Dose_volume_ml_kg.empty == False:
        df_Dose_volume_ml_kg.to_csv("Dose_volume_ml_kg.csv")

    df_Dosing_solution_concentration_mg_ml = df_edit[df_edit['Dosing_solution_concentration_mg_ml'].isnull()]
    print("No missing data in Dosing_solution_concentration_mg_ml: " + str(df_Dosing_solution_concentration_mg_ml.empty))
    if df_Dosing_solution_concentration_mg_ml.empty == False:
        df_Dosing_solution_concentration_mg_ml.to_csv("Dosing_solution_concentration_mg_ml.csv")

    df_Timepoints = df_edit[df_edit['Timepoints'].isnull()]
    print("No missing data in Timepoints: " + str(df_Timepoints.empty))
    if df_Timepoints.empty == False:
        df_Timepoints.to_csv("Timepoints.csv")

    df_Matrix = df_edit[df_edit['Matrix'].isnull()]
    print("No missing data in Matrix: " + str(df_Matrix.empty))
    if df_Matrix.empty == False:
        df_Matrix.to_csv("Matrix.csv")
        
    df_Formulations = df_edit[df_edit['Formulations'].isnull()]
    print("No missing data in Formulations: " + str(df_Formulations.empty))
    if df_Formulations.empty == False:
        df_Formulations.to_csv("Formulations.csv")
   
main()
missing_nan()




#strain = Sprague Dawley, C57BL/6, CF-1, NMR1, C57BL, DBA1/LacJ, Wistar, Human, MDR-, PGP KO, Cynomolgus, Beagle, RAG -/-
