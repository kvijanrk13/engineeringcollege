from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parents[2] / "static" / "docs" / "images"
FONT = "Arial,Helvetica,sans-serif"


def txt(x, y, value, size=14, anchor="start", weight="normal"):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="#111" stroke="none">{escape(value)}</text>'


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
