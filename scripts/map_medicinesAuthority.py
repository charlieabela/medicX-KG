import pandas as pd
import re
import json
import os

from rdflib import ConjunctiveGraph, Namespace, URIRef, Literal, Graph
from rdflib.namespace import RDF, RDFS, OWL
import urllib.parse
import sys
sys.path.insert(0, 'C:/Users/lfarrugia/Downloads/MDIA-20230729T125751Z-001/MDIA/Multi-Classifier')
import MappingHelperMethods
# import CreateMedicXNodes

graph = ConjunctiveGraph()
ontology = Namespace('http://medicX.org/')

bioPortalOntology = Namespace('http://purl.bioontology.org/ontology/ATC/')
bioPortalGraph = Graph()
bioPortalGraph.parse('ATC.ttl', format='ttl')

# Define classes
Product = ontology.Product
ActiveIngredient = ontology.ActiveIngredient
Compound = ontology.Compound
MarketingAuthorisation = ontology.MarketingAuthorisation
Contraindication = ontology.Contraindication
ATCCode = ontology.ATCCode
ADR = ontology.ADR
Indication = ontology.Indication
TherapeuticClass = ontology.TherapeuticClass
Storage = ontology.Storage
Excipient = ontology.Excipient
MethodOfAdministration = ontology.MethodOfAdministration
DrugDrugInteraction = ontology.DrugDrugInteraction
MedicinalForm = ontology.MedicinalForm

bioPortalATC = ontology.ATC

# Define properties
name = ontology.name
label = ontology.label
medicines_authority_url = ontology.medicinesAuthorityURL
bnf_url = ontology.bnfURL
fertility = ontology.fertility
pregnancy = ontology.pregnancy
allergies = ontology.allergies
caution = ontology.caution
action = ontology.action
breastFeeding = ontology.breastFeeding
adr_further_information = ontology.adrFurtherInformation
adr_overdose = ontology.overdoseInformation
medicinalForm = ontology.medicinalForm
medicineCompany = ontology.company
medicineLegalCateogry = ontology.legalCategory
shelf_life = ontology.shelfLife
status = ontology.status
holder_name = ontology.holderName
contact_number = ontology.contactNumber
address = ontology.address
place = ontology.place
temperature = ontology.temperature
is_gluten_free = ontology.isGlutenFree
is_lactose_free = ontology.isLactoseFree
interaction_type = ontology.interactionType
interaction_severity = ontology.interactionSeverity
interaction_evidence = ontology.interactionEvidence
drugbankID = ontology.drugBankID
drugbankURL = ontology.drugbankURL
pubchemID = ontology.pubchemID
pubchemURL = ontology.pubchemURL

# TODO: make side effect links sub classes of side effect


