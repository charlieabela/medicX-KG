import pandas as pd
import re

def cleanActiveIngredient(active_ingred):
    active_ingred = active_ingred.lower().replace(', hydrated', '')
    active_ingred = active_ingred.lower().replace(', heavy', '')
    active_ingred = active_ingred.lower().replace(', light', '')
    if 'milligram(s)' in active_ingred:
        active_ingred = active_ingred.lower().replace(' milligram(s)/', '')
        active_ingred = active_ingred.lower().replace(' milligram(s)', '')
    if 'microgram(s)/millilitre' in active_ingred:
        active_ingred = active_ingred.lower().replace(' microgram(s)/millilitre', '')
    if 'millimole(s)/millilitre' in active_ingred:
        active_ingred = active_ingred.lower().replace(' millimole(s)/millilitre', '')
    if 'millilitre(s)/' in active_ingred:
        active_ingred = active_ingred.lower().replace(' millilitre(s)/', '')
    if 'millilitre' in active_ingred:
        active_ingred = active_ingred.lower().replace(' millilitre', '')
    if 'micrograms(s)' in active_ingred:
        active_ingred = active_ingred.lower().replace(' micrograms(s)', '')
    if 'microgram(s)' in active_ingred:
        active_ingred = active_ingred.lower().replace(' microgram(s)', '')
    if 'gram(s)' in active_ingred:
        active_ingred = active_ingred.lower().replace(' gram(s)', '')
    if 'gigabecquerel(s)' in active_ingred:
        active_ingred = active_ingred.lower().replace(' gigabecquerel(s)', '')
    if 'international unit(s)' in active_ingred:
        active_ingred = active_ingred.lower().replace(' international unit(s)', '')
    if 'percent weight/volume' in active_ingred:
        active_ingred = active_ingred.lower().replace(' percent weight/volume', '')
    if 'percent weight/weight' in active_ingred:
        active_ingred = active_ingred.lower().replace(' percent weight/weight', '')
    if 'unit(s)/dose' in active_ingred:
        active_ingred = active_ingred.lower().replace(' unit(s)/dose', '')

    if active_ingred.endswith('\n'):
        active_ingred = active_ingred.lower().replace('\n', '')
    if active_ingred.endswith('('):
        active_ingred = active_ingred.lower().rstrip(' (')
    if active_ingred.endswith('['):
        active_ingred = active_ingred.lower().rstrip(' [')
    if active_ingred.endswith('>'):
        active_ingred = active_ingred.lower().rstrip(' >')
    if active_ingred.endswith('<'):
        active_ingred = active_ingred.lower().rstrip(' <')
    if active_ingred.endswith(' '):
        active_ingred = active_ingred.lower().rstrip(' ')

    return active_ingred

def getSelectedDrugNamesFromExcel():
        df = pd.read_excel('../MedicinesAuthority/AdvancedSearchResultsLocal_sample.xls')
        columns = ['Product', 'ActiveIngredient', 'PharmaceuticalForm', 'TherapeuticClass', 'Classification', 'ATC',
                   'Status', 'AuthorisationNumber', 'AuthorisationDate', 'AuthorisationHolder',
                   'AuthorisationHolderAddress', 'MAHContact1', 'MAHContact2', 'LicenceNumber']
        df.columns = columns
        df[columns] = df[columns].apply(lambda x: x.str.strip(' '))
        df[columns] = df[columns].apply(lambda x: x.str.strip('\''))
        df[columns] = df[columns].apply(lambda x: x.str.strip(' '))

        active_ingreds = []
        active_ingred = []

        for index, row in df.iterrows():
            ingreds_per_row = []
            active_ingreds_col = row['ActiveIngredient']
            ingreds = active_ingreds_col.split('|')
            if len(ingreds) > 1:
                print('Multiple Ingredients: ' + row)
            for ingred in ingreds:
                m = re.search(r"\d", ingred)
                if m is not None:
                    ingreds_per_row.append(ingred[: m.start()].strip(' '))
                    active_ingreds.append(cleanActiveIngredient(ingred[: m.start()].strip(' ')))
                else:
                    print('No digit: ' + row)
                    ingreds_per_row.append(ingred.strip())
                    active_ingreds.append(cleanActiveIngredient(ingred.strip()))
            active_ingred.append(
                [active_ingreds_col, ingreds_per_row, row['Product'], row['TherapeuticClass'], row['ATC'],
                 row['PharmaceuticalForm'], row['Status']])

        # print(active_ingred)
        df = pd.DataFrame(active_ingred, columns=['ActiveIngredients', 'List', 'Product', 'TherapeuticClass', 'ATC',
                                                  'PharmaceuticalForm', 'Status'])
        df.to_csv('active_ingredients_separated_sample.csv')

        flat_list = []
        for sublist in active_ingred:
            for item in sublist[1]:
                flat_list.append(item)

        # print(len(flat_list))
        # flat_list = list(set(flat_list))
        # print(len(flat_list))

        return active_ingreds


def findProductsInOriginalExcel(activeIngredients):
    df = pd.read_excel('../MedicinesAuthority/AdvancedSearchResultsLocal_august.xls')
    columns = ['Product', 'ActiveIngredient', 'PharmaceuticalForm', 'TherapeuticClass', 'Classification', 'ATC',
               'Status', 'AuthorisationNumber', 'AuthorisationDate', 'AuthorisationHolder',
               'AuthorisationHolderAddress', 'MAHContact1', 'MAHContact2', 'LicenceNumber']
    df.columns = columns
    df[columns] = df[columns].apply(lambda x: x.str.strip(' '))
    df[columns] = df[columns].apply(lambda x: x.str.strip('\''))
    df[columns] = df[columns].apply(lambda x: x.str.strip(' '))

    products_list = []

    for index, row in df.iterrows():
        sampledActiveIngredientFound = False
        ingreds_per_row = []
        active_ingreds_col = row['ActiveIngredient']
        ingreds = active_ingreds_col.split('|')
        if len(ingreds) > 1:
            print('Multiple Ingredients: ' + row)
        for ingred in ingreds:
            m = re.search(r"\d", ingred)
            if m is not None:
                activeIngredient = ingred[: m.start()].strip(' ')
                activeIngredient = cleanActiveIngredient(activeIngredient)
                ingreds_per_row.append(activeIngredient)
            else:
                print('No digit: ' + row)
                activeIngredient = ingred.strip()
                activeIngredient = cleanActiveIngredient(activeIngredient)
                ingreds_per_row.append(ingred.strip())
            if activeIngredient in activeIngredients:
                sampledActiveIngredientFound = True

        if sampledActiveIngredientFound:
            products_list.append(
                [active_ingreds_col, ingreds_per_row, row['Product'], row['TherapeuticClass'], row['ATC'],
                 row['PharmaceuticalForm'], row['Status']])

    sampledProducts_df = pd.DataFrame(products_list, columns=['ActiveIngredients', 'List', 'Product', 'TherapeuticClass', 'ATC',
                                              'PharmaceuticalForm', 'Status'])

    return products_list, sampledProducts_df


def retrieveSampledProducts():
    # retrieve the drug names from AdvancedSearchResultsLocal_sample
    sampledActiveIngredients = getSelectedDrugNamesFromExcel()
    print('Sampled active ingredients: ' + str(len(sampledActiveIngredients)))
    # find all the products that contain these drugs in AdvancedSearchResultsLocal_august
    products_list, sampledProducts_df = findProductsInOriginalExcel(sampledActiveIngredients)
    # save these products in a separate file
    sampledProducts_df.to_csv('sampledProducts.csv')

    return products_list