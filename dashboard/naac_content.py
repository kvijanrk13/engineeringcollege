"""NAAC institutional accreditation criteria reference (Revised Accreditation Framework).

NAAC assesses an institution against seven criteria. The criterion weightage is
not the same for every kind of higher education institution, so the guide is
organised the way NAAC itself organises the framework: one tab per unit of
assessment (university, autonomous college, affiliated college), each with the
seven criteria, the key indicators under every criterion and the weightage
that applies to that category.

Sources: NAAC Manual for Autonomous Colleges (Revised Accreditation Framework,
w.e.f. 1 February 2023), the NAAC "Assessment & Accreditation" page (criteria
and weightage, grading, cycles, outcome) and the "Info for institutions" page
(IQAC composition and functions, AQAR timeline).
"""

NAAC_HEI_TYPES = {
    'autonomous': {
        'label': 'Autonomous colleges (UG) — this institution’s category',
        'manual': 'NAAC Manual for Autonomous Colleges — Revised Accreditation Framework, w.e.f. 1 February 2023',
        'format': 'SSR format: 7 criteria · 34 key indicators · 85 metrics (35 qualitative + 50 quantitative) · 1,000 weighted marks',
        'eligibility': 'UGC-autonomous colleges affiliated to a UGC-recognised university, with at least two graduated batches or six years of existence, whichever is earlier. Autonomous colleges carry curricular responsibilities similar to universities, so the curriculum and research criteria carry most of the weight.',
        'total': 1000,
        'ki_weightage': True,
        'weightage': {1: 150, 2: 300, 3: 150, 4: 100, 5: 100, 6: 100, 7: 100},
    },
    'university': {
        'label': 'Universities (central, state, private, deemed)',
        'manual': 'NAAC Manual for Universities — Revised Accreditation Framework, w.e.f. 1 February 2023',
        'format': 'SSR format: 7 criteria · 34 key indicators · 85 metrics (35 qualitative + 50 quantitative) · 1,000 weighted marks',
        'eligibility': 'Universities approved by MHRD/UGC, institutions of national importance and their on-campus units. NAAC does not accredit offshore campuses or distance education units.',
        'total': 1000,
        'ki_weightage': False,
        'weightage': {1: 150, 2: 200, 3: 250, 4: 100, 5: 100, 6: 100, 7: 100},
    },
    'affiliated_ug': {
        'label': 'Affiliated / constituent colleges — UG programmes',
        'manual': 'NAAC Manual for Affiliated/Constituent (UG, PG) Colleges — Revised Accreditation Framework, w.e.f. 1 February 2023',
        'format': 'SSR format: 7 criteria · 34 key indicators · 85 metrics (35 qualitative + 50 quantitative) · 1,000 weighted marks',
        'eligibility': 'Colleges affiliated to a UGC-recognised university and offering recognised degree programmes. The university frames the curriculum, so the teaching-learning, student support and progression criteria carry most of the weight.',
        'total': 1000,
        'ki_weightage': False,
        'weightage': {1: 100, 2: 350, 3: 110, 4: 100, 5: 140, 6: 100, 7: 100},
    },
    'affiliated_pg': {
        'label': 'Affiliated / constituent colleges — PG programmes',
        'manual': 'NAAC Manual for Affiliated/Constituent (UG, PG) Colleges — Revised Accreditation Framework, w.e.f. 1 February 2023',
        'format': 'SSR format: 7 criteria · 34 key indicators · 85 metrics (35 qualitative + 50 quantitative) · 1,000 weighted marks',
        'eligibility': 'Colleges affiliated to a UGC-recognised university offering recognised postgraduate degree programmes, assessed as a single unit of assessment.',
        'total': 1000,
        'ki_weightage': False,
        'weightage': {1: 100, 2: 350, 3: 120, 4: 100, 5: 130, 6: 100, 7: 100},
    },
}