def map(medicineAuthority):
    bnfFound = []
    bnfNotFound = []
    bnfFoundCompound = []
    bnfNotFoundCompound = []
    bnfFoundDrugBankSynonym = []
    bnfNotFoundDrugBankSynonym = []
    drugbankFound = []
    drugbankNotFound = []
    drugbankFoundCompound = []
    drugbankNotFoundCompound = []
    pubchemFound = []
    pubchemNotFound = []
    counter = 0
    active_ingred_notFound = []
    drugbankProductFound = []
    atc_dict = {}
    bnf_medicx_dict = {}

    for med in medicineAuthority:
        productName = med[2]
        pharmaceuticalForm = med[5]
        status = med[6]

        medicX_product = createProduct(productName, pharmaceuticalForm, status)

        for original_active_ingred in med[1]:
            counter = counter + 1
            active_ingred_found = False
            medicX_activeIngredient = None

            active_ingred = original_active_ingred.lower().replace(', hydrated', '')
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

            if active_ingred != '':
                print('Mapping ' + str(counter))
                medicX_activeIngredient = createActiveIngredient(active_ingred.lower())

                graph.add((medicX_product, ontology.has_active_ingredient, medicX_activeIngredient))

                # check direct bnf
                bnfActiveIngredient = MappingHelperMethods.findActiveIngredientInBNF(active_ingred.lower())
                if bnfActiveIngredient:
                    bnfFound.append(active_ingred)
                    active_ingred_found = True
                    medicX_activeIngredient = addTriplesFromBNF(medicX_activeIngredient, bnfActiveIngredient)
                    bnf_medicx_dict[bnfActiveIngredient] = medicX_activeIngredient
                else:
                    bnfNotFound.append(active_ingred)

                # check direct DrugBank
                drugbankActiveIngredient = MappingHelperMethods.findActiveIngredientInDrugBank(active_ingred.lower())
                if drugbankActiveIngredient:
                    drugbankFound.append(active_ingred)
                    active_ingred_found = True
                    medicX_activeIngredient = addTriplesFromDrugBank(medicX_activeIngredient, drugbankActiveIngredient[0])

                    if active_ingred not in atc_dict:
                        atc_dict[active_ingred] = MappingHelperMethods.scrapeATCcodeFromDrugBank(drugbankActiveIngredient[0])

                    if atc_dict[active_ingred] is not None:
                        for code in atc_dict[active_ingred]:
                            atcCode = code[1].split(' ')[0]
                            atcName = code[1].split(' ')[2]
                            medicX_atc = createATCode(atcCode, atcName)
                            graph.add((medicX_activeIngredient, ontology.has_atc, medicX_atc))

                    if not bnfActiveIngredient:
                        drugbankResults = MappingHelperMethods.extractSynonymsFromDrugBank(active_ingred.lower())
                        drugbankSynonyms = drugbankResults["synonyms"]
                        drugbankSalt = drugbankResults["salts"]

                        for syn in drugbankSynonyms:
                            bnfActiveIngredient = MappingHelperMethods.findActiveIngredientInBNF(syn.lower())
                            if bnfActiveIngredient:
                                bnfFoundDrugBankSynonym.append(active_ingred.lower())
                                medicX_activeIngredient = addTriplesFromBNF(medicX_activeIngredient, bnfActiveIngredient)
                            else:
                                bnfNotFoundDrugBankSynonym.append(active_ingred.lower())
                        # for salt in drugbankSalt:
                        #     bnfActiveIngredient = MappingHelperMethods.findActiveIngredientInBNF(salt.lower())
                        #     if bnfActiveIngredient:
                        #         bnfFoundDrugBankSynonym.append(salt.lower())
                        #     else:
                        #         bnfNotFoundDrugBankSynonym.append(salt.lower())
                else:
                    drugbankNotFound.append(active_ingred)

                # check direct PubChem
                pubchemActiveIngredient = MappingHelperMethods.findActiveIngredientInPubChem(active_ingred.lower())
                if pubchemActiveIngredient:
                    pubchemFound.append(active_ingred)
                    graph.add((medicX_activeIngredient, pubchemID, Literal(pubchemActiveIngredient[0])))
                    graph.add((medicX_activeIngredient, pubchemURL, Literal(pubchemActiveIngredient[2])))
                    active_ingred_found = True

                    compounds = MappingHelperMethods.extractCompoundsFromPubChem(active_ingred.lower())
                    if compounds:
                        for compound in compounds:
                            medicX_Compound = createCompound(compound.lower())
                            graph.add((medicX_activeIngredient, ontology.has_component_compound, medicX_Compound))
                            bnfCompound = MappingHelperMethods.findActiveIngredientInBNF(compound.lower())
                            if bnfCompound:
                                bnfFoundCompound.append(compound.lower())
                                medicX_Compound = addTriplesFromBNF(medicX_Compound, bnfCompound)
                            else:
                                bnfNotFoundCompound.append(compound.lower())
                            drugBankCompound = MappingHelperMethods.findActiveIngredientInDrugBank(compound.lower())
                            if drugBankCompound:
                                drugbankFoundCompound.append(compound.lower())
                                medicX_Compound = addTriplesFromDrugBank(medicX_Compound,
                                                                                 drugBankCompound[0])
                            else:
                                drugbankNotFoundCompound.append(compound.lower())
                else:
                    pubchemNotFound.append(active_ingred)

            # if not active_ingred_found:
            #     active_ingred_notFound.append(active_ingred.lower())
            #     # check direct product in DrugBank
            #     drugbankProduct = MappingHelperMethods.findProductInDrugBank(med[2].lower())
            #     if drugbankProduct:
            #         if len(med[2]) == 1:
            #             bnfActiveIngredient = MappingHelperMethods.findActiveIngredientInBNF(active_ingred.lower())
            #             if bnfActiveIngredient:
            #                 medicX_activeIngredient = addTriplesFromBNF(medicX_activeIngredient, bnfActiveIngredient)
            #
            #         drugbankProductFound.append(drugbankProduct)


    bnfFound = list(set(bnfFound))
    bnfNotFound = list(set(bnfNotFound))
    bnfFoundCompound = list(set(bnfFoundCompound))
    bnfNotFoundCompound = list(set(bnfNotFoundCompound))
    bnfFoundDrugBankSynonym = list(set(bnfFoundDrugBankSynonym))
    bnfNotFoundDrugBankSynonym = list(set(bnfNotFoundDrugBankSynonym))
    drugbankFound = list(set(drugbankFound))
    drugbankNotFound = list(set(drugbankNotFound))
    drugbankFoundCompound = list(set(drugbankFoundCompound))
    drugbankNotFoundCompound = list(set(drugbankNotFoundCompound))
    pubchemFound = list(set(pubchemFound))
    pubchemNotFound = list(set(pubchemNotFound))
    active_ingred_notFound = list(set(active_ingred_notFound))

    print('BNF found: ' + str(len(bnfFound)))
    print('BNF not found: ' + str(len(bnfNotFound)))
    print(bnfNotFound)
    print('For active ingredients not found in BNF: BNF Compound found: ' + str(len(bnfFoundCompound)))
    print(bnfFoundCompound)
    print('For active ingredients not found in BNF: BNF Compound not found: ' + str(len(bnfNotFoundCompound)))
    print(bnfNotFoundCompound)
    print('For active ingredients not found in BNF: BNF DrugBank Synonym found: ' + str(len(bnfFoundDrugBankSynonym)))
    print(bnfFoundDrugBankSynonym)
    print('For active ingredients not found in BNF: BNF DrugBank Synonym not found: ' + str(len(bnfNotFoundDrugBankSynonym)))
    print(bnfNotFoundDrugBankSynonym)

    print('DrugBank found: ' + str(len(drugbankFound)))
    print(drugbankFound)
    print('DrugBank not found: ' + str(len(drugbankNotFound)))
    print(drugbankNotFound)
    print('For active ingredients not found in DrugBank: DrugBank Compound found: ' + str(len(drugbankFoundCompound)))
    print(drugbankFoundCompound)
    print('For active ingredients not found in DrugBank: DrugBank Compound not found: ' + str(len(drugbankNotFoundCompound)))
    print(drugbankNotFoundCompound)

    print('PubChem found: ' + str(len(pubchemFound)))
    print(pubchemFound)
    print('PubChem not found: ' + str(len(pubchemNotFound)))
    print(pubchemNotFound)

    print('Active ingredients not found with no exact match either in DrugBank, BNF or PubChem: ' + str(len(active_ingred_notFound)))
    print(active_ingred_notFound)

    print('DrugBank Product Found: ' + str(len(drugbankProductFound)))


