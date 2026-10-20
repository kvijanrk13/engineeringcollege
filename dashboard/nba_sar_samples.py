"""Real filed NBA Self-Assessment Reports (e-SAR), split criterion by criterion.

Each source is a complete, filled e-SAR printed from the e-NBA portal and
published on the institute's own website. The PDFs under ``static/nba-sar`` are
those filed reports split at the criterion boundaries printed in the report
itself, so a reader can see exactly how a real institution answered one
criterion: the tables it filled, the evidence it attached and the marks it
claimed.

``NBA_SAR_SAMPLES`` maps a tier to the list of filed samples available for it.
The list order is the order the samples are rendered under each criterion, so
the richest, longest-running example comes first.
"""

BIT_MESRA = {
    'institution': 'Birla Institute of Technology, Mesra',
    'location': 'Ranchi, Jharkhand',
    'programme': 'B.Tech. Mechanical Engineering',
    'tier_label': 'Tier I · autonomous institute',
    'short_tier': 'Tier I',
    'year': '2026',
    'format': 'GAPC V4.0 SAR format (July 2024), filed for the 2026 cycle',
    'pages': 240,
    'scope': 'Complete criterion sections split from the filed e-SAR',
    'source_url': 'https://bitmesra.ac.in/UploadedDocuments/adminmech/files/NBA-2026/UG%20MECH%20SAR%202026.pdf',
    'source_label': 'bitmesra.ac.in · NBA 2026 · UG Mechanical SAR',
    'note': 'A 1955-founded autonomous institute that has held NBA accreditation for its UG programmes. Read its criterion 1 for the vision, mission and PEO derivation with the stakeholder flowchart, criterion 3 for the full CO–PO attainment computation and criterion 9 for the institute-level support and governance narrative.',
    'criteria': {
        1: {'pdf': 'nba-sar/tier1/criterion-1.pdf', 'preview': 'nba-sar/tier1/criterion-1.jpg', 'pages': 41, 'source_pages': '14-54'},
        2: {'pdf': 'nba-sar/tier1/criterion-2.pdf', 'preview': 'nba-sar/tier1/criterion-2.jpg', 'pages': 20, 'source_pages': '56-75'},
        3: {'pdf': 'nba-sar/tier1/criterion-3.pdf', 'preview': 'nba-sar/tier1/criterion-3.jpg', 'pages': 34, 'source_pages': '76-109'},
        4: {'pdf': 'nba-sar/tier1/criterion-4.pdf', 'preview': 'nba-sar/tier1/criterion-4.jpg', 'pages': 13, 'source_pages': '112-124'},
        5: {'pdf': 'nba-sar/tier1/criterion-5.pdf', 'preview': 'nba-sar/tier1/criterion-5.jpg', 'pages': 8, 'source_pages': '127-134'},
        6: {'pdf': 'nba-sar/tier1/criterion-6.pdf', 'preview': 'nba-sar/tier1/criterion-6.jpg', 'pages': 14, 'source_pages': '135-148'},
        7: {'pdf': 'nba-sar/tier1/criterion-7.pdf', 'preview': 'nba-sar/tier1/criterion-7.jpg', 'pages': 12, 'source_pages': '149-160'},
        8: {'pdf': 'nba-sar/tier1/criterion-8.pdf', 'preview': 'nba-sar/tier1/criterion-8.jpg', 'pages': 25, 'source_pages': '161-185'},
        9: {'pdf': 'nba-sar/tier1/criterion-9.pdf', 'preview': 'nba-sar/tier1/criterion-9.jpg', 'pages': 52, 'source_pages': '188-239'},
    },
}