NAAC_CRITERIA = [
    {
        'name': 'Curricular Aspects',
        'focus': 'Curriculum the institution designs and owns: programme options, credit structure, elective and enrichment choices that respond to local and global needs, with outcomes defined, approved and reviewed by the academic bodies.',
        'key_indicators': [
            {'code': '1.1', 'name': 'Curriculum Design and Development', 'marks': 50},
            {'code': '1.2', 'name': 'Academic Flexibility', 'marks': 30},
            {'code': '1.3', 'name': 'Curriculum Enrichment', 'marks': 50},
            {'code': '1.4', 'name': 'Feedback System', 'marks': 20},
        ],
        'requirements': [
            'Frame programme outcomes and course outcomes for every programme, publish them, and design the syllabus, credit structure and assessment scheme around them.',
            'Run curriculum design through expert groups and stakeholder consultation, with approval records and periodic revision driven by feedback and emerging needs.',
            'Offer horizontal mobility, inter-disciplinary options, credit and choice-based courses, and time-frame flexibility for students.',
            'Provide value-added and enrichment courses that address gender, environment and sustainability, human values and professional ethics, and creative and divergent competencies.',
            'Collect feedback from students, teachers, alumni, employers and society, analyse it, and record the action taken on each point.',
        ],
        'evidence': 'Board of Studies and Academic Council minutes with expert-group and stakeholder lists; curriculum and syllabus documents with credit structure; published PO/CO statements; feedback instruments, analysis and action-taken records; enrichment course offerings and enrolment data; programme-option and academic-calendar records.',
        'owner': 'BoS chair, curriculum development cell, IQAC',
        'metrics': '3 qualitative · 4 quantitative metrics',
    },
    {
        'name': 'Teaching-Learning and Evaluation',
        'focus': 'Teaching that reaches a diverse student body, delivered by qualified and continuously developed teachers, and assessed in a way that measures the stated course outcomes and returns development-inducing feedback to students.',
        'key_indicators': [
            {'code': '2.1', 'name': 'Student Enrolment and Profile', 'marks': 20},
            {'code': '2.2', 'name': 'Catering to Student Diversity', 'marks': 30},
            {'code': '2.3', 'name': 'Teaching-Learning Process', 'marks': 50},
            {'code': '2.4', 'name': 'Teacher Profile and Quality', 'marks': 50},
            {'code': '2.5', 'name': 'Evaluation Process and Reforms', 'marks': 50},
            {'code': '2.6', 'name': 'Student Performance and Learning Outcomes', 'marks': 50},
            {'code': '2.7', 'name': 'Student Satisfaction Survey', 'marks': 50},
        ],
        'requirements': [
            'Run a transparent, well-administered admission process and maintain an accurate student profile covering gender, category, region, socio-economic background and entry qualification.',
            'Diagnose the learning level of new entrants and support backward-category, first-generation, differently-abled and economically weaker students through bridge, remedial and value-added courses.',
            'Plan every course around learner-centred, experiential and collaborative methods, and use the LMS and ICT resources the institute has invested in.',
            'Keep recruitment, qualification, appraisal and professional-development records for every teacher, and plan faculty development against the gaps you find.',
            'Design internal assessment to test the stated course outcomes, with moderation, transparency, timely results and feedback that develops the student.',
            'Track student performance and learning outcomes, and run a formal student satisfaction survey on a sample each year.',
        ],
        'evidence': 'Admission and enrolment data with the student profile; bridge and remedial course records with attendance; course files, lesson plans and pedagogy records; faculty recruitment orders, qualification proofs, FDP and appraisal records; question papers, evaluated scripts and moderation records; result analyses, convocation and progression data; SSS instrument, sample, tabulated results and action taken.',
        'owner': 'HoD, teaching-learning coordinator, exam cell, IQAC',
        'metrics': '6 qualitative · 11 quantitative metrics',
    },
    {
        'name': 'Research, Innovations and Extension',
        'focus': 'A research and extension culture that turns faculty effort into published, funded, patented and community-facing work, supported by the incubation, IPR and industry-academia mechanisms that keep it moving.',
        'key_indicators': [
            {'code': '3.1', 'name': 'Promotion of Research and Facilities', 'marks': 20},
            {'code': '3.2', 'name': 'Resource Mobilization for Research', 'marks': 10},
            {'code': '3.3', 'name': 'Innovation Ecosystem', 'marks': 10},
            {'code': '3.4', 'name': 'Research Publications and Awards', 'marks': 30},
            {'code': '3.5', 'name': 'Consultancy', 'marks': 10},
            {'code': '3.6', 'name': 'Extension Activities', 'marks': 50},
            {'code': '3.7', 'name': 'Collaboration', 'marks': 20},
        ],
        'requirements': [
            'Promote research through a written policy, seed funding, doctoral and post-doctoral support, a research cell, and dedicated space and equipment.',
            'Enable faculty to submit proposals with timely administrative support, and share interdisciplinary and interdepartmental facilities.',
            'Build an innovation ecosystem: incubation support, an IPR cell, industry-academia cells, start-up support and formal recognition of innovations and awards.',
            'Record publications, doctoral and post-doctoral scholars, projects, patents and awards with verifiable identifiers and citation evidence.',
            'Frame a consultancy policy with clear revenue sharing wherever consultancy is offered, and reward the faculty who take it.',
            'Run extension activities with the community — rural outreach in particular — and document the educational value they create.',
            'Formalise collaborations with institutions, industry and professional bodies through agreements, and show the activity that followed each one.',
        ],
        'evidence': 'Research policy, incentive and seed-funding files; project proposals, sanction letters and utilisation certificates; publication lists with indexing proof, DOIs and citation indices; patent and award records; consultancy agreements and revenue records; MoUs and activity reports with partner institutions; extension and outreach documentation with beneficiary evidence.',
        'owner': 'Research and innovation cell, IPR and incubation centre, HoD',
        'metrics': '3 qualitative · 14 quantitative metrics',
    },
    {
        'name': 'Infrastructure and Learning Resources',
        'focus': 'Facilities that keep pace with the academic programme and are maintained and used well, plus learning resources — the library and the digital estate in particular — that students and staff can actually reach.',
        'key_indicators': [
            {'code': '4.1', 'name': 'Physical Facilities', 'marks': 30},
            {'code': '4.2', 'name': 'Library as a Learning Resource', 'marks': 20},
            {'code': '4.3', 'name': 'IT Infrastructure', 'marks': 30},
            {'code': '4.4', 'name': 'Maintenance of Campus Infrastructure', 'marks': 20},
        ],
        'requirements': [
            'Keep classrooms, laboratories, workshops, offices, sports and support facilities adequate for the sanctioned programmes and intake, with annual budgets for upkeep and replenishment.',
            'Maintain the library as a learning resource: holdings, journals, e-resources, ILMS automation, access hours, reading room and usage statistics.',
            'Provide and maintain IT infrastructure — computing labs, licensed software, network, internet bandwidth and user support — for academic and administrative work.',
            'Show that the campus is maintained: work orders, calibration, safety and AMC records, and evidence that facilities are used optimally rather than merely owned.',
        ],
        'evidence': 'Asset and equipment registers with utilisation charts; maintenance, calibration and safety records; library accession and usage statistics, e-resource subscriptions and ILMS data; IT asset inventory, licence records and network documentation; maintenance budgets, work orders and AMC records; campus upkeep and utilisation reports.',
        'owner': 'Labs in-charge, librarian, IT support, estate manager',
        'metrics': '5 qualitative · 4 quantitative metrics',
    },
    {
        'name': 'Student Support and Progression',
        'focus': 'Support that lets every student finish the programme well, and an institutional relationship with students and alumni that continues long after graduation.',
        'key_indicators': [
            {'code': '5.1', 'name': 'Student Support', 'marks': 30},
            {'code': '5.2', 'name': 'Student Progression', 'marks': 30},
            {'code': '5.3', 'name': 'Student Participation and Activities', 'marks': 30},
            {'code': '5.4', 'name': 'Alumni Engagement', 'marks': 10},
        ],
        'requirements': [
            'Operate guidance, counselling, placement, grievance-redressal and welfare cells, and identify every student who receives a scholarship, freeship or other support.',
            'Track progression to higher study and gainful employment, diagnose poor attainment, and act on it with remedial measures and sustained good practices.',
            'Provide the infrastructure and the opportunities for social, cultural and sports participation, and value-based education that builds social responsibility and good citizenship.',
            'Run an active alumni association with chapters, regular meetings, contribution records and alumni participation in teaching, mentoring and resource mobilisation.',
        ],
        'evidence': 'Counselling and guidance logs, scholarship and freeship lists, grievance and welfare records; placement and higher-study data, remedial and bridge course records; participation and activity reports with event documentation; alumni association minutes, membership and contribution records; identity documents of students from different sections and backgrounds.',
        'owner': 'Student affairs, placement cell, counselling cell, alumni coordinator',
        'metrics': '3 qualitative · 8 quantitative metrics',
    },
    {
        'name': 'Governance, Leadership and Management',
        'focus': 'Leadership that turns a stated vision into strategy and delivery, staff who are developed and appraised, finance that is transparent and audited, and an IQAC that runs quality assurance rather than paperwork for it.',
        'key_indicators': [
            {'code': '6.1', 'name': 'Institutional Vision and Leadership', 'marks': 15},
            {'code': '6.2', 'name': 'Strategy Development and Deployment', 'marks': 10},
            {'code': '6.3', 'name': 'Faculty Empowerment Strategies', 'marks': 30},
            {'code': '6.4', 'name': 'Financial Management and Resource Mobilization', 'marks': 15},
            {'code': '6.5', 'name': 'Internal Quality Assurance System', 'marks': 30},
        ],
        'requirements': [
            'Publish the vision and mission, and let the leadership, statutory bodies and academic bodies share decision-making transparently.',
            'Build a strategy with development objectives, directives and milestones, and review progress against it instead of only stating it.',
            'Plan human resources — recruitment, performance appraisal and professional development — and let analysed feedback shape the plan.',
            'Budget, allocate and audit income and expenditure transparently, and state a strategy for mobilising resources.',
            'Run a functional IQAC that develops quality benchmarks, arranges stakeholder feedback responses, documents quality-improvement programmes, maintains an institutional database through MIS, and files the annual AQAR.',
        ],
        'evidence': 'Vision, mission and policy documents with governing-body minutes; strategic plan with milestones and progress review; recruitment, appraisal and FDP records; audited statements, utilisation certificates and budget-versus-actual analyses; IQAC constitution, meeting minutes, benchmark documents, action-taken reports, MIS database and filed AQARs.',
        'owner': 'Principal and management, IQAC coordinator, HR and accounts sections',
        'metrics': '7 qualitative · 5 quantitative metrics',
    },
    {
        'name': 'Institutional Values and Best Practices',
        'focus': 'Values that are actually practised — gender equity, environment, inclusion, ethics — together with the internal practices the institution has developed for itself and the distinctiveness it can evidence.',
        'key_indicators': [
            {'code': '7.1', 'name': 'Institutional Values and Social Responsibilities', 'marks': 50},
            {'code': '7.2', 'name': 'Best Practices', 'marks': 30},
            {'code': '7.3', 'name': 'Institutional Distinctiveness', 'marks': 20},
        ],
        'requirements': [
            'Run gender-equity promotion programmes, and act on climate and environmental concerns through energy conservation, green initiatives and sustainable campus practices.',
            'Organise value education, outreach and extension that reach beyond the campus, with documented participation and outcomes.',
            'Identify, document and evaluate the institution’s own best practices, and share them with the NAAC community.',
            'State the institution’s distinctiveness and produce the evidence — awards, rankings, unique programmes, community standing — that supports the claim.',
        ],
        'evidence': 'Gender equity and environmental programme documentation with attendance and outcome reports; value education, outreach and extension records; best-practice documentation with evaluation and dissemination evidence; distinctiveness statements, awards and supporting records.',
        'owner': 'IQAC, student affairs, administration',
        'metrics': '8 qualitative · 4 quantitative metrics',
    },
]

