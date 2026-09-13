import hashlib, sqlite3
from datetime import date
from io import BytesIO
from pathlib import Path
import pandas as pd
import streamlit as st

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False

DB = Path(__file__).with_name('hr_workforce.db')
st.set_page_config(page_title='HR Workforce Pro', page_icon='👥', layout='wide')
st.markdown('''<style>.block-container{padding-top:1.5rem}.hero{padding:26px 30px;border-radius:18px;background:linear-gradient(135deg,#ff7a18,#e52e71);color:white;margin-bottom:22px}.hero h1{font-size:38px;margin:0 0 8px}.hero p{font-size:17px;margin:0}.small{font-size:13px;opacity:.75}[data-testid="stMetricValue"]{white-space:nowrap!important;overflow:visible!important;text-overflow:clip!important}</style>''', unsafe_allow_html=True)

def hp(p): return hashlib.sha256(p.encode()).hexdigest()
def conn():
    c=sqlite3.connect(DB,check_same_thread=False); c.row_factory=sqlite3.Row; return c
def q(sql,params=(),fetch=False,many=False):
    c=conn(); cur=c.cursor(); cur.executemany(sql,params) if many else cur.execute(sql,params)
    out=[dict(x) for x in cur.fetchall()] if fetch else None; c.commit(); c.close(); return out

def init():
    c=conn(); x=c.cursor()
    x.executescript('''
    CREATE TABLE IF NOT EXISTS departments(id INTEGER PRIMARY KEY,name TEXT UNIQUE NOT NULL);
    CREATE TABLE IF NOT EXISTS employees(id INTEGER PRIMARY KEY,code TEXT UNIQUE NOT NULL,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,phone TEXT,dept_id INTEGER,designation TEXT,joining TEXT,status TEXT DEFAULT 'Active',manager TEXT,location TEXT,FOREIGN KEY(dept_id) REFERENCES departments(id));
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE,password_hash TEXT NOT NULL,role TEXT NOT NULL,employee_id INTEGER);
    CREATE TABLE IF NOT EXISTS performance(id INTEGER PRIMARY KEY,employee_id INTEGER,period TEXT,target REAL,achieved REAL,rating REAL,comments TEXT,UNIQUE(employee_id,period));
    CREATE TABLE IF NOT EXISTS attendance(id INTEGER PRIMARY KEY,employee_id INTEGER,day TEXT,status TEXT,notes TEXT,UNIQUE(employee_id,day));
    CREATE TABLE IF NOT EXISTS goals(id INTEGER PRIMARY KEY,employee_id INTEGER,title TEXT,target REAL,actual REAL,due TEXT,status TEXT);
    CREATE TABLE IF NOT EXISTS leave_records(id INTEGER PRIMARY KEY,employee_id INTEGER,type TEXT,start TEXT,end TEXT,days REAL,status TEXT,reason TEXT);
    ''')
    for d in ['Engineering','Sales & Marketing','Human Resources','Finance','Operations','IT Support']: x.execute('INSERT OR IGNORE INTO departments(name) VALUES(?)',(d,))
    if x.execute('SELECT COUNT(*) FROM employees').fetchone()[0]==0:
        ds={r['name']:r['id'] for r in x.execute('SELECT id,name FROM departments')}
        rows=[('EMP001','Arun Kumar','arun@example.com','9876543210',ds['Engineering'],'Software Engineer','2024-04-15','Active','Team Lead','Hyderabad'),('EMP002','Priya Sharma','priya@example.com','9876543211',ds['Sales & Marketing'],'Marketing Executive','2024-06-10','Active','Sales Manager','Bengaluru'),('EMP003','Rahul Reddy','rahul@example.com','9876543212',ds['Engineering'],'Python Developer','2025-01-06','Active','Engineering Manager','Hyderabad'),('EMP004','Sneha Rao','sneha@example.com','9876543213',ds['Human Resources'],'HR Executive','2024-08-19','Active','HR Manager','Vijayawada'),('EMP005','Ramu Marketing','ramu@example.com','9876543214',ds['Sales & Marketing'],'Marketing Executive','2025-03-03','Active','Sales Manager','Vijayawada'),('EMP006','Kiran Kumar','kiran@example.com','9876543215',ds['Finance'],'Finance Analyst','2023-11-20','Active','Finance Manager','Chennai'),('EMP007','Anjali Devi','anjali@example.com','9876543216',ds['Operations'],'Operations Executive','2024-02-12','Active','Operations Manager','Hyderabad'),('EMP008','Vikram Singh','vikram@example.com','9876543217',ds['IT Support'],'IT Support Engineer','2025-05-26','Active','IT Manager','Bengaluru')]
        x.executemany('INSERT INTO employees(code,name,email,phone,dept_id,designation,joining,status,manager,location) VALUES(?,?,?,?,?,?,?,?,?,?)',rows)
    em={r['code']:r['id'] for r in x.execute('SELECT id,code FROM employees')}
    for u in [('admin',hp('admin@123'),'HR Admin',None),('employee',hp('employee@123'),'Employee',em['EMP001'])]: x.execute('INSERT OR IGNORE INTO users(username,password_hash,role,employee_id) VALUES(?,?,?,?)',u)
    if x.execute('SELECT COUNT(*) FROM performance').fetchone()[0]==0:
        rows=[]
        vals={1:[92,108,105],2:[115,130,126],3:[88,96,103],4:[94,91,97],5:[72,81,76],6:[102,98,104],7:[110,107,111],8:[95,99,101]}
        for eid,avs in vals.items():
            for i,a in enumerate(avs,1): rows.append((eid,f'2026-0{i}',100 if eid!=5 else 200,a,4.0 if a>=90 else 3.0,'Demo performance record'))
        x.executemany('INSERT INTO performance(employee_id,period,target,achieved,rating,comments) VALUES(?,?,?,?,?,?)',rows)
    if x.execute('SELECT COUNT(*) FROM attendance').fetchone()[0]==0:
        rows=[]
        for eid in range(1,9):
            for d in range(1,11): rows.append((eid,f'2026-03-{d:02d}','Work From Home' if (eid+d)%7==0 else 'Present','Demo record'))
        x.executemany('INSERT INTO attendance(employee_id,day,status,notes) VALUES(?,?,?,?)',rows)
    c.commit(); c.close()

