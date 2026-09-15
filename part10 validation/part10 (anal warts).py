from pymongo import MongoClient
from bson import ObjectId
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import padding
import hashlib
import time
import numpy as np
import spacy
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import copy

from part1.main import ontologyPointers

# DomainOntology = {
#     'Asthma': {
#         'Id': '11A',
#         'Parent': [
#             {
#                 'Id': '21215431311A',
#                 'Name': 'Disorder of respiratory system'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '21256751312A',
#                 'Name': 'Asthma in pregnancy'
#             },
#             {
#                 'Id': '29865431313A',
#                 'Name': 'Childhood asthma'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431314A',
#                 'Name': 'Shortness of breath'
#             },
#             {
#                 'Id': '29865431315A',
#                 'Name': 'Chest tightness'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431316A',
#                 'Name': 'Methacholine challenge'
#             },
#             {
#                 'Id': '29865431317A',
#                 'Name': 'Imaging tests'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431318A',
#                 'Name': 'Inhaled corticosteroids'
#             },
#             {
#                 'Id': '29865431319A',
#                 'Name': 'Leukotriene modifiers'
#             }
#         ]
#     },
#     'AnalWarts': {
#         'Id': '2212112B',
#         'Parent': [
#             {
#                 'Id': '212112410B',
#                 'Name': 'Anal Infection'
#             }
#         ],
#         'Children': [],
#         'Symptoms': [
#             {
#                 'Id': '29865431311B',
#                 'Name': 'Bleeding with sex'
#             },
#             {
#                 'Id': '29865431312B',
#                 'Name': 'A cauliflower-like shape caused by a few warts close together'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313B',
#                 'Name': 'Pap tests'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314B',
#                 'Name': 'Imiquimod'
#             },
#             {
#                 'Id': '29865431315B',
#                 'Name': 'Trichloroacetic acid'
#             }
#         ]
#     },
#     'Heart block': {
#         'Id': '2212112a',
#         'Parent': [
#             {
#                 'Id': '212112410a',
#                 'Name': 'Conduction disorder of the heart'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112411a',
#                 'Name': 'Atrioventricular block'
#             },
#             {
#                 'Id': '212112412a',
#                 'Name': 'Heart block caused by drug'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431313a',
#                 'Name': 'fainting (syncope)'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313',
#                 'Name': 'Electrocardiogram (ECG or EKG)'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314',
#                 'Name': 'medications to reduce high blood pressure or reduce symptoms of heart failure'
#             }
#         ]
#     },
#     'Pneumonia': {
#         'Id': '2212112b',
#         'Parent': [
#             {
#                 'Id': '212112410b',
#                 'Name': 'Infectious disease of lung (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410b',
#                 'Name': ' Abscess of lung with pneumonia (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311b',
#                 'Name': 'Chest pain when you breathe or cough'
#             },
#             {
#                 'Id': '29865431312b',
#                 'Name': 'Fever, sweating and shaking chills'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313b',
#                 'Name': 'Blood tests'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314b',
#                 'Name': 'Antibiotics'
#             },
#             {
#                 'Id': '29865431315b',
#                 'Name': 'Cough medicine'
#             }
#         ]
#     },
#     'Bronchitis': {
#         'Id': '2212112c',
#         'Parent': [
#             {
#                 'Id': '212182410c',
#                 'Name': 'Inflammation of specific body organs'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410c',
#                 'Name': 'Acute bronchitis (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311c',
#                 'Name': 'Sore throat'
#             },
#             {
#                 'Id': '29865431312c',
#                 'Name': 'Slight fever and chills'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313c',
#                 'Name': 'Chest X-ray'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314c',
#                 'Name': 'Cough medicine'
#             },
#             {
#                 'Id': '29865431315c',
#                 'Name': 'Antibiotics'
#             }
#         ]
#     },
#     'Tuberculosis': {
#         'Id': '2212112d',
#         'Parent': [
#             {
#                 'Id': '212112410d',
#                 'Name': 'Disorder characterized by granuloma formation (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112411d',
#                 'Name': 'Acute tuberculous ulcer (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311d',
#                 'Name': 'Low fever'
#             },
#             {
#                 'Id': '29865431312d',
#                 'Name': 'Tiredness'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313d',
#                 'Name': 'Listening to breathe with a stethoscope'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314d',
#                 'Name': 'Isoniazid'
#             },
#             {
#                 'Id': '29865431315d',
#                 'Name': 'Rifampin'
#             }
#         ]
#     },
#     'Gastritis': {
#         'Id': '2212112',
#         'Parent': [
#             {
#                 'Id': '212112410e',
#                 'Name': 'Disorder of stomach (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '2121124111e',
#                 'Name': 'Acute gastritis (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311e',
#                 'Name': 'Vomiting'
#             },
#             {
#                 'Id': '29865431312e',
#                 'Name': 'Nausea'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313e',
#                 'Name': 'Tests for H. pylori'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314e',
#                 'Name': 'Antibiotics to kill H. pylori'
#             },
#             {
#                 'Id': '29865431315e',
#                 'Name': 'Medicines that block acid production and promote healing'
#             }
#         ]
#     },
#     'Hepatitis A': {
#         'Id': '2212112f',
#         'Parent': [
#             {
#                 'Id': '212112410f',
#                 'Name': 'Viral hepatitis (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410f',
#                 'Name': 'Acute type A viral hepatitis (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311f',
#                 'Name': 'Unusual tiredness and weakness'
#             },
#             {
#                 'Id': '29865431312f',
#                 'Name': 'Sudden nausea and vomiting and diarrhea'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313f',
#                 'Name': 'Blood tests are used to look for signs of the hepatitis A virus'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314f',
#                 'Name': 'Get adequate food and liquid'
#             },
#             {
#                 'Id': '29865431315f',
#                 'Name': 'Avoid alcohol and use medications with care'
#             }
#         ]
#     },
#     'Cataracts': {
#         'Id': '2212112j',
#         'Parent': [
#             {
#                 'Id': '212112410j',
#                 'Name': 'Degenerative disorder of bilateral eyes (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410j',
#                 'Name': 'Anterior subcapsular polar cataract of bilateral eyes (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311j',
#                 'Name': 'Clouded, blurred or dim vision'
#             },
#             {
#                 'Id': '29865431312j',
#                 'Name': 'Need for brighter light for reading and other activities'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313j',
#                 'Name': 'Vision test'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314j',
#                 'Name': 'surgery'
#             }
#         ]
#     },
#     'Anaemia': {
#         'Id': '2212112g',
#         'Parent': [
#             {
#                 'Id': '212112410g',
#                 'Name': 'Disorder of cellular component of blood (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410g',
#                 'Name': 'Acquired Heinz body anemia (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311g',
#                 'Name': 'Shortness of breath'
#             },
#             {
#                 'Id': '29865431312g',
#                 'Name': 'Irregular heartbeat'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313g',
#                 'Name': 'Complete blood count, also called CBC'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314g',
#                 'Name': 'Iron deficiency anemia'
#             },
#             {
#                 'Id': '29865431315g',
#                 'Name': 'Anemia of chronic disease'
#             }
#         ]
#     },
#     'Depression': {
#         'Id': '2212112h',
#         'Parent': [
#             {
#                 'Id': '212112410h',
#                 'Name': 'Mood disorder (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410h',
#                 'Name': 'Acute depression (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311h',
#                 'Name': 'Feelings of sadness, tearfulness, emptiness or hopelessness'
#             },
#             {
#                 'Id': '29865431312h',
#                 'Name': 'Angry outbursts, irritability or frustration, even over small matters'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313h',
#                 'Name': 'Blood tests are used to look for signs of the hepatitis A virus'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314h',
#                 'Name': 'Anxious distress'
#             },
#             {
#                 'Id': '29865431315h',
#                 'Name': 'Melancholic features'
#             }
#         ]
#     },
#     'Glaucoma': {
#         'Id': '2212112i',
#         'Parent': [
#             {
#                 'Id': '212112410i',
#                 'Name': 'Disorder of eye proper (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410i',
#                 'Name': 'Absolute glaucoma (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311i',
#                 'Name': 'In later stages, difficulty seeing things in your central vision'
#             },
#             {
#                 'Id': '29865431312i',
#                 'Name': 'Gradually, patchy blind spots in your side vision. Side vision also is called peripheral vision'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313i',
#                 'Name': 'Measuring intraocular pressure, also called tonometry'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314i',
#                 'Name': 'Get adequate food and liquid'
#             },
#             {
#                 'Id': '29865431315i',
#                 'Name': 'Checking for areas of vision loss, also known as a visual field test'
#             }
#         ]
#     },
#     'Gout': {
#         'Id': '2212112k',
#         'Parent': [
#             {
#                 'Id': '212112410k',
#                 'Name': 'Inflammatory disorder (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410k',
#                 'Name': 'Chronic gout without tophus (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311k',
#                 'Name': 'Intense joint pain'
#             },
#             {
#                 'Id': '29865431312k',
#                 'Name': 'Irritation, swelling and redness'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313k',
#                 'Name': 'Joint fluid test'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314k',
#                 'Name': 'Medicine that helps lessen the swelling'
#             },
#             {
#                 'Id': '29865431315k',
#                 'Name': 'Medicine that prevent gout complications by lowering uric acid in the blood'
#             }
#         ]
#     },
#     'Acute sinusitis': {
#         'Id': '2212112L',
#         'Parent': [
#             {
#                 'Id': '212112410L',
#                 'Name': 'Acute inflammatory disease (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410L',
#                 'Name': 'Acute bacterial sinusitis (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311L',
#                 'Name': 'Ear pressure'
#             },
#             {
#                 'Id': '29865431312L',
#                 'Name': 'Aching in the teeth'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313L',
#                 'Name': 'Nasal endoscopy'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314L',
#                 'Name': 'Saline nasal spray'
#             },
#             {
#                 'Id': '29865431315L',
#                 'Name': 'Nasal corticosteroids'
#             }
#         ]
#     },
#     'Gingivitis': {
#         'Id': '2212112m',
#         'Parent': [
#             {
#                 'Id': '212112410m',
#                 'Name': 'Gingival disease (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410m',
#                 'Name': 'Acute gingivitis (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311m',
#                 'Name': 'Swollen or puffy gums'
#             },
#             {
#                 'Id': '29865431312m',
#                 'Name': 'Bad breath'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313m',
#                 'Name': 'Measuring intraocular pressure, also called tonometry'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314m',
#                 'Name': 'Review of your dental and medical history'
#             },
#             {
#                 'Id': '29865431315m',
#                 'Name': 'Looking at your teeth, gums, mouth and tongue'
#             }
#         ]
#     },
#     'Haemorrhoids': {
#         'Id': '2212112n',
#         'Parent': [
#             {
#                 'Id': '212112410n',
#                 'Name': 'Disorder of anal canal (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410n',
#                 'Name': 'Bleeding hemorrhoids (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311n',
#                 'Name': 'Painless bleeding'
#             },
#             {
#                 'Id': '29865431312n',
#                 'Name': 'Itching or irritation in the anal area'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313n',
#                 'Name': 'Digital exam'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314n',
#                 'Name': 'Eat high-fiber foods'
#             },
#             {
#                 'Id': '29865431315n',
#                 'Name': 'Use topical treatments'
#             }
#         ]
#     },
#     'Constipation': {
#         'Id': '2212112o',
#         'Parent': [
#             {
#                 'Id': '212112410o',
#                 'Name': 'Disorder of anal canal (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410o',
#                 'Name': 'Bleeding hemorrhoids (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311o',
#                 'Name': 'Fewer than three stools a week'
#             },
#             {
#                 'Id': '29865431312o',
#                 'Name': 'Hard, dry or lumpy stools'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313o',
#                 'Name': 'Look at the tissue of the anus and the surrounding skin'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314o',
#                 'Name': 'Eat a high-fiber diet'
#             },
#             {
#                 'Id': '29865431315o',
#                 'Name': 'Exercise most days of the week'
#             }
#         ]
#     },
#     'Diarrhea': {
#         'Id': '2212112p',
#         'Parent': [
#             {
#                 'Id': '212112410p',
#                 'Name': 'Disorder of anal canal (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410p',
#                 'Name': 'Bleeding hemorrhoids (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311p',
#                 'Name': 'Belly cramps or pain'
#             },
#             {
#                 'Id': '29865431312p',
#                 'Name': 'Vomiting'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313p',
#                 'Name': 'Flexible sigmoidoscopy or colonoscopy'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314p',
#                 'Name': 'Antibiotics or anti-parasitics'
#             }
#         ]
#     },
#     'Gallstones': {
#         'Id': '2212112q',
#         'Parent': [
#             {
#                 'Id': '212112410q',
#                 'Name': 'Calculus in biliary tract (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410q',
#                 'Name': 'Calculus of gallbladder with cholecystitis (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311q',
#                 'Name': 'Sudden and rapidly intensifying pain in the upper right portion of your abdomen'
#             },
#             {
#                 'Id': '29865431312q',
#                 'Name': 'Back pain between your shoulder blades'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313q',
#                 'Name': 'Abdominal ultrasound'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314q',
#                 'Name': 'Surgery to remove the gallbladder'
#             },
#             {
#                 'Id': '29865431315q',
#                 'Name': 'Medications to dissolve gallstones'
#             }
#         ]
#     },
#     'Endometriosis': {
#         'Id': '2212112r',
#         'Parent': [
#             {
#                 'Id': '212112410r',
#                 'Name': 'Calculus in biliary tract (disorder)'
#             }
#         ],
#         'Children': [
#             {
#                 'Id': '212112410r',
#                 'Name': 'Calculus of gallbladder with cholecystitis (disorder)'
#             }
#         ],
#         'Symptoms': [
#             {
#                 'Id': '29865431311r',
#                 'Name': 'Painful periods'
#             },
#             {
#                 'Id': '29865431312r',
#                 'Name': 'Pain with sex'
#             }
#         ],
#         'Diagnosis': [
#             {
#                 'Id': '29865431313r',
#                 'Name': 'Pelvic exam'
#             }
#         ],
#         'Treatment': [
#             {
#                 'Id': '29865431314r',
#                 'Name': 'Pain medicines'
#             },
#             {
#                 'Id': '29865431315r',
#                 'Name': 'Hormone therapy'
#             }
#         ]
#     }
# }