NAAC_GRADING = [
    {'range': '3.51 – 4.00', 'grade': 'A++', 'status': 'Accredited'},
    {'range': '3.26 – 3.50', 'grade': 'A+', 'status': 'Accredited'},
    {'range': '3.01 – 3.25', 'grade': 'A', 'status': 'Accredited'},
    {'range': '2.76 – 3.00', 'grade': 'B++', 'status': 'Accredited'},
    {'range': '2.51 – 2.75', 'grade': 'B+', 'status': 'Accredited'},
    {'range': '2.01 – 2.50', 'grade': 'B', 'status': 'Accredited'},
    {'range': '1.51 – 2.00', 'grade': 'C', 'status': 'Accredited'},
    {'range': '≤ 1.50', 'grade': 'D', 'status': 'Not accredited'},
]

NAAC_PROCESS = [
    {'stage': 'IIQA', 'title': 'Institutional Information for Quality Assessment (IIQA)', 'detail': 'Apply online any time during the year on the NAAC HEI portal. An accepted IIQA starts the clock: the SSR must be uploaded within 45 days, with a maximum 15-day extension only for documented technical or natural-calamity reasons.'},
    {'stage': 'SSR', 'title': 'Self-Study Report (SSR)', 'detail': 'The institution writes its own report against every metric — 35 qualitative responses and 50 quantitative data points for an autonomous college. The same SSR in PDF must be uploaded on the institutional website, and the outcome document must be displayed there too.'},
    {'stage': 'DVV', 'title': 'Data Validation and Verification and the pre-qualifier', 'detail': 'NAAC verifies the quantitative data, usually within 30 days, and issues a deviation report. The institution must then score at least 25% on the quantitative metrics to qualify for the peer team visit; incorrect data can mean forfeiture of the first fee instalment and referral to statutory authorities.'},
    {'stage': 'PTV', 'title': 'Peer Team visit', 'detail': 'The visit focuses on the qualitative metrics — the peer team reads the narrative, verifies the evidence, and records strengths and weaknesses criterion by criterion. A student satisfaction survey runs alongside the DVV stage.'},
    {'stage': 'Outcome', 'title': 'Outcome document and grade sheet', 'detail': 'Three parts: the peer team report, the system-generated quality profile from the quantitative metrics, and the institutional grade sheet. The CGPA is rounded to two decimals and mapped to a letter grade; the document must be displayed on the institutional website.'},
    {'stage': 'AQAR', 'title': 'Annual Quality Assurance Report (AQAR)', 'detail': 'Filed online by 31 December every year for the completed academic year — four AQARs in a five-year validity cycle, six if validity is extended to seven years. A functional IQAC and timely AQARs are minimum institutional requirements for the next cycle.'},
    {'stage': 'Next cycle', 'title': 'Subsequent cycles and re-assessment', 'detail': 'Cycle 1 is the first assessment; later cycles follow five-year periods. A new IIQA is filed in the last six months of the validity period, and institutions may volunteer for re-assessment after at least one year but not after three years, once per cycle.'},
]