def edf(): return pd.read_sql_query('''SELECT e.code "Employee Code",e.name "Employee",e.email "Email",e.phone "Phone",d.name "Department",e.designation "Designation",e.joining "Joining Date",e.status "Status",e.manager "Manager",e.location "Location" FROM employees e LEFT JOIN departments d ON e.dept_id=d.id ORDER BY e.id''',conn())
def pdf(title,df):
    if not REPORTLAB_OK:return None
    b=BytesIO(); doc=SimpleDocTemplate(b,pagesize=A4,rightMargin=25,leftMargin=25,topMargin=25,bottomMargin=25); s=getSampleStyleSheet(); story=[Paragraph(title,s['Title']),Spacer(1,10)]
    data=[list(df.columns)]+df.fillna('').astype(str).values.tolist(); t=Table(data,repeatRows=1); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#243447')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.3,colors.grey),('FONTSIZE',(0,0),(-1,-1),7)])); story.append(t); doc.build(story); return b.getvalue()

def login():
    st.markdown('<div class="hero"><h1>HR Workforce Pro</h1><p>Employee Management • Performance • Attendance • Goals • HR Analytics</p></div>',unsafe_allow_html=True)
    _,c,_=st.columns([1,1.2,1]);
    with c:
        st.subheader('🔐 Secure Login'); u=st.text_input('Username'); p=st.text_input('Password',type='password')
        if st.button('Login',type='primary',use_container_width=True):
            r=q('SELECT * FROM users WHERE username=? AND password_hash=?',(u.strip(),hp(p)),True)
            if r: st.session_state.update(auth=True,user=r[0]['username'],role=r[0]['role'],eid=r[0]['employee_id']); st.rerun()
            else: st.error('Invalid username or password.')
        st.info('HR Admin: admin / admin@123\n\nEmployee: employee / employee@123')