DomainOntology = {
    'Asthma': {
        'Id': 'A1',
        'Parent': [
            {
                'Id': '21215431311A',
                'Name': 'Disorder of respiratory system'
            }
        ],
        'Children': [
            {
                'Id': '21256751312A',
                'Name': 'Asthma in pregnancy'
            },
            {
                'Id': '29865431313A',
                'Name': 'Childhood asthma'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S1',
                'Name': 'Shortness of breath'
            },
            {
                'Id': 'S2',
                'Name': 'Chest tightness'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D1',
                'Name': 'Methacholine challenge'
            },
            {
                'Id': 'D2',
                'Name': 'Imaging tests'
            }
        ],
        'Treatment': [
            {
                'Id': 'T1',
                'Name': 'Inhaled corticosteroids'
            },
            {
                'Id': 'T2',
                'Name': 'Leukotriene modifiers'
            }
        ]
    },
    'AnalWarts': {
        'Id': 'A2',
        'Parent': [
            {
                'Id': '212112410B',
                'Name': 'Anal Infection'
            }
        ],
        'Children': [],
        'Symptoms': [
            {
                'Id': 'S3',
                'Name': 'Bleeding with sex'
            },
            {
                'Id': 'S4',
                'Name': 'A cauliflower-like shape caused by a few warts close together'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D3',
                'Name': 'Pap tests'
            }
        ],
        'Treatment': [
            {
                'Id': 'T3',
                'Name': 'Imiquimod'
            },
            {
                'Id': 'T4',
                'Name': 'Trichloroacetic acid'
            }
        ]
    },
    'Heart block': {
        'Id': 'A3',
        'Parent': [
            {
                'Id': '212112410a',
                'Name': 'Conduction disorder of the heart'
            }
        ],
        'Children': [
            {
                'Id': '212112411a',
                'Name': 'Atrioventricular block'
            },
            {
                'Id': '212112412a',
                'Name': 'Heart block caused by drug'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S5',
                'Name': 'fainting (syncope)'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D4',
                'Name': 'Electrocardiogram (ECG or EKG)'
            }
        ],
        'Treatment': [
            {
                'Id': 'T5',
                'Name': 'medications to reduce high blood pressure or reduce symptoms of heart failure'
            }
        ]
    },
    'Pneumonia': {
        'Id': 'A4',
        'Parent': [
            {
                'Id': '212112410b',
                'Name': 'Infectious disease of lung (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410b',
                'Name': ' Abscess of lung with pneumonia (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S6',
                'Name': 'Chest pain when you breathe or cough'
            },
            {
                'Id': 'S7',
                'Name': 'Fever, sweating and shaking chills'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D5',
                'Name': 'Blood tests'
            }
        ],
        'Treatment': [
            {
                'Id': 'T6',
                'Name': 'Antibiotics'
            },
            {
                'Id': 'T7',
                'Name': 'Cough medicine'
            }
        ]
    },
    'Bronchitis': {
        'Id': 'A5',
        'Parent': [
            {
                'Id': '212182410c',
                'Name': 'Inflammation of specific body organs'
            }
        ],
        'Children': [
            {
                'Id': '212112410c',
                'Name': 'Acute bronchitis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S8',
                'Name': 'Sore throat'
            },
            {
                'Id': 'S9',
                'Name': 'Slight fever and chills'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D6',
                'Name': 'Chest X-ray'
            }
        ],
        'Treatment': [
            {
                'Id': 'T8',
                'Name': 'Cough medicine'
            },
            {
                'Id': 'T9',
                'Name': 'Antibiotics'
            }
        ]
    },
    'Tuberculosis': {
        'Id': 'A6',
        'Parent': [
            {
                'Id': '212112410d',
                'Name': 'Disorder characterized by granuloma formation (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112411d',
                'Name': 'Acute tuberculous ulcer (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S10',
                'Name': 'Low fever'
            },
            {
                'Id': 'S11',
                'Name': 'Tiredness'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D7',
                'Name': 'Listening to breathe with a stethoscope'
            }
        ],
        'Treatment': [
            {
                'Id': 'T10',
                'Name': 'Isoniazid'
            },
            {
                'Id': 'T11',
                'Name': 'Rifampin'
            }
        ]
    },
    'Gastritis': {
        'Id': 'A7',
        'Parent': [
            {
                'Id': '212112410e',
                'Name': 'Disorder of stomach (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '2121124111e',
                'Name': 'Acute gastritis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S12',
                'Name': 'Vomiting'
            },
            {
                'Id': 'S13',
                'Name': 'Nausea'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D8',
                'Name': 'Tests for H. pylori'
            }
        ],
        'Treatment': [
            {
                'Id': 'T12',
                'Name': 'Antibiotics to kill H. pylori'
            },
            {
                'Id': 'T13',
                'Name': 'Medicines that block acid production and promote healing'
            }
        ]
    },
    'Hepatitis A': {
        'Id': 'A8',
        'Parent': [
            {
                'Id': '212112410f',
                'Name': 'Viral hepatitis (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410f',
                'Name': 'Acute type A viral hepatitis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S14',
                'Name': 'Unusual tiredness and weakness'
            },
            {
                'Id': 'S39',
                'Name': 'Sudden nausea and vomiting and diarrhea'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D9',
                'Name': 'Blood tests are used to look for signs of the hepatitis A virus'
            }
        ],
        'Treatment': [
            {
                'Id': 'T14',
                'Name': 'Get adequate food and liquid'
            },
            {
                'Id': 'T15',
                'Name': 'Avoid alcohol and use medications with care'
            }
        ]
    },
    'Cataracts': {
        'Id': 'A9',
        'Parent': [
            {
                'Id': '212112410j',
                'Name': 'Degenerative disorder of bilateral eyes (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410j',
                'Name': 'Anterior subcapsular polar cataract of bilateral eyes (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S15',
                'Name': 'Clouded, blurred or dim vision'
            },
            {
                'Id': 'S16',
                'Name': 'Need for brighter light for reading and other activities'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D10',
                'Name': 'Vision test'
            }
        ],
        'Treatment': [
            {
                'Id': 'T16',
                'Name': 'surgery'
            }
        ]
    },
    'Anaemia': {
        'Id': 'A10',
        'Parent': [
            {
                'Id': '212112410g',
                'Name': 'Disorder of cellular component of blood (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410g',
                'Name': 'Acquired Heinz body anemia (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S17',
                'Name': 'Shortness of breath'
            },
            {
                'Id': 'S18',
                'Name': 'Irregular heartbeat'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D11',
                'Name': 'Complete blood count, also called CBC'
            }
        ],
        'Treatment': [
            {
                'Id': 'T17',
                'Name': 'Iron deficiency anemia'
            },
            {
                'Id': 'T18',
                'Name': 'Anemia of chronic disease'
            }
        ]
    },
    'Depression': {
        'Id': 'A11',
        'Parent': [
            {
                'Id': '212112410h',
                'Name': 'Mood disorder (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410h',
                'Name': 'Acute depression (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S19',
                'Name': 'Feelings of sadness, tearfulness, emptiness or hopelessness'
            },
            {
                'Id': 'S20',
                'Name': 'Angry outbursts, irritability or frustration, even over small matters'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D12',
                'Name': 'Blood tests are used to look for signs of the hepatitis A virus'
            }
        ],
        'Treatment': [
            {
                'Id': 'T19',
                'Name': 'Anxious distress'
            },
            {
                'Id': 'T20',
                'Name': 'Melancholic features'
            }
        ]
    },
    'Glaucoma': {
        'Id': 'A12',
        'Parent': [
            {
                'Id': '212112410i',
                'Name': 'Disorder of eye proper (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410i',
                'Name': 'Absolute glaucoma (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S21',
                'Name': 'In later stages, difficulty seeing things in your central vision'
            },
            {
                'Id': 'S22',
                'Name': 'Gradually, patchy blind spots in your side vision. Side vision also is called peripheral vision'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D13',
                'Name': 'Measuring intraocular pressure, also called tonometry'
            }
        ],
        'Treatment': [
            {
                'Id': 'T21',
                'Name': 'Get adequate food and liquid'
            },
            {
                'Id': 'T22',
                'Name': 'Checking for areas of vision loss, also known as a visual field test'
            }
        ]
    },
    'Gout': {
        'Id': 'A13',
        'Parent': [
            {
                'Id': '212112410k',
                'Name': 'Inflammatory disorder (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410k',
                'Name': 'Chronic gout without tophus (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S23',
                'Name': 'Intense joint pain'
            },
            {
                'Id': 'S24',
                'Name': 'Irritation, swelling and redness'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D14',
                'Name': 'Joint fluid test'
            }
        ],
        'Treatment': [
            {
                'Id': 'T23',
                'Name': 'Medicine that helps lessen the swelling'
            },
            {
                'Id': 'T24',
                'Name': 'Medicine that prevent gout complications by lowering uric acid in the blood'
            }
        ]
    },
    'Acute sinusitis': {
        'Id': 'A14',
        'Parent': [
            {
                'Id': '212112410L',
                'Name': 'Acute inflammatory disease (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410L',
                'Name': 'Acute bacterial sinusitis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S25',
                'Name': 'Ear pressure'
            },
            {
                'Id': 'S26',
                'Name': 'Aching in the teeth'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D15',
                'Name': 'Nasal endoscopy'
            }
        ],
        'Treatment': [
            {
                'Id': 'T25',
                'Name': 'Saline nasal spray'
            },
            {
                'Id': 'T26',
                'Name': 'Nasal corticosteroids'
            }
        ]
    },
    'Gingivitis': {
        'Id': 'A15',
        'Parent': [
            {
                'Id': '212112410m',
                'Name': 'Gingival disease (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410m',
                'Name': 'Acute gingivitis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S27',
                'Name': 'Swollen or puffy gums'
            },
            {
                'Id': 'S28',
                'Name': 'Bad breath'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D16',
                'Name': 'Measuring intraocular pressure, also called tonometry'
            }
        ],
        'Treatment': [
            {
                'Id': 'T27',
                'Name': 'Review of your dental and medical history'
            },
            {
                'Id': 'T28',
                'Name': 'Looking at your teeth, gums, mouth and tongue'
            }
        ]
    },
    'Haemorrhoids': {
        'Id': 'A16',
        'Parent': [
            {
                'Id': '212112410n',
                'Name': 'Disorder of anal canal (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410n',
                'Name': 'Bleeding hemorrhoids (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S29',
                'Name': 'Painless bleeding'
            },
            {
                'Id': 'S30',
                'Name': 'Itching or irritation in the anal area'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D17',
                'Name': 'Digital exam'
            }
        ],
        'Treatment': [
            {
                'Id': 'T29',
                'Name': 'Eat high-fiber foods'
            },
            {
                'Id': 'T30',
                'Name': 'Use topical treatments'
            }
        ]
    },
    'Constipation': {
        'Id': 'A17',
        'Parent': [
            {
                'Id': '212112410o',
                'Name': 'Disorder of anal canal (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410o',
                'Name': 'Bleeding hemorrhoids (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S31',
                'Name': 'Fewer than three stools a week'
            },
            {
                'Id': 'S32',
                'Name': 'Hard, dry or lumpy stools'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D18',
                'Name': 'Look at the tissue of the anus and the surrounding skin'
            }
        ],
        'Treatment': [
            {
                'Id': 'T31',
                'Name': 'Eat a high-fiber diet'
            },
            {
                'Id': 'T32',
                'Name': 'Exercise most days of the week'
            }
        ]
    },
    'Diarrhea': {
        'Id': 'A18',
        'Parent': [
            {
                'Id': '212112410p',
                'Name': 'Disorder of anal canal (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410p',
                'Name': 'Bleeding hemorrhoids (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S33',
                'Name': 'Belly cramps or pain'
            },
            {
                'Id': 'S34',
                'Name': 'Vomiting'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D19',
                'Name': 'Flexible sigmoidoscopy or colonoscopy'
            }
        ],
        'Treatment': [
            {
                'Id': 'T33',
                'Name': 'Antibiotics or anti-parasitics'
            }
        ]
    },
    'Gallstones': {
        'Id': 'A19',
        'Parent': [
            {
                'Id': '212112410q',
                'Name': 'Calculus in biliary tract (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410q',
                'Name': 'Calculus of gallbladder with cholecystitis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S35',
                'Name': 'Sudden and rapidly intensifying pain in the upper right portion of your abdomen'
            },
            {
                'Id': 'S36',
                'Name': 'Back pain between your shoulder blades'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D20',
                'Name': 'Abdominal ultrasound'
            }
        ],
        'Treatment': [
            {
                'Id': 'T34',
                'Name': 'Surgery to remove the gallbladder'
            },
            {
                'Id': 'T35',
                'Name': 'Medications to dissolve gallstones'
            }
        ]
    },
    'Endometriosis': {
        'Id': 'A20',
        'Parent': [
            {
                'Id': '212112410r',
                'Name': 'Calculus in biliary tract (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410r',
                'Name': 'Calculus of gallbladder with cholecystitis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S37',
                'Name': 'Painful periods'
            },
            {
                'Id': 'S38',
                'Name': 'Pain with sex'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D21',
                'Name': 'Pelvic exam'
            }
        ],
        'Treatment': [
            {
                'Id': 'T36',
                'Name': 'Pain medicines'
            },
            {
                'Id': 'T37',
                'Name': 'Hormone therapy'
            }
        ]
    }
}