def parseMedicinesAuthorityExcel():
    df = pd.read_excel('../MedicinesAuthority/AdvancedSearchResultsLocal_august.xls')
    columns = ['Product', 'ActiveIngredient', 'PharmaceuticalForm', 'TherapeuticClass', 'Classification', 'ATC',
               'Status', 'AuthorisationNumber', 'AuthorisationDate', 'AuthorisationHolder',
               'AuthorisationHolderAddress', 'MAHContact1', 'MAHContact2', 'LicenceNumber']
    df.columns = columns
    df[columns] = df[columns].apply(lambda x: x.str.strip(' '))
    df[columns] = df[columns].apply(lambda x: x.str.strip('\''))
    df[columns] = df[columns].apply(lambda x: x.str.strip(' '))
    # print(df['ActiveIngredient'].head())
    # print(df.shape[0])
    unique_active_ingred = df['ActiveIngredient'].unique()
    # print(unique_active_ingred.tolist())

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
            else:
                print('No digit: ' + row)
                ingreds_per_row.append(ingred.strip())
        active_ingred.append([active_ingreds_col, ingreds_per_row, row['Product'], row['TherapeuticClass'], row['ATC'], row['PharmaceuticalForm'], row['Status']])

    # print(active_ingred)
    df = pd.DataFrame(active_ingred, columns=['ActiveIngredients', 'List', 'Product', 'TherapeuticClass', 'ATC', 'PharmaceuticalForm', 'Status'])
    df.to_csv('active_ingredients_separated.csv')

    flat_list = []
    for sublist in active_ingred:
        for item in sublist[1]:
            flat_list.append(item)

    # print(len(flat_list))
    flat_list = list(set(flat_list))
    # print(len(flat_list))

    return df, active_ingred

def createProduct(productName, medicinalForm, medicinalStatus):
    productName = productName.replace('&', ' and ')
    productName = productName.replace('/', ' ')
    medicX_product = URIRef(
        (ontology[urllib.parse.quote(productName.replace(' ', '_'))]))
    graph.add((medicX_product, RDF.type, Product))
    graph.add((medicX_product, name, Literal(productName)))
    graph.add((medicX_product, status, Literal(medicinalStatus)))

    medicX_MedicinalForm = URIRef((ontology[urllib.parse.quote(medicinalForm.replace(' ', '_'))]))
    graph.add((medicX_MedicinalForm, RDF.type, MedicinalForm))
    graph.add((medicX_MedicinalForm, name, Literal(medicinalForm)))

    graph.add((medicX_product, ontology.has_medicinal_form, Literal(medicX_MedicinalForm)))

    return medicX_product