def performance():
    df=pd.read_sql_query('''SELECT e.code "Employee Code",e.name "Employee",d.name "Department",p.period "Period",p.target "Target",p.achieved "Achieved",ROUND(CASE WHEN p.target>0 THEN p.achieved*100.0/p.target ELSE 0 END,2) "Achievement %",CASE WHEN p.achieved>=p.target THEN 'YES' ELSE 'NO' END "Target Reach",p.rating "Rating",p.comments "Comments" FROM performance p JOIN employees e ON p.employee_id=e.id LEFT JOIN departments d ON e.dept_id=d.id ORDER BY p.period DESC,p.achieved DESC''',conn()); return df

def attendance(): return pd.read_sql_query('''SELECT e.code "Employee Code",e.name "Employee",d.name "Department",a.day "Date",a.status "Status",a.notes "Notes" FROM attendance a JOIN employees e ON a.employee_id=e.id LEFT JOIN departments d ON e.dept_id=d.id ORDER BY a.day DESC''',conn())
def goals(): return pd.read_sql_query('''SELECT e.code "Employee Code",e.name "Employee",g.title "Goal",g.target "Target",g.actual "Actual",ROUND(CASE WHEN g.target>0 THEN g.actual*100.0/g.target ELSE 0 END,2) "Progress %",g.due "Due Date",g.status "Status" FROM goals g JOIN employees e ON g.employee_id=e.id ORDER BY g.due''',conn())

def overview():
    e=edf(); p=performance(); a=attendance();
    st.markdown('<div class="hero"><h1>HR Workforce & Performance Management</h1><p>Workforce insights for HR review, development and operational visibility.</p></div>',unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4); c1.metric('Active Employees',int((e.Status=='Active').sum())); c2.metric('Performance Records',len(p)); c3.metric('Avg Achievement',f'{p["Achievement %"].mean():.1f}%'); c4.metric('Attendance Rate',f'{a.Status.isin(["Present","Work From Home"]).mean()*100:.1f}%')
    st.subheader('📈 Performance Trend'); st.line_chart(p.groupby('Period')['Achievement %'].mean())
    st.subheader('🏆 Department Snapshot'); st.dataframe(p.groupby('Department').agg(Employees=('Employee','nunique'),Avg_Achievement=('Achievement %','mean'),Target_Reached=('Target Reach',lambda x:(x=='YES').sum())).reset_index().round(1),use_container_width=True,hide_index=True)
    st.caption('This application is decision-support software; HR should use human review for employment decisions.')

def employees():
    st.title('👥 Employee Management'); df=edf(); st.dataframe(df,use_container_width=True,hide_index=True)
    with st.expander('➕ Add Employee'):
        ds=q('SELECT * FROM departments ORDER BY name',fetch=True)
        with st.form('add'):
            a,b=st.columns(2); code=a.text_input('Employee Code'); name=b.text_input('Full Name'); email=a.text_input('Email'); phone=b.text_input('Phone'); dep=a.selectbox('Department',[x['name'] for x in ds]); des=b.text_input('Designation'); joining=a.date_input('Joining Date',date.today()); manager=b.text_input('Manager'); location=a.text_input('Location')
            if st.form_submit_button('Create Employee',type='primary'):
                try:
                    did=next(x['id'] for x in ds if x['name']==dep); q('INSERT INTO employees(code,name,email,phone,dept_id,designation,joining,manager,location) VALUES(?,?,?,?,?,?,?,?,?)',(code,name,email,phone,did,des,joining.isoformat(),manager,location)); st.success('Employee created.'); st.rerun()
                except Exception as ex: st.error(str(ex))