NAAC_FACTS = [
    {'label': 'Criteria', 'value': '7'},
    {'label': 'Key indicators', 'value': '34'},
    {'label': 'Qualitative metrics', 'value': '35'},
    {'label': 'Quantitative metrics', 'value': '50'},
    {'label': 'Total weighted marks', 'value': '1,000'},
    {'label': 'Validity', 'value': '5 years'},
]

NAAC_SOURCES = [
    {'label': 'NAAC — Assessment & Accreditation: criteria, weightage, grading, cycles, outcome', 'url': 'https://naac.gov.in/index.php/en/assessment-accreditation'},
    {'label': 'NAAC — Manual for Autonomous Colleges (full official text)', 'url': 'https://naac.gov.in/index.php/en/2-uncategorised/239-empanelment-of-hindi-consultant-2023'},
    {'label': 'NAAC — Manuals and publications library', 'url': 'https://naac.gov.in/index.php/en/resources/publications/manuals'},
    {'label': 'NAAC — Info for institutions: IQAC guidelines, functions and AQAR timeline', 'url': 'https://naac.gov.in/index.php/en/info-for-institutions'},
    {'label': 'NAAC — Apply online (IIQA, SSR, AQAR and appeal submission)', 'url': 'https://naac.gov.in/index.php/en/apply-now'},
    {'label': 'NAAC — HEI portal (assessmentonline.naac.gov.in)', 'url': 'https://assessmentonline.naac.gov.in/'},
]

NAAC_INSTITUTE_SOURCES = [
    {'label': 'Anurag Engineering College — NAAC certificate (A+) published by the institute', 'url': 'https://anurag.ac.in/wp-content/uploads/2024/04/NAAC_Certificate.pdf'},
    {'label': 'Anurag Engineering College — NBA and other approvals, accreditations and IQAC disclosures', 'url': 'https://anurag.ac.in/about-us/approvals-accreditations/'},
]
