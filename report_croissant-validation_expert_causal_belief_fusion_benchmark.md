# CROISSANT VALIDATION REPORT
================================================================================
## VALIDATION RESULTS
--------------------------------------------------------------------------------
Starting validation for file: croissant_metadata.json
### JSON Format Validation
✓
The file is valid JSON.
### Croissant Schema Validation
✓
The dataset passes Croissant validation.
### Responsible AI Metadata
✓
All required Responsible AI metadata fields are present.
### Records Generation Test
✓
No record sets found to validate.
## JSON-LD REFERENCE
================================================================================
```json
{
  "@context": {
    "@language": "en",
    "@vocab": "https://schema.org/",
    "sc": "https://schema.org/",
    "cr": "http://mlcommons.org/croissant/",
    "dct": "http://purl.org/dc/terms/",
    "rai": "http://mlcommons.org/croissant/RAI/",
    "prov": "http://www.w3.org/ns/prov#",
    "@base": "cr_base_iri/"
  },
  "@type": "sc:Dataset",
  "name": "expert_causal_belief_fusion_benchmark",
  "description": "A Benchmark for Fusing Expert-Elicited Causal Beliefs under Uncertainty. This dataset provides expert-elicited belief assignments over candidate directed causal edges. For each candidate edge, experts assign belief masses to three hypotheses: edge existence, edge non-existence, and explicit uncertainty. The benchmark supports evaluation of uncertainty-aware belief fusion methods for causal edge assessment.",
  "url": "https://github.com/noname31157/A-Benchmark-for-Fusing-Expert-Elicited-Causal-Beliefs-under-Uncertainty",
  "license": "https://creativecommons.org/licenses/by-nc/4.0/",
  "conformsTo": "http://mlcommons.org/croissant/1.1",
  "version": "1.0.0",
  "datePublished": "2026",
  "creator": [
    {
      "@type": "sc:Organization",
      "name": "Anonymous Authors"
    }
  ],
  "citation": "@misc{causal_belief_fusion_benchmark, title={A Benchmark for Fusing Expert-Elicited Causal Beliefs under Uncertainty}, author={Anonymous Authors}, year={2026}, note={Benchmark dataset and code repository}}",
  "keywords": [
    "causal discovery",
    "causal inference",
    "expert elicitation",
    "uncertainty quantification",
    "Dempster-Shafer theory",
    "belief fusion",
    "causal edge benchmark"
  ],
  "distribution": [
    {
      "@type": "sc:FileObject",
      "@id": "all_expert_rows_combined_csv",
      "name": "all_expert_rows_combined_csv",
      "description": "Combined machine-readable dataset containing expert belief assignments for candidate directed causal edges.",
      "contentUrl": "https://raw.githubusercontent.com/noname31157/A-Benchmark-for-Fusing-Expert-Elicited-Causal-Beliefs-under-Uncertainty/main/data/all_expert_rows_combined.csv",
      "encodingFormat": "text/csv",
      "sha256": "875c9f51c94bb5e1c688afea50403a133cd5a7d215bb0ec747e6b4fcdf5de70e"
    },
    {
      "@type": "sc:FileObject",
      "@id": "master_summary_csv",
      "name": "master_summary_csv",
      "description": "Main edge-level fusion summary containing fused masses and derived uncertainty-aware quantities across fusion methods.",
      "contentUrl": "https://raw.githubusercontent.com/noname31157/A-Benchmark-for-Fusing-Expert-Elicited-Causal-Beliefs-under-Uncertainty/main/results/master_summary.csv",
      "encodingFormat": "text/csv",
      "sha256": "b03f1224043b7894c21a0374a9d2a500d4960259737fc7ed72e38326b43bfde8"
    }
  ],
  "recordSet": [
    {
      "@type": "cr:RecordSet",
      "@id": "expert_belief_assignments",
      "name": "expert_belief_assignments",
      "description": "Rows describing expert-assigned belief masses for candidate directed causal edges.",
      "field": [
        {
          "@type": "cr:Field",
          "@id": "expert_belief_assignments/edge",
          "name": "Edge",
          "description": "Candidate directed causal edge.",
          "dataType": "sc:Text",
          "source": {
            "fileObject": {
              "@id": "all_expert_rows_combined_csv"
            },
            "extract": {
              "column": "Edge"
            }
          }
        },
        {
          "@type": "cr:Field",
          "@id": "expert_belief_assignments/sources",
          "name": "Sources",
          "description": "Anonymized expert identifier or evidence source.",
          "dataType": "sc:Text",
          "source": {
            "fileObject": {
              "@id": "all_expert_rows_combined_csv"
            },
            "extract": {
              "column": "Sources"
            }
          }
        },
        {
          "@type": "cr:Field",
          "@id": "expert_belief_assignments/m_e",
          "name": "m_e",
          "description": "Belief mass assigned to the hypothesis that the causal edge exists.",
          "dataType": "sc:Float",
          "source": {
            "fileObject": {
              "@id": "all_expert_rows_combined_csv"
            },
            "extract": {
              "column": "m(e)"
            }
          }
        },
        {
          "@type": "cr:Field",
          "@id": "expert_belief_assignments/m_not_e",
          "name": "m_not_e",
          "description": "Belief mass assigned to the hypothesis that the causal edge does not exist.",
          "dataType": "sc:Float",
          "source": {
            "fileObject": {
              "@id": "all_expert_rows_combined_csv"
            },
            "extract": {
              "column": "m(not e)"
            }
          }
        },
        {
          "@type": "cr:Field",
          "@id": "expert_belief_assignments/m_50_50",
          "name": "m_50_50",
          "description": "Belief mass assigned to explicit uncertainty or 50-50 belief.",
          "dataType": "sc:Float",
          "source": {
            "fileObject": {
              "@id": "all_expert_rows_combined_csv"
            },
            "extract": {
              "column": "m(50-50)"
            }
          }
        },
        {
          "@type": "cr:Field",
          "@id": "expert_belief_assignments/remarks",
          "name": "Remarks",
          "description": "Optional expert remarks or notes.",
          "dataType": "sc:Text",
          "source": {
            "fileObject": {
              "@id": "all_expert_rows_combined_csv"
            },
            "extract": {
              "column": "Remarks"
            }
          }
        }
      ]
    },
    {
      "@type": "cr:RecordSet",
      "@id": "fusion_summary",
      "name": "fusion_summary",
      "description": "Rows describing fused causal edge beliefs for each fusion method.",
      "field": [
        {
          "@type": "cr:Field",
          "@id": "fusion_summary/edge",
          "name": "Edge",
          "description": "Candidate directed causal edge.",
          "dataType": "sc:Text",
          "source": {
            "fileObject": {
              "@id": "master_summary_csv"
            },
            "extract": {
              "column": "Edge"
            }
          }
        },
        {
          "@type": "cr:Field",
          "@id": "fusion_summary/method",
          "name": "Method",
          "description": "Fusion method.",
          "dataType": "sc:Text",
          "source": {
            "fileObject": {
              "@id": "master_summary_csv"
            },
            "extract": {
              "column": "Method"
            }
          }
        },
        {
          "@type": "cr:Field",
          "@id": "fusion_summary/fused_m_e",
          "name": "fused_m_e",
          "description": "Fused belief mass assigned to edge existence.",
          "dataType": "sc:Float",
          "source": {
            "fileObject": {
              "@id": "master_summary_csv"
            },
            "extract": {
              "column": "fused m(e)"
            }
          }
        },
        {
          "@type": "cr:Field",
          "@id": "fusion_summary/fused_m_not_e",
          "name": "fused_m_not_e",
          "description": "Fused belief mass assigned to edge non-existence.",
          "dataType": "sc:Float",
          "source": {
            "fileObject": {
              "@id": "master_summary_csv"
            },
            "extract": {
              "column": "fused m(not e)"
            }
          }
        },
        {
          "@type": "cr:Field",
          "@id": "fusion_summary/fused_m_50_50",
          "name": "fused_m_50_50",
          "description": "Fused belief mass assigned to explicit uncertainty or 50-50 belief.",
          "dataType": "sc:Float",
          "source": {
            "fileObject": {
              "@id": "master_summary_csv"
            },
            "extract": {
              "column": "fused m(50-50)"
            }
          }
        },
        {
          "@type": "cr:Field",
          "@id": "fusion_summary/belief_e",
          "name": "belief_e",
          "description": "Belief in edge existence.",
          "dataType": "sc:Float",
          "source": {
            "fileObject": {
              "@id": "master_summary_csv"
            },
            "extract": {
              "column": "Bel (e)"
            }
          }
        },
        {
          "@type": "cr:Field",
          "@id": "fusion_summary/plausibility_e",
          "name": "plausibility_e",
          "description": "Plausibility of edge existence.",
          "dataType": "sc:Float",
          "source": {
            "fileObject": {
              "@id": "master_summary_csv"
            },
            "extract": {
              "column": "Pl (e)"
            }
          }
        },
        {
          "@type": "cr:Field",
          "@id": "fusion_summary/betp",
          "name": "BetP",
          "description": "Pignistic probability of edge existence.",
          "dataType": "sc:Float",
          "source": {
            "fileObject": {
              "@id": "master_summary_csv"
            },
            "extract": {
              "column": "BetP"
            }
          }
        }
      ]
    }
  ],
  "rai:dataLimitations": "The benchmark represents expert beliefs over a defined set of candidate causal edges in a specific clinical causal-discovery setting. It should not be interpreted as definitive clinical causal ground truth or used for clinical decision-making without additional validation. The dataset is intended for evaluating uncertainty-aware belief fusion methods and causal edge assessment workflows.",
  "rai:dataBiases": "The benchmark may reflect selection bias from the chosen candidate edges, the expertise and disciplinary backgrounds of participating experts, and the clinical context used to define the variables. Expert judgments may vary due to differences in experience, interpretation of causal direction, and familiarity with the domain.",
  "rai:personalSensitiveInformation": "The released benchmark does not include patient-level medical records. It contains expert-assigned belief masses over candidate causal edges. Expert identifiers are anonymized or excluded where appropriate. The variables refer to clinical concepts, but no individual patient records are released in this repository.",
  "rai:dataUseCases": "The dataset is intended for benchmarking uncertainty-aware evidence fusion methods, studying expert disagreement in causal edge assessment, evaluating belief/plausibility/pignistic probability summaries, and supporting reproducible research in causal discovery under uncertainty. It is not intended for direct medical diagnosis, treatment recommendation, or deployment as a clinical decision-support system.",
  "rai:dataSocialImpact": "Potential positive impacts include improving transparency in expert-guided causal discovery, enabling reproducible comparison of belief fusion methods, and encouraging explicit reporting of uncertainty. Potential risks include overinterpreting expert beliefs as verified causal truth or using the benchmark outside its intended research context. These risks are mitigated by documenting limitations, uncertainty, and intended use cases.",
  "rai:hasSyntheticData": false,
  "prov:wasDerivedFrom": "Expert-elicited belief assignments collected through structured spreadsheet templates for candidate directed causal edges.",
  "prov:wasGeneratedBy": [
    {
      "@type": "prov:Activity",
      "name": "data_collection",
      "description": "Experts completed standardized spreadsheet templates by assigning belief masses to edge existence, edge non-existence, and explicit uncertainty for candidate directed causal edges."
    },
    {
      "@type": "prov:Activity",
      "name": "preprocessing",
      "description": "Raw expert spreadsheets were checked for consistency, converted into edge-level expert belief tables, and combined into a machine-readable CSV file."
    },
    {
      "@type": "prov:Activity",
      "name": "data_annotation",
      "description": "The annotation schema used three mutually exclusive belief categories: edge exists, edge does not exist, and uncertain. Quality control included checking that each expert-edge belief triplet summed to one."
    }
  ]
}
```