ANURAG = {
    'institution': 'Anurag Engineering College',
    'location': 'Ananthagiri (V & M), Kodad, Suryapet, Telangana – 508206',
    'programme': 'B.Tech. Computer Science and Engineering',
    'tier_label': 'Tier I · autonomous institute',
    'short_tier': 'Tier I',
    'year': '2026',
    'format': 'GAPC V4.0 SAR format, Tier I cycle 1, submitted 30 January 2026',
    'pages': 271,
    'scope': 'Complete criterion sections split from the filed e-SAR',
    'source_url': 'https://enba.nbaind.org/SARTemplates/eSARUGTierICycle1V1Print.aspx?Appid=11458&Progid=558',
    'source_label': 'enba.nbaind.org · App 11458 · UG CSE e-SAR',
    'note': 'An autonomous institute accredited by NBA since 2009, filing the current Tier I format for a 180-seat CSE programme. Its criterion 5 shows the faculty cadre and student-faculty ratio workings for a self-financing college, criterion 8 records the continuous-improvement actions taken on the previous evaluation round, and the institute also publishes the e-NBA data-capture report for both CSE and ECE.',
    'criteria': {
        1: {'pdf': 'nba-sar/tier1/anurag/criterion-1.pdf', 'preview': 'nba-sar/tier1/anurag/criterion-1.jpg', 'pages': 31, 'source_pages': '8-38'},
        2: {'pdf': 'nba-sar/tier1/anurag/criterion-2.pdf', 'preview': 'nba-sar/tier1/anurag/criterion-2.jpg', 'pages': 53, 'source_pages': '38-90'},
        3: {'pdf': 'nba-sar/tier1/anurag/criterion-3.pdf', 'preview': 'nba-sar/tier1/anurag/criterion-3.jpg', 'pages': 44, 'source_pages': '90-133'},
        4: {'pdf': 'nba-sar/tier1/anurag/criterion-4.pdf', 'preview': 'nba-sar/tier1/anurag/criterion-4.jpg', 'pages': 12, 'source_pages': '133-144'},
        5: {'pdf': 'nba-sar/tier1/anurag/criterion-5.pdf', 'preview': 'nba-sar/tier1/anurag/criterion-5.jpg', 'pages': 11, 'source_pages': '144-154'},
        6: {'pdf': 'nba-sar/tier1/anurag/criterion-6.pdf', 'preview': 'nba-sar/tier1/anurag/criterion-6.jpg', 'pages': 17, 'source_pages': '154-170'},
        7: {'pdf': 'nba-sar/tier1/anurag/criterion-7.pdf', 'preview': 'nba-sar/tier1/anurag/criterion-7.jpg', 'pages': 7, 'source_pages': '170-176'},
        8: {'pdf': 'nba-sar/tier1/anurag/criterion-8.pdf', 'preview': 'nba-sar/tier1/anurag/criterion-8.jpg', 'pages': 64, 'source_pages': '176-239'},
        9: {'pdf': 'nba-sar/tier1/anurag/criterion-9.pdf', 'preview': 'nba-sar/tier1/anurag/criterion-9.jpg', 'pages': 33, 'source_pages': '239-271'},
    },
}

BCREC = {
    'institution': 'Dr. B.C. Roy Engineering College',
    'location': 'Durgapur, West Bengal',
    'programme': 'B.Tech. Computer Science and Engineering',
    'tier_label': 'Tier II · affiliated institution',
    'short_tier': 'Tier II',
    'year': '2026',
    'format': 'GAPC V4.0 SAR format (January 2025), filed 19 June 2026',
    'pages': 394,
    'scope': 'Opening pages of each criterion section from the filed e-SAR',
    'source_url': 'https://www.bcrec.ac.in/public/pdf/e-NBA_SAR_CSE2026.pdf',
    'source_label': 'bcrec.ac.in · e-NBA SAR CSE 2026',
    'note': 'A non-autonomous affiliated college filing the current Tier II format. Compare it with the Tier I sample: the criterion headings and the evidence tables are the same, but the curriculum is university-prescribed, so the curriculum and teaching-learning answers are thinner and the output-focused criteria carry more of the answer.',
    'criteria': {
        1: {'pdf': 'nba-sar/tier2/criterion-1.pdf', 'preview': 'nba-sar/tier2/criterion-1.jpg', 'pages': 8, 'source_pages': '7-44'},
        2: {'pdf': 'nba-sar/tier2/criterion-2.pdf', 'preview': 'nba-sar/tier2/criterion-2.jpg', 'pages': 8, 'source_pages': '45-187'},
        3: {'pdf': 'nba-sar/tier2/criterion-3.pdf', 'preview': 'nba-sar/tier2/criterion-3.jpg', 'pages': 8, 'source_pages': '188-231'},
        4: {'pdf': 'nba-sar/tier2/criterion-4.pdf', 'preview': 'nba-sar/tier2/criterion-4.jpg', 'pages': 8, 'source_pages': '232-252'},
        5: {'pdf': 'nba-sar/tier2/criterion-5.pdf', 'preview': 'nba-sar/tier2/criterion-5.jpg', 'pages': 8, 'source_pages': '253-266'},
        6: {'pdf': 'nba-sar/tier2/criterion-6.pdf', 'preview': 'nba-sar/tier2/criterion-6.jpg', 'pages': 8, 'source_pages': '267-284'},
        7: {'pdf': 'nba-sar/tier2/criterion-7.pdf', 'preview': 'nba-sar/tier2/criterion-7.jpg', 'pages': 4, 'source_pages': '285-288'},
        8: {'pdf': 'nba-sar/tier2/criterion-8.pdf', 'preview': 'nba-sar/tier2/criterion-8.jpg', 'pages': 8, 'source_pages': '289-304'},
        9: {'pdf': 'nba-sar/tier2/criterion-9.pdf', 'preview': 'nba-sar/tier2/criterion-9.jpg', 'pages': 8, 'source_pages': '305-393'},
    },
}

NBA_SAR_SAMPLES = {
    'tier1': [BIT_MESRA, ANURAG],
    'tier2': [BCREC],
}
