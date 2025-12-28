from django.shortcuts import render, redirect
from django.contrib import messages
import json

# =========================================================
# FULL SYLLABUS DATA
# =========================================================

SYLLABUS_DATA = {
    "IT": {
        "1-1": [
            {"code": "MA101BS", "name": "MATRICES AND CALCULUS"},
            {"code": "AP102BS", "name": "APPLIED PHYSICS"},
            {"code": "CS103ES", "name": "PROGRAMMING FOR PROBLEM SOLVING"},
            {"code": "EN104HS", "name": "ENGLISH FOR SKILL ENHANCEMENT"},
            {"code": "ME105ES", "name": "ENGINEERING WORKSHOP"},
            {"code": "CS106ES", "name": "ELEMENTS OF COMPUTER SCIENCE & ENGINEERING"},
            {"code": "AP107BS", "name": "APPLIED PHYSICS LABORATORY"},
            {"code": "EN108HS", "name": "ENGLISH LANGUAGE AND COMMUNICATION SKILLS LABORATORY"},
            {"code": "CS109ES", "name": "PROGRAMMING FOR PROBLEM SOLVING LABORATORY"},
            {"code": "ES110MC", "name": "ENVIRONMENTAL SCIENCE"},
        ],
        "1-2": [
            {"code": "MA201BS", "name": "ORDINARY DIFFERENTIAL EQUATIONS AND VECTOR CALCULUS"},
            {"code": "CH202BS", "name": "ENGINEERING CHEMISTRY"},
            {"code": "EG203ES", "name": "COMPUTER AIDED ENGINEERING GRAPHICS"},
            {"code": "EE204ES", "name": "BASIC ELECTRICAL ENGINEERING"},
            {"code": "EC205ES", "name": "ELECTRONIC DEVICES AND CIRCUITS"},
            {"code": "CH206BS", "name": "ENGINEERING CHEMISTRY LABORATORY"},
            {"code": "CS207ES", "name": "PYTHON PROGRAMMING LABORATORY"},
            {"code": "EE208ES", "name": "BASIC ELECTRICAL ENGINEERING LABORATORY"},
            {"code": "CS209ES", "name": "IT WORKSHOP"},
            {"code": "HS210MC", "name": "CONSTITUTION OF INDIA"},
        ],
        "2-1": [
            {"code": "PS301BS", "name": "PROBABILITY AND STATISTICS"},
            {"code": "EC302ES", "name": "DIGITAL ELECTRONICS"},
            {"code": "CS303PC", "name": "DATA STRUCTURES"},
            {"code": "CM304PC", "name": "COMPUTER ORGANIZATION AND MICROPROCESSOR"},
            {"code": "IT305PC", "name": "INTRODUCTION TO IOT"},
            {"code": "CS306PC", "name": "DATA STRUCTURES LABORATORY"},
            {"code": "EC307ES", "name": "DIGITAL ELECTRONICS LABORATORY"},
            {"code": "IT308PC", "name": "INTERNET OF THINGS LABORATORY"},
            {"code": "HS309MC", "name": "GENDER SENSITIZATION"},
            {"code": "CS308PC", "name": "SKILL DEVELOPMENT COURSE(DATA VISUALIZATION-R PROGRAMMING / POWER BI)"},
        ],
        "2-2": [
            {"code": "MB401HS", "name": "BUSINESS ECONOMICS & FINANCIAL ANALYSIS"},
            {"code": "CS402PC", "name": "DISCRETE MATHEMATICS"},
            {"code": "CS403PC", "name": "OPERATING SYSTEMS"},
            {"code": "CS404PC", "name": "DATABASE MANAGEMENT SYSTEMS"},
            {"code": "IT405PC", "name": "JAVA PROGRAMMING"},
            {"code": "CS406PC", "name": "OPERATING SYSTEMS LABORATORY"},
            {"code": "CS407PC", "name": "DATABASE MANAGEMENT SYSTEMS LABORATORY"},
            {"code": "IT408PC", "name": "JAVA PROGRAMMING LABORATORY"},
            {"code": "IT409PW", "name": "REAL-TIME RESEARCH PROJECT/ SOCIETAL RELATED PROJECT"},
            {"code": "IT410PC", "name": "SKILL DEVELOPMENT COURSE (NODE JS/REACTJS/DJANGO)"},
            {"code": "HS411MC", "name": "INTELLECTUAL PROPERTY RIGHTS"},
        ],
        "3-1": [
            {"code": "CS501PC", "name": "DESIGN AND ANALYSIS OF ALGORITHMS"},
            {"code": "IT502PC", "name": "AUTOMATA AND COMPILER DESIGN"},
            {"code": "IT503PC", "name": "EMBEDDED SYSTEMS"},
            {"code": "IT511PE", "name": "FULL STACK DEVELOPMENT"},
            {"code": "IT512PE", "name": "DATA MINING"},
            {"code": "CS513PE", "name": "SCRIPTING LANGUAGES"},
            {"code": "IT514PE", "name": "MOBILE APPLICATION DEVELOPMENT"},
            {"code": "IT515PE", "name": "SOFTWARE TESTING METHODOLOGIES"},
            {"code": "AM515PE", "name": "COMPUTER GRAPHICS"},
            {"code": "IT522PE", "name": "QUANTUM COMPUTING"},
            {"code": "IT523PE", "name": "ADVANCED OPERATING SYSTEMS"},
            {"code": "CS524PE", "name": "DISTRIBUTED DATABASES"},
            {"code": "IT525PE", "name": "PATTERN RECOGNITION"},
            {"code": "IT532PE", "name": "DATA MINING LABORATORY"},
            {"code": "IT531PE", "name": "FULL STACK DEVELOPMENT LABORATORY"},
            {"code": "IT533PE", "name": "SCRIPTING LANGUAGES LABORATORY"},
            {"code": "IT534PE", "name": "MOBILE APPLICATION DEVELOPMENT LABORATORY"},
            {"code": "IT535PE", "name": "SOFTWARE TESTING METHODOLOGIES LABORATORY"},
            {"code": "IT504PC", "name": "COMPILER DESIGN LABORATORY"},
            {"code": "IT505PC", "name": "EMBEDDED SYSTEMS LABORATORY"},
            {"code": "CS507PC", "name": "SKILL DEVELOPMENT COURSE(UI DESIGN FLUTTER)"},
        ],
        "3-2": [
            {"code": "CS601PC", "name": "MACHINE LEARNING"},
            {"code": "IT602PC", "name": "SOFTWARE ENGINEERING"},
            {"code": "IT603PC", "name": "DATA COMMUNICATIONS AND COMPUTER NETWORKS"},
            {"code": "IT611PE", "name": "BIOMETRICS"},
            {"code": "IT612PE", "name": "ADVANCED COMPUTER ARCHITECTURE"},
            {"code": "CS633PE", "name": "DATA ANALYTICS"},
            {"code": "CS616PE", "name": "IMAGE PROCESSING"},
            {"code": "CS617PE", "name": "PRINCIPLES OF PROGRAMMING LANGUAGES"},
            {"code": "CE611OE", "name": "DISASTER PREPAREDNESS & PLANNING MANAGEMENT"},
            {"code": "CE612OE", "name": "BUILDING MANAGEMENT SYSTEMS"},
            {"code": "CE613OE", "name": "ENVIRONMENTAL IMPACT ASSESSMENT"},
            {"code": "CE614OE", "name": "HYDROGEOLOGY"},
            {"code": "EE611OE", "name": "RENEWABLE ENERGY SOURCES"},
            {"code": "EE612OE", "name": "FUNDAMENTAL OF ELECTRIC VEHICLES"},
            {"code": "ME611OE", "name": "BASIC MECHANICAL ENGINEERING"},
            {"code": "ME612OE", "name": "POWER PLANT ENGINEERING"},
            {"code": "EC611OE", "name": "FUNDAMENTALS OF INTERNET OF THINGS"},
            {"code": "EC612OE", "name": "PRINCIPLES OF SIGNAL PROCESSING"},
            {"code": "EC613OE", "name": "DIGITAL ELECTRONICS FOR ENGINEERING"},
            {"code": "CS611OE", "name": "DATA STRUCTURES"},
            {"code": "CS612OE", "name": "DATABASE MANAGEMENT SYSTEMS"},
            {"code": "IT611OE", "name": "JAVA PROGRAMMING"},
            {"code": "IT612OE", "name": "SOFTWARE ENGINEERING"},
            {"code": "AM611OE", "name": "FUNDAMENTALS OF AI"},
            {"code": "AM612OE", "name": "MACHINE LEARNING BASICS"},
            {"code": "CS604PC", "name": "MACHINE LEARNING LABORATORY"},
            {"code": "IT605PC", "name": "SOFTWARE ENGINEERING & COMPUTER NETWORKS LABORATORY"},
            {"code": "AE606HS", "name": "ADVANCED ENGLISH COMMUNICATION SKILLS LABORATORY"},
            {"code": "CS606PW",
             "name": "INDUSTRIAL ORIENTED MINI PROJECT/ INTERNSHIP/ SKILL DEVELOPMENT COURSE (BIG DATASPARK)"},
            {"code": "ES607MC", "name": "ENVIRONMENTAL SCIENCE"},
        ],
        "4-1": [
            {"code": "IT701PC", "name": "INFORMATION SECURITY"},
            {"code": "IT702PC", "name": "CLOUD COMPUTING"},
            {"code": "IT711PE", "name": "HUMAN COMPUTER INTERACTION"},
            {"code": "IT712PE", "name": "HIGH PERFORMANCE COMPUTING"},
            {"code": "IT713PE", "name": "ARTIFICIAL INTELLIGENCE"},
            {"code": "IT714PE", "name": "INFORMATION RETRIEVAL SYSTEMS"},
            {"code": "IT715PE", "name": "AD-HOC & SENSOR NETWORKS"},
            {"code": "IT721PE", "name": "NATURAL LANGUAGE PROCESSING"},
            {"code": "IT722PE", "name": "DISTRIBUTED SYSTEMS"},
            {"code": "IT723PE", "name": "AUGMENTED REALITY & VIRTUAL REALITY"},
            {"code": "IT724PE", "name": "WEB SECURITY"},
            {"code": "IT725PE", "name": "CYBER FORENSICS"},
            {"code": "CE721OE", "name": "REMOTE SENSING & GEOGRAPHICAL INFORMATION SYSTEMS"},
            {"code": "CE722OE", "name": "SUSTAINABLE INFRASTRUCTURE DEVELOPMENT"},
            {"code": "CE723OE", "name": "SOLID WASTE MANAGEMENT"},
            {"code": "CE724OE", "name": "SMART CITIES"},
            {"code": "EE721OE", "name": "UTILIZATION OF ELECTRIC ENERGY"},
            {"code": "EE722OE", "name": "ENERGY STORAGE SYSTEMS"},
            {"code": "ME721OE", "name": "QUANTITATIVE ANALYSIS FOR BUSINESS DECISIONS"},
            {"code": "ME722OE", "name": "INDUSTRIAL ENGINEERING & MANAGEMENT"},
            {"code": "EC721OE", "name": "ELECTRONIC SENSORS"},
            {"code": "EC722OE", "name": "ELECTRONICS FOR HEALTH CARE"},
            {"code": "EC723OE", "name": "TELECOMMUNICATIONS FOR SOCIETY"},
            {"code": "CS721OE", "name": "OPERATING SYSTEMS"},
            {"code": "CS722OE", "name": "COMPUTER NETWORKS"},
            {"code": "IT721OE", "name": "FULL STACK DEVELOPMENT"},
            {"code": "IT722OE", "name": "SCRIPTING LANGUAGES"},
            {"code": "AM721OE", "name": "INTRODUCTION TO NATURAL LANGUAGE PROCESSING"},
            {"code": "AM722OE", "name": "AI APPLICATIONS"},
            {"code": "IT703PC", "name": "INFORMATION SECURITY LAB"},
            {"code": "IT704PC", "name": "CLOUD COMPUTING LAB"},
            {"code": "IT705PC", "name": "PROJECT STAGE -- I"},
        ],
        "4-2": [
            {"code": "IT801PC", "name": "ORGANIZATIONAL BEHAVIOR"},
            {"code": "IT811PE", "name": "INTRUSION DETECTION SYSTEMS"},
            {"code": "IT812PE", "name": "REAL TIME SYSTEMS"},
            {"code": "IT813PE", "name": "BLOCK CHAIN TECHNOLOGY"},
            {"code": "IT814PE", "name": "DEEP LEARNING"},
            {"code": "IT815PE", "name": "SOFTWARE PROCESS& PROJECT MANAGEMENT"},
            {"code": "CE831OE", "name": "ENERGY EFFICIENT BUILDINGS"},
            {"code": "CE832OE", "name": "MULTI CRITERION DECISION MAKING"},
            {"code": "CE833OE", "name": "ENVIRONMENTAL POLLUTION"},
            {"code": "EE831OE", "name": "CHARGING INFRASTRUCTURE FOR ELECTRIC VEHICLES"},
            {"code": "EE832OE", "name": "RELIABILITY ENGINEERING"},
            {"code": "ME831OE", "name": "ELEMENTS OF ELECTRIC AND HYBRID VEHICLES"},
            {"code": "ME832OE", "name": "ENTREPRENEURSHIP DEVELOPMENT"},
            {"code": "EC831OE", "name": "MEASURING INSTRUMENTS"},
            {"code": "EC832OE", "name": "COMMUNICATION TECHNOLOGIES"},
            {"code": "EC833OE", "name": "FUNDAMENTALS OF SOCIAL NETWORKS"},
            {"code": "CS831OE", "name": "DESIGN AND ANALYSIS OF ALGORITHMS"},
            {"code": "CS832OE", "name": "DATA ANALYTICS"},
            {"code": "IT831OE", "name": "BIG DATA TECHNOLOGIES"},
            {"code": "IT832OE", "name": "DEVOPS"},
            {"code": "AM831OE", "name": "CHATBOTS"},
            {"code": "AM832OE", "name": "EVOLUTIONARY COMPUTING"},
            {"code": "IT802PC", "name": "PROJECT STAGE-II, INCLUDING SEMINAR"},
        ],
    },

    "CSE": {
        "1-1": [
            {"code": "MA101BS", "name": "MATRICES AND CALCULUS"},
            {"code": "CH102BS", "name": "ENGINEERING CHEMISTRY"},
            {"code": "CS103ES", "name": "PROGRAMMING FOR PROBLEM SOLVING"},
            {"code": "EE104ES", "name": "BASIC ELECTRICAL ENGINEERING"},
            {"code": "EG105ES", "name": "COMPUTER AIDED ENGINEERING GRAPHICS"},
            {"code": "CS106ES", "name": "ELEMENTS OF COMPUTER SCIENCE & ENGINEERING"},
            {"code": "CH107BS", "name": "ENGINEERING CHEMISTRY LABORATORY"},
            {"code": "CS109ES", "name": "PROGRAMMING FOR PROBLEM SOLVING LABORATORY"},
            {"code": "EE108ES", "name": "BASIC ELECTRICAL ENGINEERING LABORATORY"},
            {"code": "HS110MC", "name": "CONSTITUTION OF INDIA"},
        ],
        "1-2": [
            {"code": "MA201BS", "name": "ORDINARY DIFFERENTIAL EQUATIONS AND VECTOR CALCULUS"},
            {"code": "AP202BS", "name": "APPLIED PHYSICS"},
            {"code": "ME203ES", "name": "ENGINEERING WORKSHOP"},
            {"code": "EN204HS", "name": "ENGLISH FOR SKILL ENHANCEMENT"},
            {"code": "EC205ES", "name": "ELECTRONIC DEVICES AND CIRCUIT"},
            {"code": "AP206BS", "name": "APPLIED PHYSICS LABORATORY"},
            {"code": "CS207ES", "name": "PYTHON PROGRAMMING LABORATORY"},
            {"code": "EN208HS", "name": "ENGLISH LANGUAGE AND COMMUNICATION SKILLS LABORATORY"},
            {"code": "CS209ES", "name": "IT WORKSHOP"},
            {"code": "ES210MC", "name": "ENVIRONMENTAL SCIENCE"},
        ],
        "2-1": [
            {"code": "PS301BS", "name": "PROBABILITY AND STATISTICS"},
            {"code": "DE302ES", "name": "DIGITAL ELECTRONICS"},
            {"code": "CS303PC", "name": "DATA STRUCTURES"},
            {"code": "CS304PC", "name": "COMPUTER ORGANIZATION AND ARCHITECTURE"},
            {"code": "CS305PC", "name": "OBJECT ORIENTED PROGRAMMING THROUGH JAVA"},
            {"code": "CS306PC", "name": "DATA STRUCTURES LABORATORY"},
            {"code": "CS307PC", "name": "OBJECT ORIENTED PROGRAMMING THROUGH JAVA LABORATORY"},
            {"code": "HS309MC", "name": "GENDER SENSITIZATION"},
            {"code": "CS308PC", "name": "SKILL DEVELOPMENT COURSE(DATA VISUALIZATION-R PROGRAMMING / POWER BI)"},
        ],
        "2-2": [
            {"code": "MB401HS", "name": "BUSINESS ECONOMICS & FINANCIAL ANALYSIS"},
            {"code": "CS402PC", "name": "DISCRETE MATHEMATICS"},
            {"code": "CS403PC", "name": "OPERATING SYSTEMS"},
            {"code": "CS404PC", "name": "DATABASE MANAGEMENT SYSTEMS"},
            {"code": "CS405PC", "name": "COMPUTER NETWORKS"},
            {"code": "CS406PC", "name": "OPERATING SYSTEMS LABORATORY"},
            {"code": "CS407PC", "name": "DATABASE MANAGEMENT SYSTEMS LABORATORY"},
            {"code": "CS408PC", "name": "COMPUTER NETWORKS LABORATORY"},
            {"code": "CS409PW", "name": "REAL-TIME RESEARCH PROJECT/ SOCIETAL RELATED PROJECT"},
            {"code": "CS410PC", "name": "SKILL DEVELOPMENT COURSE (NODE JS/REACTJS/DJANGO)"},
            {"code": "HS411MC", "name": "INTELLECTUAL PROPERTY RIGHTS"},
        ],
        "3-1": [
            {"code": "CS501PC", "name": "DESIGN AND ANALYSIS OF ALGORITHMS"},
            {"code": "CS502PC", "name": "COMPUTER NETWORKS"},
            {"code": "CS503PC", "name": "DEVOPS"},
            {"code": "CS511PE", "name": "QUANTUM COMPUTING"},
            {"code": "CS512PE", "name": "ADVANCED COMPUTER ARCHITECTURE"},
            {"code": "CS513PE", "name": "SCRIPTING LANGUAGES"},
            {"code": "CS514PE", "name": "IMAGE PROCESSING"},
            {"code": "CS515PE", "name": "PRINCIPLES OF PROGRAMMING LANGUAGES"},
            {"code": "CS521PE", "name": "COMPUTER GRAPHICS"},
            {"code": "CS522PE", "name": "EMBEDDED SYSTEM"},
            {"code": "CS523PE", "name": "INFORMATION RETRIEVAL SYSTEMS"},
            {"code": "CS524PE", "name": "DISTRIBUTED DATABASES"},
            {"code": "CS525PE", "name": "NATURAL LANGUAGE PROCESSING"},
            {"code": "CS504PC", "name": "COMPUTER NETWORKS LABORATORY"},
            {"code": "CS505PC", "name": "DEVOPS LABORATORY"},
            {"code": "AE506HS", "name": "ADVANCED ENGLISH COMMUNICATION SKILLS LABORATORY"},
            {"code": "CS507PC", "name": "SKILL DEVELOPMENT COURSE(UI DESIGN FLUTTER)"},
        ],
        "3-2": [
            {"code": "CS601PC", "name": "MACHINE LEARNING"},
            {"code": "CS602PC", "name": "FORMAL LANGUAGES AND AUTOMATA THEORY"},
            {"code": "CS603PC", "name": "ARTIFICIAL INTELLIGENCE"},
            {"code": "CS631PE", "name": "FULL STACK DEVELOPMENT"},
            {"code": "CS632PE", "name": "INTERNET OF THINGS"},
            {"code": "CS633PE", "name": "DATA ANALYTICS"},
            {"code": "CS634PE", "name": "MOBILE APPLICATION DEVELOPMENT"},
            {"code": "CS635PE", "name": "SOFTWARE TESTING METHODOLOGIES"},
            {"code": "CE611OE", "name": "DISASTER PREPAREDNESS & PLANNING MANAGEMENT"},
            {"code": "CE612OE", "name": "BUILDING MANAGEMENT SYSTEMS"},
            {"code": "CE613OE", "name": "ENVIRONMENTAL IMPACT ASSESSMENT"},
            {"code": "CE614OE", "name": "HYDROGEOLOGY"},
            {"code": "EE611OE", "name": "RENEWABLE ENERGY SOURCES"},
            {"code": "EE612OE", "name": "FUNDAMENTAL OF ELECTRIC VEHICLES"},
            {"code": "ME611OE", "name": "BASIC MECHANICAL ENGINEERING"},
            {"code": "ME612OE", "name": "POWER PLANT ENGINEERING"},
            {"code": "EC611OE", "name": "FUNDAMENTALS OF INTERNET OF THINGS"},
            {"code": "EC612OE", "name": "PRINCIPLES OF SIGNAL PROCESSING"},
            {"code": "EC613OE", "name": "DIGITAL ELECTRONICS FOR ENGINEERING"},
            {"code": "CS611OE", "name": "DATA STRUCTURES"},
            {"code": "CS612OE", "name": "DATABASE MANAGEMENT SYSTEMS"},
            {"code": "IT611OE", "name": "JAVA PROGRAMMING"},
            {"code": "IT612OE", "name": "SOFTWARE ENGINEERING"},
            {"code": "AM611OE", "name": "FUNDAMENTALS OF AI"},
            {"code": "AM612OE", "name": "MACHINE LEARNING BASICS"},
            {"code": "CS604PC", "name": "MACHINE LEARNING LABORATORY"},
            {"code": "CS605PC", "name": "ARTIFICIAL INTELLIGENCE LABORATORY"},
            {"code": "CS641PC", "name": "FULL STACK DEVELOPMENT LAB"},
            {"code": "CS642PC", "name": "INTERNET OF THINGS LAB"},
            {"code": "CS643PC", "name": "DATA ANALYTICS LAB"},
            {"code": "CS644PC", "name": "MOBILE APPLICATION DEVELOPMENT LAB"},
            {"code": "CS645PC", "name": "SOFTWARE TESTING METHODOLOGIES LAB"},
            {"code": "CS606PW",
             "name": "INDUSTRIAL ORIENTED MINI PROJECT/ INTERNSHIP/ SKILL DEVELOPMENT COURSE (BIG DATASPARK)"},
            {"code": "ES607MC", "name": "ENVIRONMENTAL SCIENCE"},
        ],
        "4-1": [
            {"code": "CS701PC", "name": "CRYPTOGRAPHY AND NETWORK SECURITY"},
            {"code": "CS702PC", "name": "COMPILER DESIGN"},
            {"code": "CS741PE", "name": "DATA ANALYTICS FOR IOT"},
            {"code": "CS742PE", "name": "CLOUD COMPUTING"},
            {"code": "CS743PE", "name": "GRAPH THEORY"},
            {"code": "CS744PE", "name": "CYBER SECURITY"},
            {"code": "CS745PE", "name": "SOFT COMPUTING"},
            {"code": "CS746PE", "name": "AD HOC & SENSOR NETWORKS"},
            {"code": "CS751PE", "name": "AGILE METHODOLOGY"},
            {"code": "CS752PE", "name": "IOT ARCHITECTURES AND PROTOCOLS"},
            {"code": "CS753PE", "name": "BIG DATA ANALYTICS"},
            {"code": "CS754PE", "name": "ADVANCED ALGORITHMS"},
            {"code": "CS755PE", "name": "DEEP LEARNING"},
            {"code": "CS756PE", "name": "REINFORCEMENT LEARNING"},
            {"code": "CS757PE", "name": "SOFTWARE PROCESS & PROJECT MANAGEMENT"},
            {"code": "CE721OE", "name": "REMOTE SENSING & GEOGRAPHICAL INFORMATION SYSTEMS"},
            {"code": "CE722OE", "name": "SUSTAINABLE INFRASTRUCTURE DEVELOPMENT"},
            {"code": "CE723OE", "name": "SOLID WASTE MANAGEMENT"},
            {"code": "CE724OE", "name": "SMART CITIES"},
            {"code": "EE721OE", "name": "UTILIZATION OF ELECTRIC ENERGY"},
            {"code": "EE722OE", "name": "ENERGY STORAGE SYSTEMS"},
            {"code": "ME721OE", "name": "QUANTITATIVE ANALYSIS FOR BUSINESS DECISIONS"},
            {"code": "ME722OE", "name": "INDUSTRIAL ENGINEERING & MANAGEMENT"},
            {"code": "EC721OE", "name": "ELECTRONIC SENSORS"},
            {"code": "EC722OE", "name": "ELECTRONICS FOR HEALTH CARE"},
            {"code": "EC723OE", "name": "TELECOMMUNICATIONS FOR SOCIETY"},
            {"code": "CS721OE", "name": "OPERATING SYSTEMS"},
            {"code": "CS722OE", "name": "COMPUTER NETWORKS"},
            {"code": "IT721OE", "name": "FULL STACK DEVELOPMENT"},
            {"code": "IT722OE", "name": "SCRIPTING LANGUAGES"},
            {"code": "AM721OE", "name": "INTRODUCTION TO NATURAL LANGUAGE PROCESSING"},
            {"code": "AM722OE", "name": "AI APPLICATIONS"},
            {"code": "CS703PC", "name": "CRYPTOGRAPHY AND NETWORK SECURITY LABORATORY"},
            {"code": "CS704PC", "name": "COMPILER DESIGN LABORATORY"},
            {"code": "CS705PW", "name": "PROJECT STAGE -- I"},
        ],
        "4-2": [
            {"code": "MB801BS", "name": "ORGANIZATIONAL BEHAVIOR"},
            {"code": "CS861PE", "name": "INDUSTRIAL IOT"},
            {"code": "CS862PE", "name": "COMPUTER VISION"},
            {"code": "CS863PE", "name": "COMPUTATIONAL COMPLEXITY"},
            {"code": "CS864PE", "name": "DISTRIBUTED SYSTEMS"},
            {"code": "CS865PE", "name": "BLOCKCHAIN TECHNOLOGY"},
            {"code": "CS866PE", "name": "HUMAN COMPUTER INTERACTION"},
            {"code": "CS867PE", "name": "CYBER FORENSICS"},
            {"code": "CS868PE", "name": "QUALITY ASSURANCE AND TESTING"},
            {"code": "CE831OE", "name": "ENERGY EFFICIENT BUILDINGS"},
            {"code": "CE832OE", "name": "MULTI CRITERION DECISION MAKING"},
            {"code": "CE833OE", "name": "ENVIRONMENTAL POLLUTION"},
            {"code": "EE831OE", "name": "CHARGING INFRASTRUCTURE FOR ELECTRIC VEHICLES"},
            {"code": "EE832OE", "name": "RELIABILITY ENGINEERING"},
            {"code": "ME831OE", "name": "ELEMENTS OF ELECTRIC AND HYBRID VEHICLES"},
            {"code": "ME832OE", "name": "ENTREPRENEURSHIP DEVELOPMENT"},
            {"code": "EC831OE", "name": "MEASURING INSTRUMENTS"},
            {"code": "EC832OE", "name": "COMMUNICATION TECHNOLOGIES"},
            {"code": "EC833OE", "name": "FUNDAMENTALS OF SOCIAL NETWORKS"},
            {"code": "CS831OE", "name": "DESIGN AND ANALYSIS OF ALGORITHMS"},
            {"code": "CS832OE", "name": "DATA ANALYTICS"},
            {"code": "IT831OE", "name": "BIG DATA TECHNOLOGIES"},
            {"code": "IT832OE", "name": "DEVOPS"},
            {"code": "AM831OE", "name": "CHATBOTS"},
            {"code": "AM832OE", "name": "EVOLUTIONARY COMPUTING"},
            {"code": "CS802PW", "name": "PROJECT STAGE-II ,INCLUDING SEMINAR"},
        ],
    },

    "AIML": {
        "1-1": [
            {"code": "MA101BS", "name": "MATRICES AND CALCULUS"},
            {"code": "CH102BS", "name": "ENGINEERING CHEMISTRY"},
            {"code": "CS103ES", "name": "PROGRAMMING FOR PROBLEM SOLVING"},
            {"code": "EE104ES", "name": "BASIC ELECTRICAL ENGINEERING"},
            {"code": "EG105ES", "name": "COMPUTER AIDED ENGINEERING GRAPHICS"},
            {"code": "CS106ES", "name": "ELEMENTS OF COMPUTER SCIENCE & ENGINEERING"},
            {"code": "CH107BS", "name": "ENGINEERING CHEMISTRY LABORATORY"},
            {"code": "CS109ES", "name": "PROGRAMMING FOR PROBLEM SOLVING LABORATORY"},
            {"code": "EE108ES", "name": "BASIC ELECTRICAL ENGINEERING LABORATORY"},
            {"code": "HS110MC", "name": "CONSTITUTION OF INDIA"},
        ],
        "1-2": [
            {"code": "MA201BS", "name": "ORDINARY DIFFERENTIAL EQUATIONS AND VECTOR CALCULUS"},
            {"code": "AP202BS", "name": "APPLIED PHYSICS"},
            {"code": "ME203ES", "name": "ENGINEERING WORKSHOP"},
            {"code": "EN204HS", "name": "ENGLISH FOR SKILL ENHANCEMENT"},
            {"code": "EC205ES", "name": "ELECTRONIC DEVICES AND CIRCUIT"},
            {"code": "AP206BS", "name": "APPLIED PHYSICS LABORATORY"},
            {"code": "CS207ES", "name": "PYTHON PROGRAMMING LABORATORY"},
            {"code": "EN208HS", "name": "ENGLISH LANGUAGE AND COMMUNICATION SKILLS LABORATORY"},
            {"code": "CS209ES", "name": "IT WORKSHOP"},
            {"code": "ES210MC", "name": "ENVIRONMENTAL SCIENCE"},
        ],
        "2-1": [
            {"code": "PS301BS", "name": "PROBABILITY AND STATISTICS"},
            {"code": "CS303PC", "name": "DATA STRUCTURES"},
            {"code": "CS304PC", "name": "COMPUTER ORGANIZATION AND ARCHITECTURE"},
            {"code": "AM305PC", "name": "SOFTWARE ENGINEERING"},
            {"code": "AM306PC", "name": "OPERATING SYSTEMS"},
            {"code": "CS306PC", "name": "DATA STRUCTURES LABORATORY"},
            {"code": "AM307PC", "name": "OPERATING SYSTEMS LABORATORY"},
            {"code": "AM308PC", "name": "SOFTWARE ENGINEERING LABORATORY"},
            {"code": "HS309MC", "name": "GENDER SENSITIZATION"},
            {"code": "AM310PC", "name": "SKILL DEVELOPMENT COURSE (NODE JS/ REACT JS/ DJANGO)"},
        ],
        "2-2": [
            {"code": "MB401HS", "name": "BUSINESS ECONOMICS & FINANCIAL ANALYSIS"},
            {"code": "AM402PC", "name": "DISCRETE MATHEMATICS"},
            {"code": "CS403PC", "name": "OPERATING SYSTEMS"},
            {"code": "CS404PC", "name": "DATABASE MANAGEMENT SYSTEMS"},
            {"code": "AM405PC", "name": "JAVA PROGRAMMING"},
            {"code": "CS406PC", "name": "OPERATING SYSTEMS LABORATORY"},
            {"code": "CS407PC", "name": "DATABASE MANAGEMENT SYSTEMS LABORATORY"},
            {"code": "AM408PC", "name": "JAVA PROGRAMMING LABORATORY"},
            {"code": "AM409PW", "name": "REAL-TIME RESEARCH PROJECT/ SOCIETAL RELATED PROJECT"},
            {"code": "AM410PC", "name": "SKILL DEVELOPMENT COURSE (NODE JS/REACTJS/DJANGO)"},
            {"code": "HS411MC", "name": "INTELLECTUAL PROPERTY RIGHTS"},
        ],
        "3-1": [
            {"code": "CS501PC", "name": "DESIGN AND ANALYSIS OF ALGORITHMS"},
            {"code": "CS502PC", "name": "COMPUTER NETWORKS"},
            {"code": "AM503PC", "name": "MACHINE LEARNING"},
            {"code": "BF504HS", "name": "BUSINESS ECONOMICS & FINANCIAL ANALYSIS"},
            {"code": "AM511PE", "name": "GRAPH THEORY"},
            {"code": "AM512PE", "name": "INTRODUCTION TO DATA SCIENCE"},
            {"code": "AM513PE", "name": "WEB PROGRAMMING"},
            {"code": "EC514PE", "name": "IMAGE PROCESSING"},
            {"code": "AM515PE", "name": "COMPUTER GRAPHICS"},
            {"code": "AM505PC", "name": "MACHINE LEARNING LABORATORY"},
            {"code": "CS504PC", "name": "COMPUTER NETWORKS LABORATORY"},
            {"code": "CS507PC", "name": "SKILL DEVELOPMENT COURSE(UI DESIGN FLUTTER)"},
        ],
        "3-2": [
            {"code": "AM601PC", "name": "KNOWLEDGE REPRESENTATION AND REASONING"},
            {"code": "AM602PC", "name": "DATA ANALYTICS"},
            {"code": "AM603PC", "name": "NATURAL LANGUAGE PROCESSING"},
            {"code": "AM621PE", "name": "SOFTWARE TESTING METHODOLOGIES"},
            {"code": "AM622PE", "name": "INFORMATION RETRIEVAL SYSTEMS"},
            {"code": "AM623PE", "name": "PATTERN RECOGNITION"},
            {"code": "AM624PE", "name": "DISTRIBUTED COMPUTING"},
            {"code": "AM625PE", "name": "DATA WAREHOUSING AND BUSINESS INTELLIGENCE"},
            {"code": "CE611OE", "name": "DISASTER PREPAREDNESS & PLANNING MANAGEMENT"},
            {"code": "CE612OE", "name": "BUILDING MANAGEMENT SYSTEMS"},
            {"code": "CE613OE", "name": "ENVIRONMENTAL IMPACT ASSESSMENT"},
            {"code": "CE614OE", "name": "HYDROGEOLOGY"},
            {"code": "EE611OE", "name": "RENEWABLE ENERGY SOURCES"},
            {"code": "EE612OE", "name": "FUNDAMENTAL OF ELECTRIC VEHICLES"},
            {"code": "ME611OE", "name": "BASIC MECHANICAL ENGINEERING"},
            {"code": "ME612OE", "name": "POWER PLANT ENGINEERING"},
            {"code": "EC611OE", "name": "FUNDAMENTALS OF INTERNET OF THINGS"},
            {"code": "EC612OE", "name": "PRINCIPLES OF SIGNAL PROCESSING"},
            {"code": "EC613OE", "name": "DIGITAL ELECTRONICS FOR ENGINEERING"},
            {"code": "CS611OE", "name": "DATA STRUCTURES"},
            {"code": "CS612OE", "name": "DATABASE MANAGEMENT SYSTEMS"},
            {"code": "IT611OE", "name": "JAVA PROGRAMMING"},
            {"code": "IT612OE", "name": "SOFTWARE ENGINEERING"},
            {"code": "AM611OE", "name": "FUNDAMENTALS OF AI"},
            {"code": "AM612OE", "name": "MACHINE LEARNING BASICS"},
            {"code": "AM604PC", "name": "NATURAL LANGUAGE PROCESSING LABORATORY"},
            {"code": "AM605PC", "name": "DATA ANALYTICS LABORATORY"},
            {"code": "AE606HS", "name": "ADVANCED ENGLISH COMMUNICATION SKILLS LABORATORY"},
            {"code": "AM607PW", "name": "INDUSTRIAL ORIENTED MINI PROJECT/ INTERNSHIP"},
            {"code": "ES607MC", "name": "ENVIRONMENTAL SCIENCE"},
        ],
        "4-1": [
            {"code": "AM701PC", "name": "DEEP LEARNING"},
            {"code": "AM702PC", "name": "NATURE INSPIRED COMPUTING"},
            {"code": "AM731PE", "name": "INTERNET OF THINGS"},
            {"code": "AM732PE", "name": "DATA MINING"},
            {"code": "AM733PE", "name": "MERN STACK DEVELOPMENT"},
            {"code": "AM734PE", "name": "MOBILE APPLICATION DEVELOPMENT"},
            {"code": "AM735PE", "name": "CLOUD COMPUTING"},
            {"code": "AM711PE", "name": "INTERNET OF THINGS LABORATORY"},
            {"code": "AM712PE", "name": "DATA MINING LABORATORY"},
            {"code": "AM713PE", "name": "MERN STACK DEVELOPMENT LABORATORY"},
            {"code": "AM714PE", "name": "MOBILE APPLICATION DEVELOPMENT LABORATORY"},
            {"code": "AM715PE", "name": "CLOUD COMPUTING LABORATORY"},
            {"code": "AM741PE", "name": "QUANTUM COMPUTING"},
            {"code": "AM742PE", "name": "EXPERT SYSTEMS"},
            {"code": "AM743PE", "name": "SEMANTIC WEB"},
            {"code": "AM744PE", "name": "GAME THEORY"},
            {"code": "AM745PE", "name": "MOBILE COMPUTING"},
            {"code": "CE721OE", "name": "REMOTE SENSING & GEOGRAPHICAL INFORMATION SYSTEMS"},
            {"code": "CE722OE", "name": "SUSTAINABLE INFRASTRUCTURE DEVELOPMENT"},
            {"code": "CE723OE", "name": "SOLID WASTE MANAGEMENT"},
            {"code": "CE724OE", "name": "SMART CITIES"},
            {"code": "EE721OE", "name": "UTILIZATION OF ELECTRIC ENERGY"},
            {"code": "EE722OE", "name": "ENERGY STORAGE SYSTEMS"},
            {"code": "ME721OE", "name": "QUANTITATIVE ANALYSIS FOR BUSINESS DECISIONS"},
            {"code": "ME722OE", "name": "INDUSTRIAL ENGINEERING & MANAGEMENT"},
            {"code": "EC721OE", "name": "ELECTRONIC SENSORS"},
            {"code": "EC722OE", "name": "ELECTRONICS FOR HEALTH CARE"},
            {"code": "EC723OE", "name": "TELECOMMUNICATIONS FOR SOCIETY"},
            {"code": "CS721OE", "name": "OPERATING SYSTEMS"},
            {"code": "CS722OE", "name": "COMPUTER NETWORKS"},
            {"code": "IT721OE", "name": "FULL STACK DEVELOPMENT"},
            {"code": "IT722OE", "name": "SCRIPTING LANGUAGES"},
            {"code": "AM721OE", "name": "INTRODUCTION TO NATURAL LANGUAGE PROCESSING"},
            {"code": "AM722OE", "name": "AI APPLICATIONS"},
            {"code": "AM703PC", "name": "PROFESSIONAL PRACTICE, LAW & ETHICS"},
            {"code": "AM704PC", "name": "PROJECT STAGE -- I"},
        ],
        "4-2": [
            {"code": "AM851PE", "name": "SOCIAL MEDIA ANALYTICS"},
            {"code": "AM852PE", "name": "FEDERATED MACHINE LEARNING"},
            {"code": "AM853PE", "name": "AUGMENTED REALITY & VIRTUAL REALITY"},
            {"code": "AM854PE", "name": "CYBER SECURITY"},
            {"code": "AM855PE", "name": "AD-HOC & SENSOR NETWORKS"},
            {"code": "AM861PE", "name": "SPEECH AND VIDEO PROCESSING"},
            {"code": "AM862PE", "name": "REINFORCEMENT LEARNING"},
            {"code": "AM863PE", "name": "RANDOMIZED ALGORITHMS"},
            {"code": "AM864PE", "name": "COGNITIVE COMPUTING"},
            {"code": "AM865PE", "name": "CONVERSATIONAL AI"},
            {"code": "CE831OE", "name": "ENERGY EFFICIENT BUILDINGS"},
            {"code": "CE832OE", "name": "MULTI CRITERION DECISION MAKING"},
            {"code": "CE833OE", "name": "ENVIRONMENTAL POLLUTION"},
            {"code": "EE831OE", "name": "CHARGING INFRASTRUCTURE FOR ELECTRIC VEHICLES"},
            {"code": "EE832OE", "name": "RELIABILITY ENGINEERING"},
            {"code": "ME831OE", "name": "ELEMENTS OF ELECTRIC AND HYBRID VEHICLES"},
            {"code": "ME832OE", "name": "ENTREPRENEURSHIP DEVELOPMENT"},
            {"code": "EC831OE", "name": "MEASURING INSTRUMENTS"},
            {"code": "EC832OE", "name": "COMMUNICATION TECHNOLOGIES"},
            {"code": "EC833OE", "name": "FUNDAMENTALS OF SOCIAL NETWORKS"},
            {"code": "CS831OE", "name": "DESIGN AND ANALYSIS OF ALGORITHMS"},
            {"code": "CS832OE", "name": "DATA ANALYTICS"},
            {"code": "IT831OE", "name": "BIG DATA TECHNOLOGIES"},
            {"code": "IT832OE", "name": "DEVOPS"},
            {"code": "AM831OE", "name": "CHATBOTS"},
            {"code": "AM832OE", "name": "EVOLUTIONARY COMPUTING"},
            {"code": "AM801PC", "name": "PROJECT STAGE-II INCLUDING SEMINAR"},
        ],
    },
}