def createActiveIngredient(activeIngredient):
    medicX_drug = URIRef((ontology[urllib.parse.quote(activeIngredient.replace(' ', '_'))]))
    graph.add((medicX_drug, RDF.type, ActiveIngredient))
    graph.add((medicX_drug, name, Literal(activeIngredient)))

    return medicX_drug


def createCompound(compound):
    medicX_compound = URIRef((ontology[urllib.parse.quote(compound)]))
    graph.add((medicX_compound, RDF.type, Compound))
    graph.add((medicX_compound, name, Literal(compound)))

    return medicX_compound


def createIndication(indication):
    medicX_indication = URIRef((ontology[urllib.parse.quote(indication.title().replace(' ', '_'))]))
    graph.add((medicX_indication, RDF.type, Indication))
    graph.add((medicX_indication, name, Literal(indication)))
    return medicX_indication


def createSideEffect(sideEffect):
    medicX_sideEffect = URIRef((ontology[urllib.parse.quote(sideEffect.title().replace(' ', '_'))]))
    graph.add((medicX_sideEffect, RDF.type, ADR))
    graph.add((medicX_sideEffect, name, Literal(sideEffect)))
    return medicX_sideEffect


def createATCode(atcCode, atcName):
    medicX_atc = URIRef((ontology[atcCode]))
    graph.add((medicX_atc, RDF.type, ATCCode))
    graph.add((medicX_atc, name, Literal(atcCode)))
    graph.add((medicX_atc, label, Literal(atcName)))

    bioPortalATC = URIRef((bioPortalOntology[atcCode]))
    graph.add((medicX_atc, OWL.sameAs, bioPortalATC))

    return medicX_atc


def createDDI(medicX_drugA, medicX_drugB, row):
    # print("Creating DDI between " + row['druga'] + ' and ' + row['drugb'])
    medicX_ddi = URIRef(
        (ontology[urllib.parse.quote((row['druga'] + '_' + row['drugb']).title()).replace(' ', '_')]))
    graph.add((medicX_ddi, RDF.type, DrugDrugInteraction))
    graph.add((medicX_ddi, name,
               Literal('Drug-drug Interaction between ' + row['druga'] + ' and ' + row['drugb'])))

    graph.add((medicX_ddi, interaction_type, Literal(row['desc'])))
    graph.add((medicX_ddi, interaction_severity, Literal(row['severity'])))
    graph.add((medicX_ddi, interaction_evidence, Literal(row['evidence'])))

    graph.add((medicX_drugA, ontology.has_drug_interaction, medicX_ddi))
    graph.add((medicX_drugB, ontology.has_drug_interaction, medicX_ddi))

    graph.add((medicX_ddi, interaction_type, Literal(row['desc'])))
    graph.add((medicX_ddi, interaction_severity, Literal(row['severity'])))
    graph.add((medicX_ddi, interaction_evidence, Literal(row['evidence'])))


def addTriplesFromDrugBank(medicX_ActiveIngredient, drugBankID):
    graph.add((medicX_ActiveIngredient, drugbankID, Literal(drugBankID)))
    graph.add((medicX_ActiveIngredient, drugbankURL, Literal('https://go.drugbank.com/drugs/'+drugBankID)))
    # add atc
    return medicX_ActiveIngredient