def consumptionContextGenerator(db):
    csc = {}
    ##-----------------------------------context--------------------------------------##
    timeStamp = time.time()
    context = {
        'timeStamp' : timeStamp
    }
    ##----------------------------------agent ascertain---------------------------------##
    agentPublicKeys = {}
    for i in range(1, 4):
        with open("../asymKeys/public_{0}.pem".format(i), 'rb') as f:  ##obtain the saved public key
            publicKey = serialization.load_pem_public_key(f.read())
            agentPublicKeys['agent{0}'.format(i)] = publicKey


    ##-----------------------------------query-------------------------------------##
    ##query comes in here
    query = ('We would like to obtain the dialogue between Doctor and his Patient. '
             'The patient believes that he has experienced fainting'
             'and Electrocardiogram has been used for diagnosis.')

    csc['context'] = context
    # csc['leashTicket'] = leashTicket
    csc['agents'] = agentPublicKeys
    csc['query'] = query

    return csc



if __name__ == '__main__':
    ##-----------------------------database activation---------------------------##
    client = MongoClient('localhost', 27017)  ## save the encrypted text into database
    db = client['encryptedData']
    collection = db['data']



    ##-----------------------------------------conception context obtaining---------------------------------##
    csc = consumptionContextGenerator(db)
    print('this is the consumption context: ', csc, '\n')




    ##------------------------------------------Query Decoding------------------------------------##
    ontologyPointers = []

    kbModel = KeyBERT()
    keywords = kbModel.extract_keywords(
        csc['query'],
        stop_words='english',
        use_mmr=True  ## exclude those similar words
    )
    print('keywords: ', keywords)
    keywordsNum = len(keywords)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    sentences = []
    for i in range(len(keywords)):
        sentences.append(keywords[i][0])

    ontologies = ['Heart block']
    for i in ontologies:
        nodesNum  = 0
        sen = copy.deepcopy(sentences)
        for j in DomainOntology[i].items():
            if(j[0] != 'Id') and (j[0] != 'Parent') and (j[0] != 'Children'):
                for k in j[1]:
                    sen.append(k['Name'])
                    nodesNum += 1


        print('those are the sentences:', sen, '\n')
        embedding = model.encode(sen)
        relevanceResult = model.similarity(embedding, embedding)
        print('The relevance result: ', relevanceResult, '\n')


        ##---------------------------------locating the ontology with the highest relevance-------------------------------------------##
        posi = (0, 0)  ##find the most relevant Domain Ontology with for loop
        value = 0
        for m in range(0, keywordsNum):
            for n in range(keywordsNum, keywordsNum + nodesNum):
                if relevanceResult[m][n] > value:
                    value = relevanceResult[m][n]
                    posi = [m, n]
        print(posi)
        print(relevanceResult[posi[0]][posi[1]])
        print(sen[posi[1]])


        print(DomainOntology[i]['Id'])
        pointer = {}
        found = 0
        for j in DomainOntology[i].items():
            if (j[0] != 'Id') and (j[0] != 'Parent') and (j[0] != 'Children'):
                for k in j[1]:
                    if k['Name'] == sen[posi[1]]:
                        pointer[DomainOntology[i]['Id']] = k['Id']
                        found = 1
                        break
            if found:
                break

        ontologyPointers.append(pointer)

    print(ontologyPointers)


    # ##-------------------------------------hookstack construction-------------------------------------------##
    # hookStack = {'stack': []}
    #
    # for i in range(len(keywords)):
    #     temp = 0 ##the most similar ontology
    #     posi = [] ## the position of the most similar ontology
    #     for j in range(len(keywords), relevanceResult.shape[1]):
    #         if(relevanceResult[i, j] > temp):
    #             temp = relevanceResult[i, j]
    #             posi = [i, j]
    #     print(temp)
    #     print(posi)
    #
    #     hookStack['stack'].append({'segment1': i + 1, 'keyword': keywords[i][0], 'mostSimilarOnto': 'DomainOnto{0}'.format(posi[1] - len(keywords) + 1)})
    #
    # print(hookStack)



    ##------------------------------------obtain candidates-----------------------------------##
    candidates = []
    candidatesPosi = []
    index = 1
    for i in ontologyPointers:
        for item in collection.find():
            if 'Wrapper' in item:
                for j in item['Wrapper']['Ontology Pointers']:
                    if (list(j.keys())[0] == list(i.keys())[0]) and (list(j.values())[0] == list(i.values())[0]) and (item['_id'] not in candidates):
                        candidates.append(item['_id'])
                        candidatesPosi.append(index)
                index += 1

    print('Those are the candidates: ', candidates)



    #-----------------------------------Access Check------------------------------------##
    #-----------------------------------Access tokens-------------------------------------##
    WAM = np.zeros((len(csc['agents']), len(candidates)))
    RAM = np.zeros((len(csc['agents']), len(candidates)))
    # print('\n', WAM, '\n\n', RAM, '\n\n')

    agentNo = 1
    for i in csc['agents'].items():
        print('This is the agent: ', i[0])
        print('This is his public key: ', i[1])
        publicKeyBytes = i[1].public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        hashedPublicKey = hashlib.sha256(publicKeyBytes).hexdigest()
        print('This is his hashed public key: ', hashedPublicKey)

        atomNo = 1
        for j in candidates:
            atom = db['data'].find_one({'_id': j})
            # print('This is the atom: ', atom['Wrapper']['Access Tokens'])
            isWriteAccess = 0

            ##--------------------------------check if this agent's public key matches one of the tokens in the wrapper-----------------------------------##
            for item in atom['Wrapper']['Access Tokens'].items():
                isWriteAccess = isWriteAccess + 1
                # print('\nThis is the hashed public key: ', item[0])
                if (hashedPublicKey == item[0] and isWriteAccess == 1):
                    WAM[agentNo - 1, atomNo - 1] = 1
                    break
                elif hashedPublicKey == item[0] and isWriteAccess != 1:
                    RAM[agentNo - 1, atomNo - 1] = 1
                    break


            atomNo += 1

        agentNo += 1

    print('\n\nThis is the WAM: \n', WAM, '\n\n', 'This is the RAM: \n', RAM)

    #---------------------------------------------BM generation---------------------------------------##
    BM = np.zeros((len(csc['agents']), len(candidates)))
    for i in range(WAM.shape[0]):
        for j in range(WAM.shape[1]):
            if(WAM[i, j] == 1 or RAM[i, j] == 1):
                BM[i, j] = 1

    print('\nThis is the BM: \n', BM)



    ##-----------------------------atom filtering-----------------------------------##
    acceptedAtoms = []
    for i in range(BM.shape[1]):
        isAccepted = True
        for j in range(BM.shape[0]):
            if BM[j, i] == 0:
                isAccepted = False
        if isAccepted:
            acceptedAtoms.append(candidates[i])  ##BM's column represents all the candidates.

    print('Those are accepted atoms: ', acceptedAtoms)
    print('Those are their positions in MongoDB: ', candidatesPosi)



    # ##------------------------------------Atom Decryption-------------------------------------##
    # for item in accessDescription.items():
    #     print('Now we are processing: ', item[0], item[0][-3])
    #     with open("../asymKeys/private_{0}.pem".format(item[0][-3]), 'rb') as f:  ##obtain the saved public key
    #         privateKey = serialization.load_pem_private_key(f.read(), password = None)
    #     with open("../asymKeys/public_{0}.pem".format(item[0][-3]), 'rb') as f:  ##obtain the saved public key
    #         publicKey = serialization.load_pem_public_key(f.read())
    #     publicKeyBytes = publicKey.public_bytes(
    #         encoding=serialization.Encoding.PEM,
    #         format=serialization.PublicFormat.SubjectPublicKeyInfo)
    #     hashedPublicKey = hashlib.sha256(publicKeyBytes).hexdigest()
    #
    #
    #     ##----------------------------decrypt every atom that this agent has access to-----------------------------------##
    #     for atomId in item[1]:
    #         atom = db['data'].find_one({"_id": ObjectId(atomId)})
    #
    #
    #         ##------------------------looping to find the token for this agent, so that we can get his encrypted Symmetric Key--------------------##
    #         for j in atom['Wrapper']['Access Tokens'].items():
    #             if (hashedPublicKey == j[0]):
    #                 print('This is the hashed public key: ', j[0])
    #                 symmetricKey = privateKey.decrypt(
    #                     j[1],
    #                     padding.OAEP(
    #                         mgf=padding.MGF1(algorithm=hashes.SHA256()),
    #                         algorithm=hashes.SHA256(),
    #                         label=None
    #                     )
    #                 )
    #
    #                 fernet = Fernet(symmetricKey)
    #                 data = fernet.decrypt(atom['Nucleus']['encryptedData'])
    #                 print('This is the encrypted data in the atom: ', data, '\n')
    #                 break