SEM_ORDER = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]


def build_comparison():
    """
    Return a list like:
    [
      {"sem": "1-1", "rows": [ {name, IT, CSE, AIML, common_count}, ... ]},
      ...
    ]
    This avoids any dict indexing in the template.
    """
    comparison_by_sem = []

    for sem in SEM_ORDER:
        mapping = {}
        for dept in ["IT", "CSE", "AIML"]:
            for subj in SYLLABUS_DATA.get(dept, {}).get(sem, []):
                key = subj["name"].strip().upper()
                if key not in mapping:
                    mapping[key] = {
                        "name": subj["name"],
                        "IT": None,
                        "CSE": None,
                        "AIML": None,
                    }
                mapping[key][dept] = {"code": subj["code"], "name": subj["name"]}

        rows = []
        for item in mapping.values():
            count = sum(1 for d in ["IT", "CSE", "AIML"] if item[d] is not None)
            item["common_count"] = count
            rows.append(item)

        rows.sort(key=lambda x: (-x["common_count"], x["name"]))
        comparison_by_sem.append({"sem": sem, "rows": rows})

    return comparison_by_sem


# ================= BASIC VIEWS =================

def index(request):
    return render(request, "dashboard/index.html")


def dashboard(request):
    return render(request, "dashboard/dashboard.html")


