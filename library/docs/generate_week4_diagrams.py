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


def save(name, title, width, height, body):
    (OUT / name).write_text(svg(title, width, height, body), encoding="utf-8")


def structural():
    nodes = []
    author, _ = box(40, 75, 255, "Author", ["- id : BigInteger", "- name : String", "- description : String"], ["+ __str__() : String"])
    book, _ = box(365, 60, 285, "Book", ["- id : BigInteger", "- name : String", "- image : ImageField", "- category : String", "- author : Author"], ["+ __str__() : String", "+ image_url() : String"])
    issue, issue_h = box(725, 55, 310, "Issue", ["- id : BigInteger", "- student : Student", "- book : Book", "- created_at : DateTime", "- issued : Boolean", "- issued_at : DateTime", "- returned : Boolean", "- return_date : DateTime"], ["+ days_no() : String", "+ __str__() : String"])
    fine, _ = box(705, 390, 330, "Fine", ["- id : BigInteger", "- student : Student", "- issue : Issue", "- amount : Decimal", "- paid : Boolean", "- order_id : String", "- payment_id : String"], ["+ save() : void", "+ __str__() : String"])
    stats, _ = box(190, 405, 275, "LibraryStat", ["- id : BigInteger", "- borrowed_books : Integer"], ["+ __str__() : String"])
    nodes += [author, book, issue, fine, stats, edge(295, 150, 365, 150, "writes", "1", "0..*", open_arrow=True), edge(650, 165, 725, 165, "issues", "1", "0..*", open_arrow=True), edge(880, 55+issue_h, 870, 390, "generates", "1", "0..1", open_arrow=True)]
    save("library_class_diagram.svg", "Library App - Class Diagram", 1080, 700, "".join(nodes))

    user, _ = box(45, 90, 280, "auth.User", ["- id : BigInteger", "- username : String", "- email : Email", "- password : String"], ["+ get_full_name() : String"])
    student, _ = box(405, 70, 315, "Student", ["- id : BigInteger", "- student_id : User", "- department : Department", "- first_name : String", "- last_name : String"], ["+ __str__() : String"])
    dept, _ = box(800, 105, 250, "Department", ["- id : BigInteger", "- name : String"], ["+ __str__() : String"])
    body = user+student+dept+edge(325,170,405,170,"profile","1","1",open_arrow=True)+edge(720,175,800,175,"belongs to","0..*","1",open_arrow=True)
    save("student_class_diagram.svg", "Student App - Class Diagram", 1090, 420, body)

    body = '<rect x="30" y="55" width="680" height="520" fill="#fff"/><rect x="740" y="55" width="410" height="520" fill="#fff"/>'+txt(50,82,"<<package>> library",15,weight="bold")+txt(760,82,"<<package>> student",15,weight="bold")
    positions = [(55,115,"Author"),(270,115,"Book"),(490,115,"Issue"),(270,345,"Fine"),(55,345,"LibraryStat"),(770,125,"Student"),(770,355,"Department"),(950,355,"auth.User")]
    for x,y,name in positions:
        node,_=box(x,y,165,name,["- id : BigInteger"],["+ __str__() : String"]); body += node
    body += edge(220,165,270,165,"writes","1","*",open_arrow=True)+edge(435,165,490,165,"records","1","*",open_arrow=True)+edge(655,180,770,180,"borrower","*","1",dashed=True,open_arrow=True)+edge(575,250,435,345,"fine","1","0..1",open_arrow=True)+edge(850,355,850,285,"department","*","1",open_arrow=True)+edge(935,405,950,405,"account","1","1",open_arrow=True)
    save("relationships_diagram.svg", "Library and Student Apps - Package Diagram", 1180, 610, body)


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