def performance_page():
    st.title('📊 Performance Management'); df=performance(); st.dataframe(df,use_container_width=True,hide_index=True)
    em=q('SELECT id,code,name FROM employees ORDER BY name',fetch=True)
    with st.form('perf'):
        label=st.selectbox('Employee',[f"{x['code']} — {x['name']}" for x in em]); a,b,c=st.columns(3); period=a.text_input('Period','2026-04'); target=b.number_input('Target',0.0,10000000.0,100.0); achieved=c.number_input('Achieved',0.0,10000000.0,0.0); rating=st.slider('Rating',0.,5.,3.,.5); comments=st.text_area('Comments')
        if st.form_submit_button('Save Performance',type='primary'):
            eid=next(x['id'] for x in em if f"{x['code']} — {x['name']}"==label); q('INSERT INTO performance(employee_id,period,target,achieved,rating,comments) VALUES(?,?,?,?,?,?) ON CONFLICT(employee_id,period) DO UPDATE SET target=excluded.target,achieved=excluded.achieved,rating=excluded.rating,comments=excluded.comments',(eid,period,target,achieved,rating,comments)); st.success('Saved.'); st.rerun()

def attendance_page():
    st.title('📅 Attendance Management'); st.dataframe(attendance(),use_container_width=True,hide_index=True); em=q('SELECT id,code,name FROM employees ORDER BY name',fetch=True)
    with st.form('att'):
        label=st.selectbox('Employee',[f"{x['code']} — {x['name']}" for x in em]); d=st.date_input('Date',date.today()); status=st.selectbox('Status',['Present','Absent','Work From Home','Leave']); notes=st.text_input('Notes')
        if st.form_submit_button('Save Attendance',type='primary'):
            eid=next(x['id'] for x in em if f"{x['code']} — {x['name']}"==label); q('INSERT INTO attendance(employee_id,day,status,notes) VALUES(?,?,?,?) ON CONFLICT(employee_id,day) DO UPDATE SET status=excluded.status,notes=excluded.notes',(eid,d.isoformat(),status,notes)); st.success('Saved.'); st.rerun()

def goals_page():
    st.title('🎯 Goals & Target Tracking'); st.dataframe(goals(),use_container_width=True,hide_index=True); em=q('SELECT id,code,name FROM employees ORDER BY name',fetch=True)
    with st.form('goal'):
        label=st.selectbox('Employee',[f"{x['code']} — {x['name']}" for x in em]); title=st.text_input('Goal title'); a,b,c=st.columns(3); target=a.number_input('Target value',0.,10000000.,100.); actual=b.number_input('Actual value',0.,10000000.,0.); due=c.date_input('Due date',date.today()); status=st.selectbox('Status',['Not Started','In Progress','Completed','On Hold'])
        if st.form_submit_button('Create Goal',type='primary'):
            eid=next(x['id'] for x in em if f"{x['code']} — {x['name']}"==label); q('INSERT INTO goals(employee_id,title,target,actual,due,status) VALUES(?,?,?,?,?,?)',(eid,title,target,actual,due.isoformat(),status)); st.success('Goal created.'); st.rerun()

