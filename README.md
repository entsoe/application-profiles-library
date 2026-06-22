# CGMES v2.4 and QoCDC SHACL Constraints

## Overview
This folder contains **SHACL-based validation constraints** for **CGMES v2.4 and QoCDC 4.1.4** datasets.

---

## Content
The directory includes:
- SHACL shapes 
- Constraint definitions derived from:
  - CGMES v2.4 profiles
  - QoCDC requirements (partial coverage)
- Supporting structures for validation workflows

These constraints are used to validate:
- Structural conformance (profiles, relationships)
- Datatype consistency
- Mandatory attributes and associations

---

## Usage

### Prerequisites
To use these constraints, you need:
- A CGMES v2.4 dataset (RDF/XML)
- Datatype mappings 
- A SHACL validation engine 

### Validation Workflow
Typical validation process:

1. Load CGMES dataset
2. Load datatype mapping
3. Load SHACL constraints from this folder
4. Execute validation

