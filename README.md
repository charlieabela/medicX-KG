# medicX-KG: A Knowledge Graph for Pharmacists' Drug Information Needs

This repository contains sample files, mapping scripts, and data subsets from the medicX-KG project, aimed at constructing a pharmacist-oriented biomedical knowledge graph with regulatory awareness specific to small EU markets such as Malta.

## Repository Structure

```
/scripts/
    map_medicinesAuthority.py           # Mapping script (refactored)
    MappingHelperMethods.py              # Helper functions
/data/
    active_ingredients_separated_sample.csv
    AdvancedSearchResultsLocal_sample.xls
    sampledProducts.csv
    feedback.xlsx
/kg/
    example_kg_sampled_v2.nq.zip         # RDF graph sample (N-Quads)
/docs/
    (Documentation and additional examples can be added here)
README.md
LICENSE
```

## How to Reproduce the Knowledge Graph

1. Clone this repository:
   ```bash
   git clone https://github.com/[your-username]/medicX-KG.git
   cd medicX-KG
   ```

2. Install required Python libraries:
   ```bash
   pip install pandas rdflib openpyxl
   ```

3. Ensure that `/data/` contains the relevant files (sampledProducts.csv, active ingredients, ATC ontology, etc.).

4. Run the mapping script:
   ```bash
   python scripts/map_medicinesAuthority.py
   ```

5. The output RDF triples can be serialised into N-Quads, Turtle, or RDF/XML depending on further needs.

## About medicX-KG

medicX-KG addresses pharmacist decision support challenges in small jurisdictions that are aligned with EU law but face supply chain and regulatory particularities (e.g., continued reliance on UK imports post-Brexit).

For details, refer to our manuscript: *medicX-KG: A Knowledge Graph for Pharmacists' Drug Information Needs*.

## License

Sample data is made available for academic review purposes. Licensing terms: Creative Commons Attribution 4.0 International (CC BY 4.0). See LICENSE file.

## How to Cite

If you use medicX-KG or its resources in your research or applications, please cite:

> Charlie Abela, Lizzy Farrugia, Lilian M. Azzopardi, and Jeremy Debattista. *medicX-KG: A Knowledge Graph for Pharmacists' Drug Information Needs.* Under review in the Journal of Biomedical Semantics (JBMS), 2025.

Once available, a preprint version can be accessed via [Research Square](https://www.researchsquare.com/).

A formal citation will be updated here once the final DOI is issued.

### BibTeX (preliminary)

```bibtex
@misc{abela2025medicxkg,
  author = {Charlie Abela and Lizzy Farrugia and Lilian M. Azzopardi and Jeremy Debattista},
  title = {medicX-KG: A Knowledge Graph for Pharmacists' Drug Information Needs},
  year = {2025},
  note = {Manuscript under review in the Journal of Biomedical Semantics. Preprint available on Research Square.}
}
```

## Contact

For questions or collaboration, please contact:
- Dr. Charlie Abela - charlie.abela@um.edu.mt
