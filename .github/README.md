# ENTSO-E Application Profiles Library

v1.1.0 ICTC approved on 11 September 2025

v1.1.1 patch release (bug solving) approved in CIM WG on 7 October 2025

# Overview
This library contains all applications profiles for Common Grid Model Exchange Standard/Specification (CMGES) and Network Code Profiles (NCP) organised in a folder structure. The application profiles consist of vocabulary schemas (RDFS) and constraints (SHACL) derived from the information model in UML available on the [ENTSO-E CGMES Library](https://www.entsoe.eu/data/cim/cim-for-grid-models-exchange/#_ENTSO_E_CGMES_Extension_and_Profile).

The folders (and branches) reveal which artifacts were used in which release and version of the CGMES and NCP. In the main branch, the folders are also dived into a current release and previous release. As ENTSO-E updates the artefacts, the ones under current release will be moved to previous release (and to additional branches) as archived.

Note that for some of the previous version’s folders (e.g., for CGMES v2.4, NCP v2.2), an Enhanced folder exists. Such folders have a version that is updated after the official version release. This happens in cases where (profiling and validation) tooling was updated in the meantime and offers users using an archived, but updated version of the artifacts bug fixes discovered years after their release. 

Enhanced versions of other previous release folders can be generated under request.


### How to provide feedback
When importing any data contained in the repository, you might find bugs or issues to report. Please, open a GitHub issue and include your export log when applicable. Additionally, please write an email to [cim@entsoe.eu](cim@entsoe.eu).

Do not forget to read [CONTRIBUTING](https://github.com/entsoe/application-profiles-library/blob/main/.github/CONTRIBUTING.adoc) file.

### License
Please, refer to the [LICENSE](https://github.com/entsoe/application-profiles-library/blob/main/LICENSE.txt) for more information on the open-source license collaboration framework of the repository.

### Accreditations
List of the people and organisations contributing to this repository.

- [@EduardoRelAlg](https://github.com/EduardoRelAlg) - ENTSO-E
- [@griddigit-eu](https://github.com/griddigit-eu) - gridDigIt

# Introduction

ENTSO-E agreed to publish all application profiles in one package which has a structure to distinguish CGMES, Network Code Profiles (NCP) and DatasetMetadata related RDFS (vocabulary) and SHACL (constraints) artifacts. Specifically for the NCP and the DatasetMetadata profiles, there is a distinction between the current and past versions. All the material can be found on the CGMES Library under the Application Profiles Library tab.

The application profiles are provided to facilitate the implementation of the profiles and related constraints as defined in different standards, e.g. IEC 61970-600-1:2021, IEC 61970-600-2:2021, IEC 61970-301 and other related 61970-45x series of profiles. 

Note that the application profile serialization based on RDFS and RDF XML syntax is defined in IEC 61970-501:2006 (Ed1) and CIM XML serialization is defined in IEC 61970-552:2016. However, current implementations deviate from these standards due to various reasons. For additional information, please refer to the latest version of the [RDF-syntax User Guide](https://www.entsoe.eu/data/cim/cim-for-grid-models-exchange/#_ENTSO_E_CGMES_Extension_and_Profile) CGMES Library.

The content of the Application Profiles Library is published under [Apache 2.0 open-source license](https://github.com/entsoe/application-profiles-library/blob/main/LICENSE.txt).

# ENTSO-E GitHub Repository Structure

ENTSO-E offers the [application-profiles-library](https://github.com/entsoe/application-profiles-library/) GitHub Repository storing all the published CIM related artifacts (including CGMES and the NCP).

The main branch stores all the available artifacts and several snapshots in time will constitute the application profiles library releases as such. This branch is continuously under development and ENTSO-E CIM WG so it can be considered the _edge_ or _development_ branch. 

On the other hand, the repository is also subdivided into several branches corresponding to packages of profiles’ sets releases. With this structure, ENTSO-E aims at enhancing transparency and clearly associating a set of machine artifacts to profiles releases.

As an example, someone interested in the NCP v2.2 release artifacts can access them in the main branch but also in the branch _ncp-v2-2_.

This current document establishes in [section 6](# Application Profiles – File Naming Convention) the naming convention used for the artifacts in the application profiles library. However, in order to exploit git functionalities for version control, the artifacts in the main branch may not include the version number in the files’ name. Every time a change is done in a file, it must increase the version number but if one does this, git will not capture the changes as it needs the file name to be static. 

Only once a release is ready for publication, a new branch will be created with the subset of artifacts corresponding to it. 
As an example, imagine that the current release of the NCP is version 2.4. In the moment of publication, the main branch and the _ncp-v2-4-0_ contain the exact same. One month later, ENTSO-E CIM WG detects a bug in the release’ artifacts (e.g., the _AssessedElement-AP-Voc-RDFS2020.rdf_) and fixes it in the main branch, thus the two previous branches differ. When the next release v2.5 of the NCP is ready, a new branch _ncp-v2-5-0_ will be created and the process restarted.

Regardless of the file naming convention used exclusively for human readability, all artifacts contain version fields in the dataset header (_dcat:isVersionOf_, _dcterms:conformsTo_, etc.) which shall be used for machine readability.

## Special Mentions

### Solving inconsistency in the use of dcterms ontology

All current releases of CGMES ([v3.0](https://github.com/entsoe/application-profiles-library/tree/cgmes-v3-0)) and NCP ([v2.4](https://github.com/entsoe/application-profiles-library/tree/ncp-v2-4-0)) RDFS and SHACL artifacts are updated to replace the term _dct_ with the term _dcterms_. This is done because dct was initially use but later decided not to use. This change enhances consistency.

### Addition of header schema for CGMES v3.0

For context, CGMES v3.0 profiles have the metadata under owl:Onthology. On the other hand, CGMES v2.4 profiles have the metadata under entsoe:<profile>Version.

A maintenance request detected that [File Header RDFS of CGMES v3.0](https://github.com/entsoe/application-profiles-library/blob/main/CGMES/CurrentRelease/RDFS/61970-600-2_Header-AP-Voc-RDFS2019.rdf) was missing the metadata. This originated a the addition of a [new File Header RDFS](https://github.com/entsoe/application-profiles-library/blob/main/CGMES/CurrentRelease/RDFS/61970-600-2_Header-AP-Voc-RDFS2020.rdf) that features a new Ontology file header added to the schema (RDFS).

It is recommended to use the [new File Header RDFS](https://github.com/entsoe/application-profiles-library/blob/main/CGMES/CurrentRelease/RDFS/61970-600-2_Header-AP-Voc-RDFS2020.rdf) instead of the [old](https://github.com/entsoe/application-profiles-library/blob/main/CGMES/CurrentRelease/RDFS/61970-600-2_Header-AP-Voc-RDFS2019.rdf).


# RDF schemas (RDFS)
The RDFS 2020 export of the RDFS augmented version is based on IEC 61970-501:2006 (Ed1). The package contains RDFS for CGMES v3.0 and NC Profiles. These are the files which file name contains “Voc-RDFS2020”.

In addition a [beta version](https://github.com/entsoe/application-profiles-library/tree/main/CGMES/CurrentRelease/RDFS/Beta_501_Ed2_CD) of application profile based on RDFS specified in the draft IEC 61970-501:Ed2 (see subfolder CGMES\RDFS\Beta_501_Ed2_CD) is provided. The purpose of inclusion of the beta version in the distribution is to enable the review process. 

Please use these files only for information on the direction where RDFS will evolve in that standard and provide feedback that will be discussed in the standardisation process. 
Namely, the RDFS contains the vocabulary part only, while the constraints (cardinalities, datatypes, etc.) are expressed by SHACL based constraints.

# Constraints
SHACL based constraints are provided for CGMES v3.0 and NC Profiles. These are the files which file name contains “Con-SHACL” or “Con-{xys}-SHACL”, where {xys} indicates the main content. For instance, “Con-Simple-SHACL” indicates that the constraints were derived from RDFS and “Con-Complex-NotSolvedMAS-SHACL” indicates that constraints have manually been produced and are applicable for a model that contains Equipment (EQ) and Steady State Hypothesis (SSH) profiles of CGMES.

Please, note that constraints automatically generated from the schema are denoted as Simple. The constraints needing some manual expert modifications are denoted as Complex. In case these two scenarios are combined, this is indicated not specifying anything (nor Simple, nor Complex). 

The following additional details facilitate the usage of the CGMES constraints:

* Constraints marked as “NotSolvedMAS” are constraints defined in document and translated in SHACL. These constraints apply to a not solved MAS, i.e. EQ and SSH information.
* Constraints marked as “SolvedMAS” are constraints defined in document and translated in SHACL. These constraints apply to a solved MAS, i.e. EQ, SSH, TP and SV information.
* Constraints marked as “CrossProfile” are constraints defined in document and translated in SHACL. Used for cross profile validation.
* Constraints marked as “Explicit-CrossProfile” are constraints defined in document and translated in SHACL. Explicit (references to classes are explicit) constraints for cross profile validation.
* Constraints marked as “Implicit-CrossProfile” are constraints defined in document and translated in SHACL. Implicit (references to classes are implicit and require RDFS information on the inheritance) constraints for cross profile validation.
* Constraints marked as “InverseAssociation” are constraints defined in document and translated in SHACL. For checking inverse associations.

There are constraints for cardinalities and datatypes derived from the RDFS, constraints defined in the descriptions of the classes and attributes, constraints defined in IEC 61970-600-1:2021, IEC 61970-600-2:2021, IEC 61970-301 and other related 61970-45x series of profiles and expressed there in plain English text. Note that SHACL based constraints in this folder are serialised in two RDF formats, Turtle and RDF XML plain (no nesting). Originally the constraints were developed in Turtle using Notepad++ as an editor and then converted to RDF XML using [CimPal](https://github.com/griddigit-ci/CimPal) app. 

The recommended serialisation of SHACL constraints is Turtle as that was the primary serialisation and it is well tested. This is because many constraints rely on SHACL SPARQL method, which is not covered in the draft IEC 61970-501:Ed2, the RDF XML may not represent the desired way of serialisation. However, the resulted RDF XML version was not used or validated in terms of content and should be used with a caution.

OCL based constraints are not provided. Versions of OCL constraints provided earlier are no longer maintained. Only SHACL constraints will be maintained.

# Application Profiles – File Naming Convention
Filename shall only be used for human consumption and shall not be processes to decode metadata. Machine interpretation shall use the Manifest file, that includes all the relevant metadata and reference to the dataset artifacts. The datasets are currently included in the sip file but can later be stored in a linked repository. Manifest file will be added as a technical update as soon as it is ready.

Filename convention is linked to the dataset information in the file header.
< dct:publisher>_<dct:title>_<owl:versionInfo>.<mediaType>

Examples:
* [61970-301-DiagramLayout-AP-Con-SHACL_v3-0-0.rdf](https://github.com/entsoe/application-profiles-library/blob/main/CGMES/CurrentRelease/RDFS/61970-600-2_DiagramLayout-AP-Voc-RDFS2020.rdf)
* [61970-600-2-Header-AP-Voc-RDFS2019_v3-0-0.rdf](https://github.com/entsoe/application-profiles-library/blob/main/CGMES/CurrentRelease/RDFS/61970-600-2_Header-AP-Voc-RDFS2019.rdf)
* [61970-600-2-Operation-AP-Con-Simple-SHACL_v3-0-0.ttl](https://github.com/entsoe/application-profiles-library/blob/main/CGMES/CurrentRelease/SHACL/TTL/61970-600-2_Operation-AP-Con-Simple-SHACL.ttl)

ENTSO-E does not put the publisher in the file name as it is not expected that these artifacts will be republished. 

# SHACL Constraints Design
Constraints for CGMES v3.0 were designed in 2020 and a master spreadsheet named CGMES Constraints Repository was prepared.
 
# Master spreadsheet of CGMES v3.0 constraints
## Overview 
-	2025 constraints are listed in the master spreadsheet.
-	All profiles part of CGMES v3.0 were screened for constraints that can be validated. To a large extend these are value related constraints (>0, <0, etc), but there are some that are more complex. DY profile has about 1500 value constraints which is about 75% of all constraints. In the process of defining validation rules/constraints in machine readable form some of the complex constraints were split in order to have more exact validation results.
-	171 constraints from IEC 61970-600-2.
-	33 constraints from IEC 61970-600-1.
-	22 constraints were extracted from the IEC 61970-301:Ed7 
-	3 constraints were extracted from the IEC 61970-457:Ed1.  
-	212 constraints were extracted from UML descriptions from profiles other than DY profile.

## Explanation of the master spreadsheet columns
The master spreadsheet contains information on all constraints, their source and ID. The following summarises the columns in the spreadsheet and their usage:

* Columns A-F are general references to indicate the source of the constraint. In column E the value “UML description” means that these are constraints extracted from the descriptions in the UML so then in column J the relevant part of the description that is the constraint is added. Sometimes it is the whole description sometimes only part depending on the case.
* Column A is a key that is UUID. It is not used now for specific purpose, but it might be useful to track changes.
* Column G is the ID which follows the naming convention agreed in the IEC 61970-452 and in IEC 61970-600-1 and-2. The ID is complete for the constraints that are either references from other documents or there is machine readable representation of them. Note that some are incomplete as there are either with not in SHACL or there is some other reason indicated in the columns.
* Columns H and I are a bit indicative where the constraint is attached or main source for the constraint. For the IDs there is an Excel formula which in most of the cases uses these 2 columns in addition to others. Note that some of the IDs and Name, Class were done manually – so it is not always the formula. 
* Column J is the description of the constraint. This is either coming from UML or some standard. The wording there is exactly the same as in the standard. In fact, for the IEC 61970-600-2 this column was used together with column G to populate the constraints in 600-2 clause 16. 
* Column K and L are the message and the severity. An approach has been taken in which the message should say what is wrong rather than what should be. The severity is derived from the description of the constraint (column J), but in some cases (especially where the wording is not that concrete) maybe more restrictive approach has been taken. In general, there is an open area in CIM standards on how to define the severities and their meaning for the data exchange, so this is a topic which is open for future discussion. 
* Column M attempts to clarify if the constraint can be checked by just looking at instance data of one profile or the validation scope is more than that. There are many constraints that require data from other profiles, so that column tries to capture this. That would help to design which check is triggered when.
* Column N indicates if the constraint is part of the standard or it is business specific as it is the case for CGM. In case of business process specific, column O gives the information which process.
* Column P is providing comments – there some key words like REASON, ATTENTION, PROPOSAL, INFO, QUESTION, REPORT TO WG13, etc are used in order to be able to filter and find out what is follow up actions or proposal. 
* Column Q is added for admin purpose to indicate when a constraint was modified.
* Column R indicates the status on SHACL. Here it is indicated which constraints are done in the SHACL shapes package. There is indication in case the constraint cannot be validated/represented in machine readable way, or it is not needed, and the reason is given in the comment’s column.  
* Column S indicates the file name of the .ttl file where the constraint is defined.
* Column T indicates the date of the last modification of the code.