from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parents[2] / "static" / "docs" / "images"
FONT = "Arial,Helvetica,sans-serif"
FONT_SCALE = 1.15


def txt(x, y, value, size=14, anchor="start", weight="normal"):
    display_size = max(size + 1, round(size * FONT_SCALE))
    return f'<text x="{x}" y="{y}" font-size="{display_size}" text-anchor="{anchor}" font-weight="{weight}" fill="#111" stroke="none">{escape(value)}</text>'


def svg(title, width, height, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#222"/></marker><marker id="open" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="10" markerHeight="10" orient="auto"><path d="M1,1 L11,6 L1,11 z" fill="#fff" stroke="#222"/></marker></defs>
<rect width="100%" height="100%" fill="#f7f7f7"/><g font-family="{FONT}" stroke="#222" stroke-width="1.4">{txt(width/2, 30, title, 19, 'middle', 'bold')}{body}</g></svg>'''


def box(x, y, width, title, attrs, methods=()):
    row = 18
    header = 34
    attrs_height = max(28, len(attrs) * row + 10)
    methods_height = max(28, len(methods) * row + 10)
    height = header + attrs_height + methods_height
    body = [f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="#fff"/>',
            f'<line x1="{x}" y1="{y+header}" x2="{x+width}" y2="{y+header}"/>',
            f'<line x1="{x}" y1="{y+header+attrs_height}" x2="{x+width}" y2="{y+header+attrs_height}"/>',
            txt(x+width/2, y+22, title, 15, "middle", "bold")]
    body.extend(txt(x+9, y+header+18+i*row, item, 12) for i, item in enumerate(attrs))
    body.extend(txt(x+9, y+header+attrs_height+18+i*row, item, 12) for i, item in enumerate(methods))
    return "".join(body), height


def edge(x1, y1, x2, y2, label="", left="", right="", dashed=False, arrow=False, open_arrow=False):
    marker = ' marker-end="url(#arrow)"' if arrow else (' marker-end="url(#open)"' if open_arrow else "")
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    body = [f'<path d="M{x1},{y1} L{x2},{y2}" fill="none"{marker}{dash}/>']
    if label:
        body.append(f'<rect x="{(x1+x2)/2-55}" y="{(y1+y2)/2-20}" width="110" height="18" fill="#f7f7f7" stroke="none"/>')
        body.append(txt((x1+x2)/2, (y1+y2)/2-6, label, 11, "middle"))
    if left: body.append(txt(x1+5, y1-6, left, 11))
    if right: body.append(txt(x2-5, y2-6, right, 11, "end"))
    return "".join(body)


def relation(points, label="", source_mult="", target_mult="", dashed=False, target_arrow=False,
             label_x=None, label_y=None, source_pos=None, target_pos=None):
    """Draw an orthogonal UML relationship without placing text over the line."""
    marker = ' marker-end="url(#open)"' if target_arrow else ""
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    path = " ".join(
        (f"M{x},{y}" if index == 0 else f"L{x},{y}")
        for index, (x, y) in enumerate(points)
    )
    body = [f'<path d="{path}" fill="none"{marker}{dash}/>']
    if label:
        lx = label_x if label_x is not None else (points[0][0] + points[-1][0]) / 2
        ly = label_y if label_y is not None else (points[0][1] + points[-1][1]) / 2
        body.append(f'<rect x="{lx-64}" y="{ly-15}" width="128" height="20" rx="3" fill="#f7f7f7" stroke="none"/>')
        body.append(txt(lx, ly, label, 12, "middle", "bold"))
    sx, sy = source_pos or (points[0][0] + 8, points[0][1] - 8)
    tx, ty = target_pos or (points[-1][0] - 8, points[-1][1] - 8)
    if source_mult:
        body.append(txt(sx, sy, source_mult, 12, "start", "bold"))
    if target_mult:
        body.append(txt(tx, ty, target_mult, 12, "end", "bold"))
    return "".join(body)


def save(name, title, width, height, body):
    (OUT / name).write_text(svg(title, width, height, body), encoding="utf-8")


def structural():
    # Library app: every persistent model is shown. Student is included as an
    # external class because both Issue and Fine contain real foreign keys to it.
    author, _ = box(45, 85, 270, "Author", ["- id : BigInteger", "- name : String", "- description : String"], ["+ __str__() : String"])
    book, _ = box(420, 70, 300, "Book", ["- id : BigInteger", "- name : String", "- image : ImageField", "- category : String", "- author : Author [FK]"], ["+ __str__() : String", "+ cloudinary_image_url : String"])
    issue, _ = box(825, 55, 325, "Issue", ["- id : BigInteger", "- student : Student [FK]", "- book : Book [FK]", "- created_at : DateTime", "- issued : Boolean", "- issued_at : DateTime [0..1]", "- returned : Boolean", "- return_date : DateTime [0..1]"], ["+ days_no() : String", "+ __str__() : String"])
    student, _ = box(1245, 105, 250, "Student", ["«external: student app»", "- id : BigInteger"], ["+ __str__() : String"])
    fine, _ = box(825, 470, 360, "Fine", ["- id : BigInteger", "- student : Student [FK]", "- issue : Issue [FK]", "- amount : Decimal", "- paid : Boolean", "- order_id : String [0..1]", "- razorpay_order_id : String [0..1]", "- razorpay_payment_id : String [0..1]", "- razorpay_signature : String [0..1]", "- datetime_of_payment : DateTime [0..1]"], ["+ save() : void", "+ __str__() : String"])
    stats, _ = box(420, 500, 300, "LibraryStat", ["- id : BigInteger", "- borrowed_books : PositiveInteger"], ["+ __str__() : String"])
    rec, _ = box(45, 430, 330, "BookRecommendation", ["- id : BigInteger", "- image : ImageField [0..1]", "- title : String", "- author : String", "- book_type : Text", "- isbn : String", "- publisher : String", "- edition_year : String", "- book_format : {Hard, E-book}", "- copies_recommended : String", "- existing : String", "- cost : String", "- created_at : DateTime"], ["+ __str__() : String"])
    body = author + book + issue + student + fine + stats + rec
    body += relation([(315, 150), (420, 150)], "writes / author", "1", "0..*", target_arrow=True, label_y=133)
    body += relation([(720, 165), (825, 165)], "issue records / book", "1", "0..*", target_arrow=True, label_y=148)
    body += relation([(1150, 185), (1245, 185)], "borrower / issues", "0..*", "1", dashed=True, target_arrow=True, label_y=168)
    body += relation([(990, 305), (990, 470)], "generates / issue", "1", "0..*", target_arrow=True, label_x=1070, label_y=397)
    body += relation([(1185, 590), (1380, 590), (1380, 233)], "charged to / fines", "0..*", "1", dashed=True, target_arrow=True, label_x=1300, label_y=575)
    body += relation([(825, 275), (765, 275), (765, 560), (720, 560)], "updates on save", "", "1", dashed=True, target_arrow=True, label_x=765, label_y=425)
    body += txt(210, 760, "Independent recommendation record (no ForeignKey relationships)", 12, "middle", "bold")
    save("library_class_diagram.svg", "Library App - Complete Class Diagram", 1540, 810, body)

    user, _ = box(45, 95, 300, "auth.User", ["- id : BigInteger", "- username : String", "- email : Email", "- password : String"], ["+ get_full_name() : String"])
    student, _ = box(465, 75, 340, "Student", ["- id : BigInteger", "- student_id : User [OneToOne]", "- department : Department [FK]", "- first_name : String", "- last_name : String"], ["+ __str__() : String"])
    dept, _ = box(925, 105, 285, "Department", ["- id : BigInteger", "- name : String"], ["+ __str__() : String"])
    body = user + student + dept
    body += relation([(345, 175), (465, 175)], "account / profile", "1", "1", target_arrow=True, label_y=155)
    body += relation([(805, 175), (925, 175)], "members / department", "0..*", "1", target_arrow=True, label_y=155)
    body += txt(630, 335, "Student.student_id is OneToOneField(User); Student.department is ForeignKey(Department).", 13, "middle", "bold")
    save("student_class_diagram.svg", "Student App - Complete Class Diagram", 1260, 390, body)

    # A single domain view makes the cross-app relationships explicit.
    body = '<rect x="25" y="55" width="925" height="760" fill="#fff"/><rect x="985" y="55" width="485" height="760" fill="#fff"/>'+txt(45,84,"«package» library",16,weight="bold")+txt(1005,84,"«package» student + auth",16,weight="bold")
    positions = [(60,120,210,"Author"),(350,120,210,"Book"),(665,120,230,"Issue"),(665,410,230,"Fine"),(350,595,230,"LibraryStat"),(60,540,235,"BookRecommendation"),(1030,120,230,"Student"),(1030,430,190,"Department"),(1260,430,170,"auth.User")]
    for x,y,w,name in positions:
        node,_ = box(x,y,w,name,["- id : BigInteger"],["+ __str__() : String"])
        body += node
    body += relation([(270,165),(350,165)],"author","1","0..*",target_arrow=True,label_y=145)
    body += relation([(560,165),(665,165)],"book","1","0..*",target_arrow=True,label_y=145)
    body += relation([(895,165),(1030,165)],"student","0..*","1",dashed=True,target_arrow=True,label_y=145)
    body += relation([(780,210),(780,410)],"issue / fines","1","0..*",target_arrow=True,label_x=850,label_y=315)
    body += relation([(895,515),(960,515),(960,245),(1030,245)],"student / fines","0..*","1",dashed=True,target_arrow=True,label_x=960,label_y=390)
    body += relation([(1145,210),(1145,430)],"department","0..*","1",target_arrow=True,label_x=1220,label_y=330)
    body += relation([(1260,475),(1250,475),(1250,300),(1345,300),(1345,520)],"account / profile","1","1",target_arrow=True,label_x=1345,label_y=285)
    body += relation([(665,195),(620,195),(620,640),(580,640)],"updates count","0..*","1",dashed=True,target_arrow=True,label_x=620,label_y=455)
    body += txt(178, 790, "No associations", 12, "middle", "bold")
    save("relationships_diagram.svg", "AEC Library - Complete Cross-App Domain Model", 1500, 850, body)


def actor(x, y, name):
    return f'<circle cx="{x}" cy="{y}" r="17" fill="#fff"/><path d="M{x},{y+17} V{y+70} M{x-28},{y+38} H{x+28} M{x},{y+70} L{x-24},{y+108} M{x},{y+70} L{x+24},{y+108}" fill="none"/>'+txt(x,y+130,name,14,"middle","bold")


def usecase(x, y, label):
    return f'<ellipse cx="{x}" cy="{y}" rx="125" ry="31" fill="#fff"/>'+txt(x,y+5,label,13,"middle")


def use_cases(filename, title, actor_name, cases):
    body = '<rect x="260" y="55" width="930" height="570" fill="#fff"/>'+txt(280,82,"AEC Library Management System",14,weight="bold")+actor(115,260,actor_name)
    for index, label in enumerate(cases):
        x = 480 if index < 4 else 910
        y = 130 + (index % 4) * 130
        body += usecase(x,y,label)+edge(145,295,x-125,y)
    save(filename,title,1220,660,body)


def behavioral():
    use_cases("student_use_case_diagram.svg", "Student - Use Case Diagram", "Student", ["Login with Google", "Search books", "View availability", "Request book issue", "View issue history", "View fines", "Pay fine online", "Update profile"])
    use_cases("admin_use_case_diagram.svg", "Librarian / Admin - Use Case Diagram", "Librarian / Admin", ["Secure login", "Manage books", "Manage students", "Approve issue", "Process return", "Calculate fine", "Generate reports", "Configure system"])

    body = ""
    participants = [(110,"Student"),(345,"Web UI"),(590,"Issue Service"),(830,"Book"),(1060,"Database")]
    for x,name in participants:
        body += f'<rect x="{x-65}" y="55" width="130" height="40" fill="#fff"/>'+txt(x,80,name,13,"middle","bold")+f'<path d="M{x},95 V600" stroke-dasharray="6 5"/>'
    for x1,x2,y,label,reply in [(110,345,135,"requestBook(bookId)",False),(345,590,195,"validateRequest()",False),(590,830,255,"checkAvailability()",False),(830,590,315,"available",True),(590,1060,375,"createIssue()",False),(1060,590,435,"issueCreated",True),(590,345,495,"confirmation",True),(345,110,555,"showSuccess()",True)]:
        body += edge(x1,y,x2,y,label,dashed=reply,arrow=True)
    save("book_issue_sequence_diagram.svg", "Book Issue Flow - Sequence Diagram", 1170, 640, body)

    def state(x,y,w,label): return f'<rect x="{x}" y="{y}" width="{w}" height="72" rx="16" fill="#fff"/>'+txt(x+w/2,y+42,label,15,"middle","bold")
    body = '<circle cx="70" cy="225" r="12" fill="#222"/>'+state(145,190,190,"Available")+state(430,190,190,"Issued")+state(725,85,190,"Overdue")+state(725,310,190,"Reserved")+'<circle cx="1030" cy="225" r="16" fill="#fff"/><circle cx="1030" cy="225" r="9" fill="#222"/>'
    body += edge(82,225,145,225,"added",arrow=True)+edge(335,225,430,225,"issue",arrow=True)+edge(620,205,725,140,"due date",arrow=True)+edge(725,160,620,220,"return + fine",arrow=True)+edge(620,245,725,335,"reserve",arrow=True)+edge(725,355,335,245,"cancel",arrow=True)+edge(915,120,1030,210,"remove",arrow=True)
    save("book_status_statechart_diagram.svg", "Book Status - State Machine Diagram", 1100, 470, body)

    def action(x,y,w,label): return f'<rect x="{x}" y="{y}" width="{w}" height="55" rx="18" fill="#fff"/>'+txt(x+w/2,y+34,label,14,"middle","bold")
    body = '<circle cx="560" cy="60" r="12" fill="#222"/>'+action(465,100,190,"Login")+action(450,195,220,"Select operation")+'<path d="M560,275 L590,305 L560,335 L530,305 z" fill="#fff"/>'+action(100,365,220,"Search / request book")+action(450,365,220,"Issue / return book")+action(800,365,220,"View / pay fine")+action(450,475,220,"Update records")+'<circle cx="560" cy="590" r="16" fill="#fff"/><circle cx="560" cy="590" r="9" fill="#222"/>'
    body += edge(560,72,560,100,arrow=True)+edge(560,155,560,195,arrow=True)+edge(560,250,560,275,arrow=True)+edge(530,305,210,365,"student",arrow=True)+edge(560,335,560,365,"librarian",arrow=True)+edge(590,305,910,365,"payment",arrow=True)+edge(210,420,500,475,arrow=True)+edge(560,420,560,475,arrow=True)+edge(910,420,620,475,arrow=True)+edge(560,530,560,574,"complete",arrow=True)
    save("library_operations_activity_diagram.svg", "Library Operations - Activity Diagram", 1120, 630, body)


structural()
behavioral()


# Complete course-lab UML set. These overwrite the older compact behavioral
# drawings with diagrams reverse-checked against the current views and URLs.
def note(x, y, width, lines):
    height = 24 + len(lines) * 18
    body = f'<path d="M{x},{y} H{x+width-18} L{x+width},{y+18} V{y+height} H{x} Z M{x+width-18},{y} V{y+18} H{x+width}" fill="#fff"/>'
    body += "".join(txt(x+10, y+24+i*18, line, 11) for i, line in enumerate(lines))
    return body


def component(x, y, width, height, name, stereotype="component"):
    body = f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="3" fill="#fff"/>'
    body += f'<rect x="{x-10}" y="{y+18}" width="28" height="14" fill="#fff"/><rect x="{x-10}" y="{y+43}" width="28" height="14" fill="#fff"/>'
    body += txt(x+width/2, y+28, f"«{stereotype}»", 11, "middle")
    body += txt(x+width/2, y+52, name, 14, "middle", "bold")
    return body


def deployment_node(x, y, width, height, name, stereotype):
    depth = 16
    body = f'<path d="M{x},{y+depth} L{x+depth},{y} H{x+width} V{y+height-depth} L{x+width-depth},{y+height} H{x} Z" fill="#fff"/>'
    body += f'<path d="M{x},{y+depth} H{x+width-depth} L{x+width},{y} M{x+width-depth},{y+depth} V{y+height}"/>'
    body += txt(x+width/2, y+34, f"«{stereotype}»", 11, "middle")
    body += txt(x+width/2, y+57, name, 15, "middle", "bold")
    return body


def complete_uml_set():
    def activity_action(x, y, width, label):
        return f'<rect x="{x}" y="{y}" width="{width}" height="55" rx="18" fill="#fff"/>'+txt(x+width/2,y+34,label,14,"middle","bold")

    # Use case diagram
    body = '<rect x="245" y="55" width="1110" height="760" fill="#fff"/>'+txt(265,84,"AEC Library Management System",16,weight="bold")
    body += actor(100,185,"Student")+actor(100,585,"Librarian / Admin")+actor(1460,330,"Razorpay")
    student_cases = [(450,135,"Sign up / Login"),(750,135,"Browse & search books"),(1050,135,"Request / borrow book"),
                     (450,285,"View issue history"),(750,285,"View fines"),(1050,285,"Pay fine")]
    admin_cases = [(450,500,"Manage catalogue"),(750,500,"Review issue requests"),(1050,500,"Issue / return book"),
                   (450,665,"Manage fines"),(750,665,"Reset circulation"),(1050,665,"View documentation")]
    for x,y,label in student_cases+admin_cases:
        body += usecase(x,y,label)
    for x,y,_ in student_cases:
        body += edge(130,220,x-125,y)
    for x,y,_ in admin_cases:
        body += edge(130,620,x-125,y)
    body += relation([(1175,285),(1365,285),(1365,330),(1430,330)],"payment API","","",dashed=True,target_arrow=True,label_x=1300,label_y=268)
    save("library_use_case_diagram.svg","AEC Library - Use Case Diagram",1540,860,body)

    # Sequence diagram: complete request, approval, return, and payment lifecycle.
    participants = [(90,"Student"),(300,"Browser UI"),(535,"Django Views"),(780,"Models / ORM"),(1010,"PostgreSQL"),(1235,"Librarian"),(1450,"Razorpay")]
    body = ""
    for x,name in participants:
        body += f'<rect x="{x-72}" y="55" width="144" height="42" fill="#fff"/>'+txt(x,81,name,12,"middle","bold")+f'<path d="M{x},97 V850" stroke-dasharray="6 5"/>'
    messages = [
        (90,300,125,"1: request book",False),(300,535,165,"2: issuerequest(bookID)",False),
        (535,780,205,"3: get_or_create(Issue)",False),(780,1010,245,"4: INSERT / SELECT",False),
        (1010,780,285,"5: issue record",True),(535,300,325,"6: request confirmed",True),
        (1235,535,375,"7: approve issue",False),(535,780,415,"8: set issued_at, return_date",False),
        (780,1010,455,"9: UPDATE Issue",False),(535,1235,495,"10: issued",True),
        (1235,535,545,"11: return book",False),(535,780,585,"12: calcFine(issue), mark returned",False),
        (780,1010,625,"13: UPDATE Issue / Fine",False),(90,300,675,"14: pay fine",False),
        (300,535,715,"15: payfine(fineID)",False),(535,1450,755,"16: create order",False),
        (1450,535,795,"17: order / signature",True),(535,780,835,"18: verify & mark paid",False),
    ]
    for x1,x2,y,label,reply in messages:
        body += edge(x1,y,x2,y,label,dashed=reply,arrow=True)
    save("library_sequence_diagram.svg","Book Issue, Return and Fine Payment - Sequence Diagram",1540,890,body)

    # Communication/collaboration diagram: numbered messages over object links.
    objects = [(60,90,245,"student:Student"),(410,70,270,"ui:Browser"),(810,70,290,"views:LibraryViews"),
               (1215,90,245,"admin:Librarian"),(90,560,260,"razorpay:Gateway"),(500,560,270,"orm:DjangoORM"),
               (900,560,270,"db:PostgreSQL"),(1260,560,235,"fine:Fine")]
    body = ""
    for x,y,w,name in objects:
        body += f'<rect x="{x}" y="{y}" width="{w}" height="64" fill="#fff"/>'+txt(x+w/2,y+27,name,14,"middle","bold")+txt(x+w/2,y+49,"«object»",11,"middle")
    links = [
        (305,122,410,102,"1: requestBook(bookID)"),(680,102,810,102,"1.1: issuerequest()"),
        (1100,102,1215,122,"2: review / approve"),(955,134,635,560,"1.2 / 2.1: create or update Issue"),
        (770,592,900,592,"1.3: SQL INSERT / UPDATE"),(1337,154,1337,560,"3: returnBook(issueID)"),
        (1260,592,1170,592,"3.1: calcFine()"),(500,592,350,592,"4.1: createOrder()"),
        (220,560,535,134,"4.2: order response"),(410,134,305,134,"4: checkout / callback"),
        (810,122,350,560,"4.3: verifySignature()"),(770,612,1260,612,"4.4: mark Fine paid"),
    ]
    for x1,y1,x2,y2,label in links:
        body += relation([(x1,y1),(x2,y2)],label,target_arrow=True,label_x=(x1+x2)/2,label_y=(y1+y2)/2-8)
    body += note(580,325,355,["Message numbers show execution order.","Links show collaborating runtime objects."])
    save("library_collaboration_diagram.svg","AEC Library - Collaboration Diagram",1540,760,body)

    # Statechart for an Issue record (the actual persisted circulation state).
    def st(x,y,w,label,sub=""):
        result=f'<rect x="{x}" y="{y}" width="{w}" height="82" rx="18" fill="#fff"/>'+txt(x+w/2,y+34,label,15,"middle","bold")
        if sub: result += txt(x+w/2,y+59,sub,11,"middle")
        return result
    body = '<circle cx="65" cy="265" r="12" fill="#222"/>'
    body += st(130,224,230,"Requested","issued = false")
    body += st(465,224,230,"Issued","issued = true")
    body += st(805,80,230,"Overdue","now > return_date")
    body += st(805,375,230,"Returned","returned = true")
    body += st(1155,80,250,"Fine Outstanding","Fine.paid = false")
    body += st(1155,375,250,"Closed","returned and no balance")
    body += '<circle cx="1480" cy="416" r="16" fill="#fff"/><circle cx="1480" cy="416" r="9" fill="#222"/>'
    body += edge(77,265,130,265,"request",arrow=True)+edge(360,265,465,265,"approve / issue",arrow=True)
    body += edge(695,245,805,135,"due date passes",arrow=True)+edge(695,285,805,395,"return on time",arrow=True)
    body += edge(920,162,920,375,"return / calculate fine",arrow=True)
    body += edge(1035,120,1155,120,"amount > 0",arrow=True)+edge(1035,416,1155,416,"amount = 0",arrow=True)
    body += edge(1280,162,1280,375,"pay or waive",arrow=True)+edge(1405,416,1464,416,"complete",arrow=True)
    body += relation([(245,306),(245,525),(1280,525),(1280,457)],"cancel / clear pending","","",dashed=True,target_arrow=True,label_x=700,label_y=515)
    save("library_statechart_diagram.svg","Issue Lifecycle - Statechart Diagram",1540,600,body)

    # Activity diagram with student/admin swimlanes.
    body = '<rect x="30" y="55" width="480" height="810" fill="#fff"/><rect x="510" y="55" width="500" height="810" fill="#fff"/><rect x="1010" y="55" width="500" height="810" fill="#fff"/>'
    body += txt(270,85,"Student",15,"middle","bold")+txt(760,85,"Django System",15,"middle","bold")+txt(1260,85,"Librarian / Payment Gateway",15,"middle","bold")
    body += '<circle cx="270" cy="125" r="12" fill="#222"/>'
    actions=[(170,165,200,"Login"),(160,255,220,"Search / select book"),(155,345,230,"Request issue"),
             (645,165,230,"Authenticate user"),(635,345,250,"Create Issue request"),(1135,345,250,"Review request"),
             (1135,455,250,"Approve and issue"),(635,455,250,"Set 15-day return date"),(160,555,220,"Return book"),
             (635,555,250,"Calculate fine"),(1135,650,250,"Pay / waive fine"),(635,745,250,"Close transaction")]
    for x,y,w,label in actions: body += activity_action(x,y,w,label)
    body += edge(270,137,270,165,arrow=True)+edge(370,192,645,192,arrow=True)+edge(760,220,270,255,arrow=True)
    body += edge(270,310,270,345,arrow=True)+edge(385,372,635,372,arrow=True)+edge(885,372,1135,372,arrow=True)
    body += edge(1260,400,1260,455,"[approved]",arrow=True)+edge(1135,482,885,482,arrow=True)
    body += edge(760,510,270,555,"book due / returned",arrow=True)+edge(380,582,635,582,arrow=True)
    body += '<path d="M760,625 L795,660 L760,695 L725,660 Z" fill="#fff"/>'+txt(760,665,"fine?",11,"middle","bold")
    body += edge(760,610,760,625,arrow=True)+edge(795,660,1135,677,"[yes]",arrow=True)+edge(1135,705,885,772,arrow=True)
    body += edge(725,660,760,745,"[no]",arrow=True)
    body += '<circle cx="760" cy="835" r="16" fill="#fff"/><circle cx="760" cy="835" r="9" fill="#222"/>'+edge(760,800,760,819,arrow=True)
    save("library_activity_diagram.svg","Borrow, Return and Fine Processing - Activity Diagram",1540,900,body)

    # Component diagram.
    body = component(45,120,240,90,"Browser UI","client")+component(385,85,270,90,"Django URL Router")
    body += component(385,245,270,90,"Library Views")+component(385,405,270,90,"Student/Auth Views")
    body += component(770,85,260,90,"Templates & Static SVGs")+component(770,245,260,90,"Domain Models / ORM")
    body += component(770,405,260,90,"Fine Utility")+component(1150,90,260,90,"PostgreSQL","database")
    body += component(1150,270,260,90,"Cloudinary","external service")+component(1150,450,260,90,"Razorpay API","external service")
    body += relation([(285,165),(385,130)],"HTTP(S)","","",target_arrow=True,label_x=335,label_y=125)
    body += relation([(520,175),(520,245)],"dispatch","","",target_arrow=True,label_x=575,label_y=215)
    body += relation([(520,175),(520,405)],"auth routes","","",target_arrow=True,label_x=590,label_y=380)
    body += relation([(655,290),(770,290)],"render / query","","",target_arrow=True,label_y=270)
    body += relation([(655,450),(770,290)],"user profile","","",target_arrow=True,label_x=700,label_y=385)
    body += relation([(900,245),(900,175)],"renders","","",target_arrow=True,label_x=950,label_y=215)
    body += relation([(1030,290),(1150,135)],"SQL","","",target_arrow=True,label_x=1090,label_y=205)
    body += relation([(1030,290),(1150,315)],"image URLs","","",dashed=True,target_arrow=True,label_x=1090,label_y=285)
    body += relation([(655,290),(770,450)],"calcFine()","","",target_arrow=True,label_x=710,label_y=390)
    body += relation([(655,310),(1150,495)],"orders / signatures","","",dashed=True,target_arrow=True,label_x=910,label_y=470)
    save("library_component_diagram.svg","AEC Library - Component Diagram",1480,650,body)

    # Deployment diagram based on render.yaml/settings.
    body = deployment_node(45,110,310,210,"Student / Librarian Device","device")
    body += component(90,190,220,80,"Web Browser","artifact")
    body += deployment_node(455,70,610,570,"Render Web Service: anrkitdept","execution environment")
    body += component(515,160,230,90,"Gunicorn","process")+component(775,160,230,90,"Django Application","artifact")
    body += component(515,315,230,90,"Templates / Static Files","artifact")+component(775,315,230,90,"Library + Student Apps","artifact")
    body += component(645,470,230,90,"Django ORM","component")
    body += deployment_node(1165,70,315,210,"Render PostgreSQL","database node")
    body += component(1210,160,225,80,"anrkitdept-db","database")
    body += deployment_node(1165,345,315,210,"External Cloud Services","cloud")
    body += component(1210,420,225,70,"Cloudinary","service")+component(1210,505,225,70,"Razorpay","service")
    body += relation([(355,215),(455,215)],"HTTPS","","",target_arrow=True,label_y=195)
    body += relation([(745,205),(775,205)],"WSGI","","",target_arrow=True,label_y=188)
    body += relation([(890,250),(890,315)],"loads","","",target_arrow=True,label_x=940,label_y=290)
    body += relation([(890,405),(760,470)],"model calls","","",target_arrow=True,label_x=845,label_y=445)
    body += relation([(875,515),(1165,185)],"TLS / DATABASE_URL","","",target_arrow=True,label_x=1030,label_y=360)
    body += relation([(1005,350),(1165,445)],"HTTPS media","","",dashed=True,target_arrow=True,label_x=1085,label_y=415)
    body += relation([(1005,380),(1165,535)],"HTTPS payment API","","",dashed=True,target_arrow=True,label_x=1085,label_y=505)
    body += note(470,670,590,["Build: build.sh → collectstatic + migrate","Runtime: gunicorn engineeringcollege.wsgi:application","Configuration and secrets are supplied through Render environment variables."])
    save("library_deployment_diagram.svg","AEC Library - Deployment Diagram",1540,800,body)


complete_uml_set()


def association(points, name, source_mult, target_mult, label_x, label_y,
                source_x, source_y, target_x, target_y, dashed=False):
    """A proper UML association: no inheritance-style triangular arrowhead."""
    path = " ".join(
        (f"M{x},{y}" if index == 0 else f"L{x},{y}")
        for index, (x, y) in enumerate(points)
    )
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    body = f'<path d="{path}" fill="none"{dash}/>'
    if name:
        body += f'<rect x="{label_x-68}" y="{label_y-14}" width="136" height="19" rx="3" fill="#f7f7f7" stroke="none"/>'
        body += txt(label_x, label_y, name, 11, "middle", "bold")
    body += txt(source_x, source_y, source_mult, 12, "middle", "bold")
    body += txt(target_x, target_y, target_mult, 12, "middle", "bold")
    return body


def corrected_class_diagrams():
    # Complete domain class diagram: compact enough to remain legible in the
    # documentation card, with every relationship fully inside the viewBox.
    author, _ = box(30, 75, 190, "Author",
                    ["- id : BigInteger", "- name : String", "- description : String"],
                    ["+ __str__() : String"])
    book, _ = box(275, 65, 205, "Book",
                  ["- id : BigInteger", "- name : String", "- image : ImageField",
                   "- category : String", "- author_id : FK"],
                  ["+ __str__() : String", "+ cloudinary_image_url : String"])
    issue, _ = box(535, 50, 245, "Issue",
                   ["- id : BigInteger", "- book_id : FK", "- student_id : FK",
                    "- created_at : DateTime", "- issued : Boolean",
                    "- issued_at : DateTime [0..1]", "- returned : Boolean",
                    "- return_date : DateTime [0..1]"],
                   ["+ days_no() : String", "+ __str__() : String"])
    fine, _ = box(845, 55, 305, "Fine",
                  ["- id : BigInteger", "- issue_id : FK", "- student_id : FK",
                   "- amount : Decimal", "- paid : Boolean",
                   "- order_id : String [0..1]", "- datetime_of_payment : DateTime [0..1]",
                   "- razorpay_order_id : String [0..1]",
                   "- razorpay_payment_id : String [0..1]",
                   "- razorpay_signature : String [0..1]"],
                  ["+ save() : void", "+ __str__() : String"])
    recommendation, _ = box(30, 485, 245, "BookRecommendation",
                            ["- id : BigInteger", "- title : String", "- author : String",
                             "- isbn : String", "- publisher : String",
                             "- book_format : Choice", "- copies_recommended : String",
                             "- created_at : DateTime"],
                            ["+ __str__() : String"])
    stats, _ = box(320, 610, 260, "LibraryStat",
                   ["- id : BigInteger", "- borrowed_books : PositiveInteger"],
                   ["+ __str__() : String"])
    department, _ = box(600, 610, 190, "Department",
                        ["- id : BigInteger", "- name : String"],
                        ["+ __str__() : String"])
    student, _ = box(845, 520, 250, "Student",
                     ["- id : BigInteger", "- department_id : FK", "- student_id_id : OneToOne",
                      "- first_name : String", "- last_name : String"],
                     ["+ __str__() : String"])
    user, _ = box(1145, 610, 200, "auth.User",
                  ["- id : BigInteger", "- username : String", "- email : Email"],
                  ["+ get_full_name() : String"])
    body = author+book+issue+fine+recommendation+stats+department+student+user
    body += association([(220,150),(275,150)],"author / books","1","0..*",247,132,228,144,267,144)
    body += association([(480,165),(535,165)],"book / issues","1","0..*",507,147,488,159,527,159)
    body += association([(780,180),(845,180)],"issue / fines","1","0..*",812,162,788,174,837,174)
    body += association([(657,305),(657,455),(970,455),(970,520)],"borrower / issues","0..*","1",815,443,672,320,985,513)
    body += association([(997,361),(997,430),(1065,430),(1065,520)],"student / fines","0..*","1",1080,418,1012,376,1080,513)
    body += association([(790,675),(845,675)],"department / students","1","0..*",817,657,798,669,837,669)
    body += association([(1095,675),(1145,675)],"profile / account","1","1",1120,657,1103,669,1137,669)
    body += association([(535,260),(510,260),(510,610)],"«signal» updates count","0..*","1",455,445,550,275,525,603,dashed=True)
    body += txt(152, 775, "Independent class — no model associations", 11, "middle", "bold")
    body += txt(690, 825, "Solid line = association   |   Dashed line = dependency   |   Numbers at both ends = multiplicity", 12, "middle", "bold")
    save("relationships_diagram.svg", "AEC Library - Complete Class Diagram", 1380, 860, body)

    # Library-only detail, including the external Student reference used by two FKs.
    author, _ = box(35, 80, 225, "Author",
                    ["- id : BigInteger", "- name : String", "- description : String"],
                    ["+ __str__() : String"])
    book, _ = box(330, 65, 255, "Book",
                  ["- id : BigInteger", "- name : String", "- image : ImageField",
                   "- category : String", "- author_id : FK"],
                  ["+ __str__() : String", "+ cloudinary_image_url : String"])
    issue, _ = box(665, 50, 280, "Issue",
                   ["- id : BigInteger", "- book_id : FK", "- student_id : FK",
                    "- created_at : DateTime", "- issued : Boolean",
                    "- issued_at : DateTime [0..1]", "- returned : Boolean",
                    "- return_date : DateTime [0..1]"],
                   ["+ days_no() : String", "+ __str__() : String"])
    fine, _ = box(665, 470, 315, "Fine",
                  ["- id : BigInteger", "- issue_id : FK", "- student_id : FK",
                   "- amount : Decimal", "- paid : Boolean", "- order_id : String [0..1]",
                   "- datetime_of_payment : DateTime [0..1]",
                   "- razorpay_order_id : String [0..1]",
                   "- razorpay_payment_id : String [0..1]",
                   "- razorpay_signature : String [0..1]"],
                  ["+ save() : void", "+ __str__() : String"])
    ext_student, _ = box(1045, 220, 225, "Student «external»",
                         ["- id : BigInteger", "«student app class»"],
                         ["+ __str__() : String"])
    stats, _ = box(330, 520, 255, "LibraryStat",
                   ["- id : BigInteger", "- borrowed_books : PositiveInteger"],
                   ["+ __str__() : String"])
    recommendation, _ = box(35, 450, 225, "BookRecommendation",
                            ["- id : BigInteger", "- title : String", "- author : String",
                             "- isbn : String", "- publisher : String",
                             "- book_format : Choice", "- created_at : DateTime"],
                            ["+ __str__() : String"])
    body = author+book+issue+fine+ext_student+stats+recommendation
    body += association([(260,150),(330,150)],"author / books","1","0..*",295,132,268,144,322,144)
    body += association([(585,165),(665,165)],"book / issues","1","0..*",625,147,593,159,657,159)
    body += association([(805,305),(805,470)],"issue / fines","1","0..*",875,395,820,320,790,463)
    body += association([(945,175),(1010,175),(1010,260),(1045,260)],"borrower / issues","0..*","1",1010,155,960,169,1037,254)
    body += association([(980,600),(1155,600),(1155,328)],"student / fines","0..*","1",1090,585,995,594,1170,343)
    body += association([(665,260),(625,260),(625,575),(585,575)],"«signal» updates count","0..*","1",625,430,680,275,600,569,dashed=True)
    body += txt(147, 760, "Independent class", 11, "middle", "bold")
    body += txt(650, 815, "ForeignKey associations use solid lines; the post-save signal is a dashed dependency.", 12, "middle", "bold")
    save("library_class_diagram.svg", "Library App - Class Diagram", 1310, 850, body)

    user, _ = box(35, 90, 260, "auth.User",
                  ["- id : BigInteger", "- username : String", "- email : Email", "- password : String"],
                  ["+ get_full_name() : String"])
    student, _ = box(390, 65, 300, "Student",
                     ["- id : BigInteger", "- student_id_id : OneToOne",
                      "- department_id : FK", "- first_name : String", "- last_name : String"],
                     ["+ __str__() : String"])
    department, _ = box(785, 100, 250, "Department",
                        ["- id : BigInteger", "- name : String"],
                        ["+ __str__() : String"])
    body = user+student+department
    body += association([(295,165),(390,165)],"account / profile","1","1",342,147,305,159,380,159)
    body += association([(690,165),(785,165)],"students / department","0..*","1",737,147,700,159,775,159)
    body += txt(535, 330, "Student.student_id is OneToOneField(User)   |   Student.department is ForeignKey(Department)", 12, "middle", "bold")
    save("student_class_diagram.svg", "Student App - Class Diagram", 1070, 370, body)


corrected_class_diagrams()