def about(request):
    return render(request, "dashboard/about.html")


def faculty(request):
    # Get IT subjects from SYLLABUS_DATA
    it_subjects = {}
    for sem in SEM_ORDER:
        if sem in SYLLABUS_DATA.get("IT", {}):
            it_subjects[sem] = SYLLABUS_DATA["IT"][sem]
        else:
            it_subjects[sem] = []  # Empty list for semesters without data

    # Create a simplified structure for template
    years = {
        "1": {"name": "First Year", "semesters": ["1-1", "1-2"]},
        "2": {"name": "Second Year", "semesters": ["2-1", "2-2"]},
        "3": {"name": "Third Year", "semesters": ["3-1", "3-2"]},
        "4": {"name": "Fourth Year", "semesters": ["4-1", "4-2"]},
    }

    # Prepare subjects by semester for JavaScript
    subjects_by_semester = {}
    for sem, subjects in it_subjects.items():
        subjects_by_semester[sem] = subjects

    context = {
        "it_subjects": it_subjects,
        "subjects_by_semester": subjects_by_semester,
        "years": years,
        "sem_order": SEM_ORDER,
    }
    return render(request, "dashboard/faculty.html", context)


def students(request):
    return render(request, "dashboard/students.html")


def library(request):
    return render(request, "dashboard/library.html")


def exambranch(request):
    return render(request, "dashboard/exambranch.html")


def gallery(request):
    return render(request, "dashboard/gallery.html")


# ================= LOGIN =================

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        if username == "7001" and password == "anrkitdept":
            request.session["logged_in"] = True
            request.session["username"] = username
            messages.success(request, "Login successful")
            return redirect("dashboard:syllabus")
        messages.error(request, "Invalid credentials")
    return render(request, "dashboard/login.html")


def logout_view(request):
    request.session.flush()
    return redirect("dashboard:login")


# ================= SYLLABUS VIEW =================

def syllabus(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")

    context = {
        "syllabus": SYLLABUS_DATA,
        "comparison_by_sem": build_comparison(),
    }
    return render(request, "dashboard/syllabus.html", context)


# ================= ERROR HANDLERS =================

def handler404(request, exception):
    return render(request, "dashboard/404.html", status=404)


def handler500(request):
    return render(request, "dashboard/500.html", status=500)