def leave_page():
    st.title('📝 Leave Records'); df=pd.read_sql_query('''SELECT e.code "Employee Code",e.name "Employee",l.type "Leave Type",l.start "Start",l.end "End",l.days "Days",l.status "Status",l.reason "Reason" FROM leave_records l JOIN employees e ON l.employee_id=e.id ORDER BY l.start DESC''',conn()); st.dataframe(df,use_container_width=True,hide_index=True); em=q('SELECT id,code,name FROM employees ORDER BY name',fetch=True)
    with st.form('leave'):
        label=st.selectbox('Employee',[f"{x['code']} — {x['name']}" for x in em]); typ=st.selectbox('Leave Type',['Casual Leave','Sick Leave','Earned Leave','Work From Home','Other']); a,b=st.columns(2); start=a.date_input('Start',date.today()); end=b.date_input('End',date.today()); reason=st.text_area('Reason')
        if st.form_submit_button('Submit Leave',type='primary'):
            eid=next(x['id'] for x in em if f"{x['code']} — {x['name']}"==label); days=max(1,(end-start).days+1); q("INSERT INTO leave_records(employee_id,type,start,end,days,status,reason) VALUES(?,?,?,?,?,'Pending',?)",(eid,typ,start.isoformat(),end.isoformat(),days,reason)); st.success('Leave submitted.'); st.rerun()

def reports():
    st.title('📄 HR Reports'); choices={'Employee Directory':edf(),'Performance Report':performance(),'Attendance Report':attendance(),'Goals Report':goals()}; name=st.selectbox('Report',list(choices)); df=choices[name]; st.dataframe(df,use_container_width=True,hide_index=True); st.download_button('⬇️ Download CSV',df.to_csv(index=False).encode(),name.lower().replace(' ','_')+'.csv','text/csv')
    if REPORTLAB_OK: st.download_button('📄 Download PDF',pdf(name,df.head(40)),name.lower().replace(' ','_')+'.pdf','application/pdf')

def employee_view():
    eid=st.session_state.eid; emp=q('SELECT e.*,d.name dept FROM employees e LEFT JOIN departments d ON e.dept_id=d.id WHERE e.id=?',(eid,),True)[0]; p=performance(); p=p[p['Employee Code']==emp['code']]; a=attendance(); a=a[a['Employee Code']==emp['code']]
    st.markdown(f'<div class="hero"><h1>Welcome, {emp["name"]}</h1><p>{emp["designation"]} • {emp["dept"]}</p></div>',unsafe_allow_html=True); c1,c2,c3=st.columns(3); c1.metric('Performance Records',len(p)); c2.metric('Avg Achievement',f'{p["Achievement %"].mean():.1f}%' if len(p) else '0%'); c3.metric('Attendance Rate',f'{a.Status.isin(["Present","Work From Home"]).mean()*100:.1f}%' if len(a) else '0%'); st.dataframe(p,use_container_width=True,hide_index=True)

def main():
    if not st.session_state.get('auth'):
        login(); return
    st.sidebar.title('HR Workforce Pro'); st.sidebar.caption(f"Signed in as **{st.session_state.user}**")
    if st.sidebar.button('Logout',use_container_width=True): st.session_state.clear(); st.rerun()
    if st.session_state.role=='HR Admin':
        page=st.sidebar.radio('Navigation',['🏠 HR Overview','👥 Employees','📊 Performance','📅 Attendance','🎯 Goals','📝 Leave Records','📄 Reports'])
        {'🏠 HR Overview':overview,'👥 Employees':employees,'📊 Performance':performance_page,'📅 Attendance':attendance_page,'🎯 Goals':goals_page,'📝 Leave Records':leave_page,'📄 Reports':reports}[page]()
    else:
        page=st.sidebar.radio('Navigation',['🏠 My Overview','📊 My Performance','📅 My Attendance','🎯 My Goals','📄 My Report']); employee_view()
        eid=st.session_state.eid; code=q('SELECT code FROM employees WHERE id=?',(eid,),True)[0]['code']
        if page=='📊 My Performance': st.dataframe(performance().query('`Employee Code`==@code'),use_container_width=True,hide_index=True)
        elif page=='📅 My Attendance': st.dataframe(attendance().query('`Employee Code`==@code'),use_container_width=True,hide_index=True)
        elif page=='🎯 My Goals': st.dataframe(goals().query('`Employee Code`==@code'),use_container_width=True,hide_index=True)

init(); main()