def addTriplesFromBNF(medicX_activeIngredient, activeIngred):
    directory = '../Multi-Classifier/bnf_info/'
    bnfFileName = directory + activeIngred + '_bnf_info.json'
    with open(bnfFileName, 'r') as fp:
        drug_data = json.load(fp)

        drug_bnf = drug_data['drug']
        drug_url_bnf = drug_data['drug_url']

        graph.add((medicX_activeIngredient, bnf_url, Literal(drug_url_bnf)))
        # graph.add((medicX_drug, medicines_authority_url, Literal("https://example.com/panadol")))
        # graph.add((medicX_drug, fertility, Literal(fertility)))
        if 'pregnancy' in drug_data:
            pregnancy_bnf = drug_data['pregnancy']
            graph.add((medicX_activeIngredient, pregnancy, Literal(pregnancy_bnf)))

        if 'breastFeeding' in drug_data:
            breastFeeding_bnf = drug_data['breastFeeding']
            graph.add((medicX_activeIngredient, breastFeeding, Literal(breastFeeding_bnf)))

        if 'indications' in drug_data:
            indications_bnf = drug_data['indications']
            for indication in indications_bnf:
                medicX_indication = createIndication(indication)
                graph.add((medicX_activeIngredient, ontology.has_indication, medicX_indication))

        if 'side_effects' in drug_data:
            side_effects_bnf = drug_data['side_effects']
            furtherInfo = ''
            overdose = ''
            for sideEffects in side_effects_bnf:
                freq = sideEffects[0]
                sideEffects = sideEffects[1].split('; ')
                for sideEffect in sideEffects:
                    if freq.lower() != 'further information' and freq != 'overdose':
                        medicX_sideEffect = createSideEffect(sideEffect)
                    if freq.lower() == 'common or very common':
                        graph.add((medicX_activeIngredient, ontology.has_common_side_effect, medicX_sideEffect))
                    elif freq.lower() == 'uncommon':
                        graph.add((medicX_activeIngredient, ontology.has_uncommon_side_effect, medicX_sideEffect))
                    elif freq.lower() == 'Rare or very rare':
                        graph.add((medicX_activeIngredient, ontology.has_rare_side_effect, medicX_sideEffect))
                    elif freq.lower() == 'frequency not known':
                        graph.add((medicX_activeIngredient, ontology.has_frequency_not_known_side_effect, medicX_sideEffect))
                    elif freq.lower() == 'further information':
                        furtherInfo += sideEffect
                    elif freq.lower() == 'overdose':
                        overdose += sideEffect

            if furtherInfo != '':
                graph.add((medicX_activeIngredient, adr_further_information, Literal(furtherInfo)))
            if overdose != '':
                graph.add((medicX_activeIngredient, adr_overdose, Literal(overdose)))

        if 'allergies' in drug_data:
            allergies_bnf = drug_data['allergies']
            graph.add((medicX_activeIngredient, allergies, Literal(allergies_bnf)))

        if 'caution' in drug_data:
            caution_bnf = drug_data['caution']
            graph.add((medicX_activeIngredient, caution, Literal(caution_bnf)))

        if 'action' in drug_data:
            action_bnf = drug_data['action']
            graph.add((medicX_activeIngredient, action, Literal(action_bnf)))

        if 'contraIndications' in drug_data:
            contraIndications_bnf = drug_data['contraIndications']
            for contraIndication in contraIndications_bnf:
                medicX_contraIndication = URIRef((ontology[urllib.parse.quote(contraIndication.title().replace(' ', '_'))]))
                graph.add((medicX_activeIngredient, ontology.has_contraIndication, medicX_contraIndication))
                graph.add((medicX_contraIndication, RDF.type, Contraindication))
                graph.add((medicX_contraIndication, name, Literal(contraIndication)))

        if 'relatedDrugs' in drug_data:
            relatedDrugs_bnf = drug_data['relatedDrugs']
            for relatedDrug in relatedDrugs_bnf:
                # TherapeuticClass
                medicX_therapeuticClass = URIRef((ontology[urllib.parse.quote(relatedDrug[0].title().replace(' ', '_'))]))
                graph.add((medicX_therapeuticClass, RDF.type, TherapeuticClass))
                graph.add((medicX_therapeuticClass, name, Literal(relatedDrug[0])))
                graph.add((medicX_activeIngredient, ontology.has_therapeutic_class, medicX_therapeuticClass))

                if relatedDrug[2] != '' and relatedDrug[2] is not None:
                    medicX_relatedDrug = createActiveIngredient(relatedDrug[2])
                    graph.add((medicX_relatedDrug, bnf_url, Literal(relatedDrug[1])))
                    graph.add((medicX_relatedDrug, ontology.has_therapeutic_class, medicX_therapeuticClass))

    return medicX_activeIngredient


if __name__ == '__main__':
    print("Parsing Medicines Authority Excel file")
    # medicinesAuthority, active_ingred = parseMedicinesAuthorityExcel()
    from map_medicinesAuthority_sample import retrieveSampledProducts
    active_ingred = retrieveSampledProducts()
    print("Finished parsing Medicines Authority Excel file")

    map(active_ingred)

    print("Creating DDIs")
    directory = '../scraped_bnf_interactions'
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            df = pd.read_csv(f, index_col=0)
            for index, row in df.iterrows():
                # desc = (row['desc'].lower().replace(row['druga'].lower(), 'drugA')).replace(row['drugb'].lower(), 'drugB')
                drugA = row['druga']
                drugB = row['drugb']

                # create active ingredient
                medicX_drugA = createActiveIngredient(drugA.lower())
                medicX_drugB = createActiveIngredient(drugA.lower())

                createDDI(medicX_drugA, medicX_drugB, row)

    graph.serialize(destination='example_kg_sampled_v2.nq', format='nquads')
