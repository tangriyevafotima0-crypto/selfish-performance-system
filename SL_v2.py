#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 SELFISH v2.0 — Personal Performance System
 v2.0: Startup Folder, AppData storage, 90-day history,
       icon, uninstall, Strategic Planning Visual Tool
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading, time, os, sys, json, re, random, math
import subprocess, atexit, ctypes, ctypes.wintypes as wt
import hashlib, base64, urllib.request, urllib.error, tempfile
from datetime import datetime, date as ddate, timedelta

# ══════════════════════════════════════════════════════════════
#  PATHS
# ══════════════════════════════════════════════════════════════
if getattr(sys, 'frozen', False):
    APP_DIR  = os.path.dirname(sys.executable)
    APP_PATH = sys.executable
else:
    APP_DIR  = os.path.dirname(os.path.abspath(__file__))
    APP_PATH = os.path.abspath(__file__)

_APPDATA = os.environ.get('APPDATA', os.path.expanduser('~'))
DATA_DIR  = os.path.join(_APPDATA, 'SL_Selfish')
os.makedirs(DATA_DIR, exist_ok=True)

CFG_FILE      = os.path.join(APP_DIR,  'sl_config.json')
TASKS_FILE    = os.path.join(DATA_DIR, 'sl_tasks.json')
JOUR_FILE     = os.path.join(DATA_DIR, 'sl_journal.json')
NOTES_FILE    = os.path.join(DATA_DIR, 'sl_vault.enc')
APPLOG_FILE   = os.path.join(DATA_DIR, 'sl_applog.json')
POWERLOG_FILE = os.path.join(DATA_DIR, 'sl_powerlog.json')
LOG_FILE      = os.path.join(DATA_DIR, 'sl_log.txt')
HOSTS_FILE    = r'C:\Windows\System32\drivers\etc\hosts'
HOSTS_BK      = os.path.join(DATA_DIR, '.sl_hosts_bk')
STARTUP_FOLDER= os.path.join(_APPDATA, r'Microsoft\Windows\Start Menu\Programs\Startup')

# ══════════════════════════════════════════════════════════════
#  COLORS
# ══════════════════════════════════════════════════════════════
C = {
    'bg':'#04040a','card':'#07070f','card2':'#090914','inp':'#0c0c18',
    'brd':'#111124','brd2':'#181830','hov':'#0f0f1e','sel':'#12102e',
    'acc':'#4f46e5','acc2':'#6366f1','acc3':'#818cf8',
    'grn':'#059669','grn2':'#10b981','grn3':'#34d399',
    'red':'#b91c1c','red2':'#dc2626','red3':'#ef4444',
    'yel':'#b45309','yel2':'#d97706','yel3':'#f59e0b',
    'vio':'#7c3aed','vio2':'#8b5cf6',
    'blu':'#2563eb','blu2':'#3b82f6',
    'txt':'#e2e8f0','sub':'#3d4468','mut':'#0f1020',
    'wht':'#f8fafc','dim':'#94a3b8',
}

_ICON_B64 = (
    'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAABS0lEQVR42u3bPQ6DMAyG'
    'YQYkpC69Vdeeib3X7B26tWJFUJzYTuLkHbxVgu8pf0rsaZ5v08g1AVD5BJ6P97d7gC1k'
    'boUF0IQuiVE99LLcq2IUCb+FzC1vBLfgmtCpGFUASgb3hDALXyK4BMIdoJXwVgihw1sg'
    'ZIdvIfgVhBlAhPC5CF2Fz0FIBlhfH3UdnXTKb4sBeIQvAZCCIAawCl8KYI+QDLC/7yMC'
    'SBDED74eAI4QRP9+ZICrq0ANYPXqagbg7J0fGeAfAgAACML3AHCGAAAAAACgAojwJQiA'
    'BOBq1acHgCMErgAAhADeT3YAAAAAgOoA1ggtAagXRAAYBcASYYhlce8vQYvjqABq7wxp'
    'j5O1M9TS3qAlQMjdYU2Zbo/X6g+wCJ8N0EKHiGd4eoToEqNPkE5ReoXpFmdegIkRZoaY'
    'GmNukMlRZodHrR8VQ8nzqZDKwwAAAABJRU5ErkJggg=='
)

BLOCKED = [
    'instagram.com','www.instagram.com','tiktok.com','www.tiktok.com',
    'facebook.com','www.facebook.com','snapchat.com','twitter.com',
    'x.com','reddit.com','twitch.tv','pinterest.com','vk.com','ok.ru',
    'pornhub.com','xvideos.com','xnxx.com','xhamster.com',
    'chaturbate.com','stripchat.com','livejasmin.com',
]

QUOTES = [
    ('🔥','FOCUS ZONE','Har o\'tgan daqiqa — kelajakka investitsiya.'),
    ('💎','DISCIPLINE = FREEDOM','Muvaffaqiyatlilar ko\'p narsadan voz kechadilar.'),
    ('🚀','COMPOUND EFFECT','Har kungi FOCUS = Yillardagi ulkan natija.'),
    ('⏳','TIME = CAPITAL','Bugungi har soat — ertangi resurs.'),
    ('🧠','BRAIN UPGRADE','Instagram kutadi. Maqsadlaring kutmaydi.'),
    ('🎯','MISSION MODE','30 sekund mazza vs butun umr. O\'zing bilyapsan.'),
]

DEF_CFG = {
    'password':'SL2024',
    'vault_pw_hash':hashlib.sha256(b'VAULT2024').hexdigest(),
    'notif_min':15,'pomo_work':25,'pomo_break':5,
    'block_sites':True,
    'dl_path':os.path.join(os.path.expanduser('~'),'Downloads'),
    'ai_api_key':'','ai_model':'claude-haiku-4-5-20251001','track_apps':True,
}

# ══════════════════════════════════════════════════════════════
#  WIN32
# ══════════════════════════════════════════════════════════════
try:
    _u32=ctypes.windll.user32; _k32=ctypes.windll.kernel32; _WIN=True
except: _WIN=False

def get_foreground_app():
    if not _WIN: return None,None
    try:
        hwnd=_u32.GetForegroundWindow()
        if not hwnd: return None,None
        ln=_u32.GetWindowTextLengthW(hwnd)+1
        tb=ctypes.create_unicode_buffer(ln)
        _u32.GetWindowTextW(hwnd,tb,ln)
        pid=wt.DWORD()
        _u32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
        h=_k32.OpenProcess(0x0400,False,pid.value)
        name=None
        if h:
            b=ctypes.create_unicode_buffer(512); s=wt.DWORD(512)
            _k32.QueryFullProcessImageNameW(h,0,b,ctypes.byref(s))
            _k32.CloseHandle(h)
            if b.value: name=os.path.basename(b.value)
        return name,tb.value
    except: return None,None

def is_admin():
    try: return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except: return False

def req_admin():
    if not is_admin():
        try:
            ret=ctypes.windll.shell32.ShellExecuteW(
                None,'runas',sys.executable,
                ' '.join(f'"{a}"' for a in sys.argv),None,1)
            if int(ret)>32: sys.exit(0)
        except: pass

# ══════════════════════════════════════════════════════════════
#  STARTUP — Startup Folder (kechikishsiz)
# ══════════════════════════════════════════════════════════════
def _make_lnk(target, lnk_path):
    vbs=(f'Set s=WScript.CreateObject("WScript.Shell")\n'
         f'Set l=s.CreateShortcut("{lnk_path}")\n'
         f'l.TargetPath="{target}"\n'
         f'l.WorkingDirectory="{os.path.dirname(target)}"\n'
         f'l.Save\n')
    try:
        with tempfile.NamedTemporaryFile(suffix='.vbs',mode='w',delete=False,encoding='utf-8') as f:
            f.write(vbs); p=f.name
        subprocess.run(['wscript',p],capture_output=True,creationflags=0x08000000,timeout=15)
        return os.path.exists(lnk_path)
    except: return False
    finally:
        try: os.unlink(p)
        except: pass

def register_startup():
    exe = APP_PATH if getattr(sys,'frozen',False) else sys.executable
    cmd = f'"{APP_PATH}"' if getattr(sys,'frozen',False) else f'"{sys.executable.replace("python.exe","pythonw.exe")}" "{APP_PATH}"'
    # 1) Startup Folder
    try:
        lnk=os.path.join(STARTUP_FOLDER,'SL_Selfish.lnk')
        if not os.path.exists(lnk):
            if _make_lnk(exe,lnk): log('Startup: Folder'); return True
    except Exception as e: log(f'Startup folder: {e}')
    # 2) Task Scheduler
    try:
        r=subprocess.run(['schtasks','/create','/tn','SL_Selfish','/tr',cmd,
                          '/sc','ONLOGON','/delay','0000:00','/f','/rl','HIGHEST'],
                         capture_output=True,creationflags=0x08000000,timeout=15)
        if r.returncode==0: log('Startup: TaskSched'); return True
    except: pass
    # 3) Registry
    try:
        import winreg
        k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Run',0,winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k,'SL_Selfish',0,winreg.REG_SZ,cmd)
        winreg.CloseKey(k); log('Startup: Registry'); return True
    except: return False

def unregister_startup():
    try:
        lnk=os.path.join(STARTUP_FOLDER,'SL_Selfish.lnk')
        if os.path.exists(lnk): os.remove(lnk)
    except: pass
    try:
        subprocess.run(['schtasks','/delete','/tn','SL_Selfish','/f'],
                       capture_output=True,creationflags=0x08000000,timeout=10)
    except: pass
    try:
        import winreg
        k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Run',0,winreg.KEY_SET_VALUE)
        try: winreg.DeleteValue(k,'SL_Selfish')
        except: pass
        winreg.CloseKey(k)
    except: pass

# ══════════════════════════════════════════════════════════════
#  UTILITIES
# ══════════════════════════════════════════════════════════════
def log(msg):
    try:
        with open(LOG_FILE,'a',encoding='utf-8') as f:
            f.write(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}\n')
    except: pass

def load_json(path,default):
    try:
        if os.path.exists(path):
            with open(path,'r',encoding='utf-8') as f: return json.load(f)
    except: pass
    return default

def save_json(path,data):
    try:
        with open(path,'w',encoding='utf-8') as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
    except: pass

def now_str(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def date_str(): return datetime.now().strftime('%d.%m.%Y')

def fmt_time(secs):
    s=max(0,int(secs)); h,r=divmod(s,3600); m,s=divmod(r,60)
    return f'{h:02d}:{m:02d}:{s:02d}' if h else f'{m:02d}:{s:02d}'

def fmt_dur(secs):
    s=max(0,int(secs))
    if s<60: return f'{s}s'
    m=s//60
    if m<60: return f'{m}m {s%60}s'
    return f'{m//60}h {m%60}m'

def ph(pw): return hashlib.sha256(pw.encode()).hexdigest()

# ══════════════════════════════════════════════════════════════
#  HOSTS BLOCKING
# ══════════════════════════════════════════════════════════════
def block_sites():
    if not is_admin(): return False
    try:
        with open(HOSTS_FILE,'r',encoding='utf-8',errors='ignore') as f: orig=f.read()
        with open(HOSTS_BK,'w',encoding='utf-8') as f: f.write(orig)
        clean=re.sub(r'\n?# ==SL_START==.*?# ==SL_END==\n?','',orig,flags=re.DOTALL)
        blk='\n# ==SL_START==\n'+''.join(f'0.0.0.0  {s}\n' for s in BLOCKED)+'# ==SL_END==\n'
        with open(HOSTS_FILE,'w',encoding='utf-8') as f: f.write(clean+blk)
        subprocess.run(['ipconfig','/flushdns'],capture_output=True,creationflags=0x08000000)
        return True
    except Exception as e: log(f'block: {e}'); return False

def unblock_sites():
    try:
        if os.path.exists(HOSTS_BK):
            with open(HOSTS_BK,'r',encoding='utf-8') as f: orig=f.read()
            with open(HOSTS_FILE,'w',encoding='utf-8') as f: f.write(orig)
            try: os.remove(HOSTS_BK)
            except: pass
        else:
            with open(HOSTS_FILE,'r',encoding='utf-8',errors='ignore') as f: c=f.read()
            c=re.sub(r'\n?# ==SL_START==.*?# ==SL_END==\n?','',c,flags=re.DOTALL)
            with open(HOSTS_FILE,'w',encoding='utf-8') as f: f.write(c)
        subprocess.run(['ipconfig','/flushdns'],capture_output=True,creationflags=0x08000000)
    except: pass

def do_shutdown():
    unblock_sites()
    try: subprocess.Popen(['shutdown','/s','/t','5'])
    except: pass

# ══════════════════════════════════════════════════════════════
#  POWER LOG
# ══════════════════════════════════════════════════════════════
class PowerLog:
    def __init__(self):
        self.events=load_json(POWERLOG_FILE,[])
        self._boot_ts=now_str(); self._boot_time=time.time()
        self.events.append({'event':'boot','time':self._boot_ts})
        self._save()
    def record_shutdown(self):
        up=time.time()-self._boot_time
        self.events.append({'event':'shutdown','time':now_str(),'uptime_s':int(up),'uptime':fmt_dur(up)})
        for ev in reversed(self.events):
            if ev['event']=='boot' and ev['time']==self._boot_ts:
                ev['uptime_s']=int(up); ev['uptime']=fmt_dur(up); break
        self._save()
    def get_recent(self,n=200): return self.events[-n:]
    def _save(self): save_json(POWERLOG_FILE,self.events[-500:])

# ══════════════════════════════════════════════════════════════
#  APP TRACKER
# ══════════════════════════════════════════════════════════════
class AppTracker:
    IGNORE={'SL.exe','sl.exe','python.exe','pythonw.exe','Taskmgr.exe','SearchApp.exe'}
    def __init__(self,enabled=True):
        self.enabled=enabled
        self._data=load_json(APPLOG_FILE,{})
        self._running=False; self._lock=threading.Lock()
        self._last_app=None; self._last_switch=time.time()
    def start(self):
        if not self.enabled: return
        self._running=True
        threading.Thread(target=self._loop,daemon=True).start()
    def stop(self):
        self._running=False; self._flush(); self._save()
    def _loop(self):
        while self._running:
            try:
                app,_=get_foreground_app()
                if app and app not in self.IGNORE:
                    now=time.time()
                    if app!=self._last_app:
                        if self._last_app: self._add(self._last_app,now-self._last_switch)
                        self._last_app=app; self._last_switch=now
                time.sleep(1.5)
                if int(time.time())%300<2: self._flush(); self._save()
            except: time.sleep(5)
    def _flush(self):
        if self._last_app:
            self._add(self._last_app,time.time()-self._last_switch)
            self._last_switch=time.time()
    def _add(self,app,secs):
        today=ddate.today().isoformat()
        with self._lock:
            if today not in self._data: self._data[today]={}
            self._data[today][app]=self._data[today].get(app,0)+secs
    def _save(self):
        with self._lock:
            keys=sorted(self._data.keys())[-90:]
            save_json(APPLOG_FILE,{k:self._data[k] for k in keys})
    def get_date(self,dt):
        with self._lock: return sorted(self._data.get(dt,{}).items(),key=lambda x:x[1],reverse=True)
    def get_available_dates(self):
        with self._lock: return sorted(self._data.keys(),reverse=True)

# ══════════════════════════════════════════════════════════════
#  ENCRYPTION
# ══════════════════════════════════════════════════════════════
def _derive(pw,salt): return hashlib.pbkdf2_hmac('sha256',pw.encode(),salt,200_000)
def enc(data,pw):
    raw=json.dumps(data,ensure_ascii=False).encode(); salt=os.urandom(32); key=_derive(pw,salt)
    full=b''; seed=key
    while len(full)<len(raw): seed=hashlib.sha256(seed).digest(); full+=seed
    full=full[:len(raw)]
    return base64.urlsafe_b64encode(salt+bytes(a^b for a,b in zip(raw,full))).decode()
def dec(enc_str,pw):
    raw=base64.urlsafe_b64decode(enc_str.encode()); salt=raw[:32]; data=raw[32:]; key=_derive(pw,salt)
    full=b''; seed=key
    while len(full)<len(data): seed=hashlib.sha256(seed).digest(); full+=seed
    full=full[:len(data)]
    return json.loads(bytes(a^b for a,b in zip(data,full)).decode())

# ══════════════════════════════════════════════════════════════
#  DATA MANAGERS
# ══════════════════════════════════════════════════════════════
class CfgMgr:
    def __init__(self): self.d={**DEF_CFG,**load_json(CFG_FILE,{})}
    def get(self,k,d=None): return self.d.get(k,d)
    def set(self,k,v): self.d[k]=v; save_json(CFG_FILE,self.d)
    def save(self): save_json(CFG_FILE,self.d)

class TaskMgr:
    def __init__(self):
        self.sessions=load_json(TASKS_FILE,[]); self.cur=None; self._start_ts=0.0
    def new(self,goal='',hours=0):
        self._start_ts=time.time()
        self.cur={'id':datetime.now().strftime('%Y%m%d_%H%M%S'),
                  'date':datetime.now().strftime('%Y-%m-%d'),
                  'start_time':now_str(),'planned_h':hours,'actual_h':0,
                  'goal':goal,'tasks':[]}
    def add(self,text):
        if self.cur and text.strip():
            self.cur['tasks'].append({'text':text.strip(),'done':False,'added':now_str(),'done_at':None})
            self._save()
    def complete(self,i):
        if self.cur and 0<=i<len(self.cur['tasks']):
            t=self.cur['tasks'][i]; t['done']=True; t['done_at']=now_str(); self._save()
    def uncomplete(self,i):
        if self.cur and 0<=i<len(self.cur['tasks']):
            t=self.cur['tasks'][i]; t['done']=False; t['done_at']=None; self._save()
    def end(self):
        if self.cur:
            s=time.time()-self._start_ts
            self.cur.update({'actual_h':round(s/3600,4),'actual_s':int(s),'end_time':now_str(),
                             'summary':f'{sum(1 for t in self.cur["tasks"] if t["done"])}/{len(self.cur["tasks"])}'})
            self.sessions.append(self.cur); save_json(TASKS_FILE,self.sessions); self.cur=None
    def _save(self): save_json(TASKS_FILE,self.sessions+([self.cur] if self.cur else []))

class JournalMgr:
    def __init__(self): self.entries=load_json(JOUR_FILE,[])
    def add(self,content,goal='',actual_h=0):
        if not content.strip(): return False
        e={'id':len(self.entries)+1,'datetime':now_str(),
           'date':datetime.now().strftime('%Y-%m-%d'),
           'time':datetime.now().strftime('%H:%M'),
           'actual_h':actual_h,'goal':goal,'content':content.strip()}
        self.entries.append(e); save_json(JOUR_FILE,self.entries); return True

class VaultMgr:
    def __init__(self): self._notes=None; self._pw=None
    def unlock(self,pw):
        if not os.path.exists(NOTES_FILE):
            self._pw=pw; self._notes={'notes':[],'plans':[],'visual_plans':[],'ai_history':[]}; return True
        try:
            with open(NOTES_FILE,'r') as f: s=f.read().strip()
            self._notes=dec(s,pw); self._notes.setdefault('visual_plans',[]); self._pw=pw; return True
        except: return False
    def lock(self): self._flush(); self._notes=None; self._pw=None
    def is_open(self): return self._notes is not None
    def add_note(self,title,cat,content):
        n={'id':len(self._notes['notes'])+1,'title':title,'category':cat,
           'content':content,'created':now_str(),'updated':now_str()}
        self._notes['notes'].append(n); self._flush(); return n['id']
    def update_note(self,i,title,cat,content):
        if 0<=i<len(self._notes['notes']):
            self._notes['notes'][i].update({'title':title,'category':cat,'content':content,'updated':now_str()})
            self._flush()
    def delete_note(self,i):
        if 0<=i<len(self._notes['notes']): self._notes['notes'].pop(i); self._flush()
    def get_notes(self): return (self._notes or {}).get('notes',[])
    def save_plan(self,title,content):
        self._notes.setdefault('plans',[]).append({'title':title,'content':content,'saved':now_str()})
        self._flush()
    def get_plans(self): return (self._notes or {}).get('plans',[])
    def save_visual_plan(self,plan_dict):
        plans=self._notes.setdefault('visual_plans',[])
        for i,p in enumerate(plans):
            if p.get('title')==plan_dict.get('title'): plans[i]=plan_dict; self._flush(); return
        plans.append(plan_dict); self._flush()
    def get_visual_plans(self): return (self._notes or {}).get('visual_plans',[])
    def delete_visual_plan(self,title):
        self._notes['visual_plans']=[p for p in self._notes.get('visual_plans',[]) if p.get('title')!=title]
        self._flush()
    def _flush(self):
        if self._notes and self._pw:
            with open(NOTES_FILE,'w') as f: f.write(enc(self._notes,self._pw))

# ══════════════════════════════════════════════════════════════
#  AI CALL
# ══════════════════════════════════════════════════════════════
def ai_call(api_key,messages,system='',model='claude-haiku-4-5-20251001',max_tokens=1500):
    if not api_key: return '❌ API kalit yo\'q.\nconsole.anthropic.com dan kalit oling.'
    payload={'model':model,'max_tokens':max_tokens,'messages':messages}
    if system: payload['system']=system
    data=json.dumps(payload).encode()
    req=urllib.request.Request('https://api.anthropic.com/v1/messages',data=data,method='POST')
    req.add_header('Content-Type','application/json')
    req.add_header('anthropic-version','2023-06-01')
    req.add_header('x-api-key',api_key)
    try:
        with urllib.request.urlopen(req,timeout=60) as r:
            return json.loads(r.read())['content'][0]['text']
    except urllib.error.HTTPError as e:
        body=e.read().decode('utf-8',errors='replace')
        try: err=json.loads(body)['error']['message']
        except: err=body[:200]
        return f'❌ API xato ({e.code}): {err}'
    except Exception as e: return f'❌ Ulanish xatosi: {e}'

# ══════════════════════════════════════════════════════════════
#  YT-DLP
# ══════════════════════════════════════════════════════════════
def ensure_ytdlp():
    try: import yt_dlp; return True
    except:
        try:
            subprocess.run([sys.executable,'-m','pip','install','yt-dlp','--quiet'],
                           check=True,capture_output=True,timeout=120)
            return True
        except: return False

def yt_download(url,fmt,out_dir,prog_cb,stat_cb,done_cb,err_cb):
    try:
        import yt_dlp
        opts={'quiet':True,'no_warnings':True,'outtmpl':os.path.join(out_dir,'%(title)s.%(ext)s')}
        if fmt=='audio': opts.update({'format':'bestaudio/best','postprocessors':[{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}]})
        elif fmt=='1080': opts['format']='bestvideo[height<=1080]+bestaudio/best'
        elif fmt=='720':  opts['format']='bestvideo[height<=720]+bestaudio/best'
        elif fmt=='480':  opts['format']='bestvideo[height<=480]+bestaudio/best'
        else: opts['format']='best'
        def hook(d):
            if d['status']=='downloading':
                tot=d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                pct=min(99.0,d.get('downloaded_bytes',0)/tot*100)
                spd=d.get('speed'); ss=f'{spd/1048576:.1f}MB/s' if spd and spd>1048576 else f'{spd/1024:.0f}KB/s' if spd else ''
                prog_cb(pct); stat_cb(f'⬇ {pct:.0f}% {ss}')
            elif d['status']=='finished': prog_cb(99); stat_cb('⚙ Qayta ishlanmoqda...')
        opts['progress_hooks']=[hook]
        with yt_dlp.YoutubeDL(opts) as ydl: info=ydl.extract_info(url,download=True)
        prog_cb(100); done_cb(info.get('title','Video'))
    except Exception as e: err_cb(str(e))

# ══════════════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════════════
def mk_btn(parent,text,cmd,bg,fg=None,fs=10,bold=True,px=14,py=8):
    fg=fg or C['wht']; fw='bold' if bold else 'normal'
    hmap={C['acc']:C['acc2'],C['grn']:C['grn2'],C['red']:C['red2'],
          C['inp']:C['hov'],C['card']:C['hov'],C['vio']:C['vio2'],C['mut']:C['hov'],C['brd2']:C['hov']}
    hbg=hmap.get(bg,bg)
    b=tk.Button(parent,text=text,command=cmd,font=('Segoe UI',fs,fw),
                bg=bg,fg=fg,activebackground=hbg,activeforeground=fg,
                relief='flat',padx=px,pady=py,cursor='hand2',bd=0)
    b.bind('<Enter>',lambda e:b.config(bg=hbg))
    b.bind('<Leave>',lambda e:b.config(bg=bg))
    return b

def mk_lbl(parent,text,fs=10,fg=None,bold=False,**kw):
    return tk.Label(parent,text=text,font=('Segoe UI',fs,'bold' if bold else 'normal'),
                    bg=kw.get('bg',C['bg']),fg=fg or C['txt'],
                    **{k:v for k,v in kw.items() if k!='bg'})

def mk_entry(parent,var,**kw):
    brd=tk.Frame(parent,bg=C['brd2'],padx=1,pady=1)
    e=tk.Entry(brd,textvariable=var,font=kw.get('font',('Segoe UI',11)),
               bg=C['inp'],fg=C['txt'],insertbackground=C['acc3'],relief='flat',
               width=kw.get('width',30),justify=kw.get('justify','left'),show=kw.get('show',''))
    e.pack(ipady=kw.get('ipy',8),ipadx=kw.get('ipx',6))
    return brd,e

def setup_style():
    s=ttk.Style(); s.theme_use('clam')
    s.configure('SL.TNotebook',background=C['card'],bordercolor=C['brd'],tabmargins=[2,4,2,0])
    s.configure('SL.TNotebook.Tab',background=C['inp'],foreground=C['sub'],
                font=('Segoe UI',9,'bold'),padding=[10,6])
    s.map('SL.TNotebook.Tab',background=[('selected',C['acc']),('active',C['hov'])],
          foreground=[('selected',C['wht']),('active',C['txt'])])
    s.configure('SL.Horizontal.TProgressbar',troughcolor=C['inp'],background=C['acc'],
                lightcolor=C['acc2'],darkcolor=C['acc'])
    s.configure('G.Horizontal.TProgressbar',troughcolor=C['inp'],background=C['grn'],
                lightcolor=C['grn2'],darkcolor=C['grn'])

def canvas_bar(cv,data,w,h,title='',color=C['acc'],lc=C['sub']):
    cv.delete('all'); cv.create_rectangle(0,0,w,h,fill=C['card'],outline='')
    if not data: cv.create_text(w//2,h//2,text='Ma\'lumot yo\'q',fill=C['sub'],font=('Segoe UI',9)); return
    pl,pr,pt,pb=46,12,26,38; cw=w-pl-pr; ch=h-pt-pb
    mx=max(v for _,v in data) or 1; n=len(data); bw=max(5,(cw-(n-1)*3)//n)
    if title: cv.create_text(w//2,13,text=title,fill=C['sub'],font=('Segoe UI',8,'bold'))
    for ratio in (.25,.5,.75,1.0):
        y=pt+ch-int(ch*ratio)
        cv.create_line(pl-4,y,pl+n*bw+(n-1)*3+4,y,fill=C['brd2'],dash=(3,4))
        val=mx*ratio; lbl=f'{val:.0f}h' if val>=1 else f'{val*60:.0f}m'
        cv.create_text(pl-6,y,text=lbl,fill=lc,font=('Segoe UI',7),anchor='e')
    for i,(label,val) in enumerate(data):
        x0=pl+i*(bw+3); x1=x0+bw; bh2=max(2,int(ch*val/mx)); y0=pt+ch-bh2; y1=pt+ch
        cv.create_rectangle(x0+2,y0+2,x1+2,y1+2,fill=C['mut'],outline='')
        cv.create_rectangle(x0,y0,x1,y1,fill=color,outline='')
        if val>0:
            txt=f'{val:.1f}h' if val>=1 else f'{int(val*60)}m'
            cv.create_text((x0+x1)//2,y0-5,text=txt,fill=C['acc3'],font=('Segoe UI',7))
        cv.create_text((x0+x1)//2,y1+7,text=str(label)[:5],fill=lc,font=('Segoe UI',7))

# ══════════════════════════════════════════════════════════════
#  STRATEGIC PLANNING VISUAL TOOL
# ══════════════════════════════════════════════════════════════
class StrategicPlanTool:
    NODE_INFO = {
        'current_state':{'shape':'circle', 'fill':'#1a3566','outline':'#3b82f6','text':'#bfdbfe','label':'CURRENT STATE','emoji':'🔵','desc':'Hozirgi holat, resurslar, muammolar','w':110,'h':74},
        'goal':         {'shape':'hexagon','fill':'#064e3b','outline':'#10b981','text':'#a7f3d0','label':'GOAL',         'emoji':'🟢','desc':'Maqsad, deadline, success criteria','w':110,'h':72},
        'decision':     {'shape':'diamond','fill':'#451a03','outline':'#f59e0b','text':'#fef3c7','label':'DECISION',    'emoji':'🟡','desc':'Qaror nuqtasi, yo\'l tanlash','w':120,'h':80},
        'action':       {'shape':'rect',   'fill':'#0f172a','outline':'#64748b','text':'#e2e8f0','label':'ACTION',      'emoji':'⬜','desc':'Harakat: nima, qancha, kim','w':120,'h':58},
        'risk':         {'shape':'triangle','fill':'#450a0a','outline':'#ef4444','text':'#fecaca','label':'RISK',        'emoji':'🔺','desc':'Xavf, cheklov, ehtiyot bo\'l','w':100,'h':78},
        'consequence':  {'shape':'oval',   'fill':'#1c1917','outline':'#78716c','text':'#d6d3d1','label':'CONSEQUENCE', 'emoji':'⬛','desc':'Natija: ijobiy/salbiy, ehtimollik','w':124,'h':62},
    }
    TIME_LAYERS=['past','present','near_future','long_term']
    TIME_LABELS=["O'TGAN","HOZIR","YAQIN KELAJAK","UZOQ KELAJAK"]
    TIME_COLORS=['#0a0a12','#04040a','#060612','#080810']
    TIME_BORDER=['#1e1b3a','#2a1f5a','#1a2a3a','#1e1b3a']
    CW=2400; CH=1100

    def __init__(self,parent,vm,get_api,get_model):
        self.parent=parent; self.vm=vm; self.get_api=get_api; self.get_model=get_model
        self.nodes={}; self.conns={}
        self._node_cids={}; self._conn_cids={}; self._id2node={}
        self._nc=0; self._cc=0
        self.mode='select'; self.add_type='action'
        self.selected=None; self._conn_src=None
        self._drag_node=None; self._dox=0; self._doy=0
        self.plan_title='Yangi Reja'; self._unsaved=False
        self._build()

    def _build(self):
        p=self.parent
        # ── Toolbar ──
        tb=tk.Frame(p,bg=C['card'],pady=4); tb.pack(fill='x',padx=4,pady=(4,0))

        title_f=tk.Frame(tb,bg=C['card']); title_f.pack(side='left',padx=4)
        self._tv=tk.StringVar(value=self.plan_title)
        te=tk.Entry(title_f,textvariable=self._tv,font=('Segoe UI',10,'bold'),
                    bg=C['inp'],fg=C['acc3'],relief='flat',insertbackground=C['acc3'],width=18)
        te.pack(ipady=5,ipadx=4); te.bind('<FocusOut>',lambda e:self._set_title())

        tk.Frame(tb,bg=C['brd2'],width=1,height=26).pack(side='left',padx=5)

        self._mbtns={}
        for m,emoji in [('select','🖱 Select'),('connect','🔗 Connect'),('delete','🗑 Delete')]:
            b=tk.Button(tb,text=emoji,font=('Segoe UI',9,'bold'),
                        bg=C['acc'] if m=='select' else C['inp'],
                        fg=C['wht'],relief='flat',padx=9,pady=5,cursor='hand2',bd=0,
                        command=lambda mm=m:self._set_mode(mm))
            b.pack(side='left',padx=2); self._mbtns[m]=b

        tk.Frame(tb,bg=C['brd2'],width=1,height=26).pack(side='left',padx=5)
        mk_lbl(tb,'Qo\'sh:',8,C['sub'],bg=C['card']).pack(side='left',padx=3)
        self._tbtns={}
        for nt,info in self.NODE_INFO.items():
            b=tk.Button(tb,text=f"{info['emoji']} {info['label'][:6]}",
                        font=('Segoe UI',8),bg=info['fill'],fg=info['text'],
                        relief='flat',padx=6,pady=5,cursor='hand2',bd=0,
                        command=lambda t=nt:self._set_add(t))
            b.pack(side='left',padx=1); self._tbtns[nt]=b
            b.bind('<Enter>',lambda e,btn=b,info=info:btn.config(bg=info['outline']))
            b.bind('<Leave>',lambda e,btn=b,info=info:btn.config(bg=info['fill']))

        tk.Frame(tb,bg=C['brd2'],width=1,height=26).pack(side='left',padx=5)
        mk_btn(tb,'💾',self._save,C['grn'],fs=9,px=8,py=5).pack(side='left',padx=2)
        mk_btn(tb,'📂',self._load,C['inp'],fs=9,px=8,py=5).pack(side='left',padx=2)
        mk_btn(tb,'🤖 AI',self._ai_advisor,C['acc'],fs=9,px=10,py=5).pack(side='left',padx=2)
        mk_btn(tb,'📊 Sim',self._simulate,C['vio'],fs=9,px=10,py=5).pack(side='left',padx=2)
        mk_btn(tb,'🧹',self._clear,C['red'],fs=9,px=8,py=5).pack(side='right',padx=2)

        # Hint bar
        self._hv=tk.StringVar(value="🖱 Bosish → node yaratish  |  Drag → ko'chirish  |  Dbl-click → tahrirlash")
        tk.Label(p,textvariable=self._hv,font=('Segoe UI',8),bg=C['mut'],
                 fg=C['sub'],anchor='w',padx=8,pady=2).pack(fill='x',padx=4)

        # Main layout
        mf=tk.Frame(p,bg=C['bg']); mf.pack(fill='both',expand=True,padx=4,pady=4)

        # Properties panel
        self._pf=tk.Frame(mf,bg=C['card'],width=230); self._pf.pack(side='right',fill='y',padx=(4,0))
        self._pf.pack_propagate(False); self._build_props()

        # Canvas
        cf=tk.Frame(mf,bg=C['bg']); cf.pack(side='left',fill='both',expand=True)
        self.cv=tk.Canvas(cf,bg='#03030a',scrollregion=(0,0,self.CW,self.CH),highlightthickness=0)
        hb=tk.Scrollbar(cf,orient='horizontal',command=self.cv.xview)
        vb=tk.Scrollbar(cf,orient='vertical',command=self.cv.yview)
        self.cv.configure(xscrollcommand=hb.set,yscrollcommand=vb.set)
        hb.pack(side='bottom',fill='x'); vb.pack(side='right',fill='y')
        self.cv.pack(fill='both',expand=True)

        self._draw_timeline()
        self.cv.bind('<Button-1>',self._click)
        self.cv.bind('<Double-Button-1>',self._dblclick)
        self.cv.bind('<B1-Motion>',self._drag)
        self.cv.bind('<ButtonRelease-1>',self._release)
        self.cv.bind('<Button-3>',self._rclick)

        # Starter node
        n=self._make_node('current_state',300,300,'Hozirgi Holat')
        self._draw_node(n['id'])

    def _build_props(self):
        for w in self._pf.winfo_children():
            try: w.destroy()
            except: pass
        p=self._pf
        mk_lbl(p,'⚙  PROPERTIES',9,C['sub'],bold=True,bg=C['card']).pack(anchor='w',padx=10,pady=(10,4))
        if not self.selected:
            mk_lbl(p,'Node tanlang\nClick → tanla\nDrag → ko\'chir\nDbl → tahrirlash',
                   8,C['sub'],bg=C['card']).pack(anchor='w',padx=10,pady=6)
            # Legend
            mk_lbl(p,'— NODE TURLARI —',7,C['sub'],bg=C['card']).pack(anchor='w',padx=10,pady=(12,4))
            for nt,info in self.NODE_INFO.items():
                rf=tk.Frame(p,bg=info['fill'],padx=6,pady=3); rf.pack(fill='x',padx=8,pady=1)
                mk_lbl(rf,f"{info['emoji']} {info['label']}",8,info['text'],bold=True,bg=info['fill']).pack(anchor='w')
                mk_lbl(rf,info['desc'],7,info['text'],bg=info['fill']).pack(anchor='w')
            return

        n=self.nodes.get(self.selected)
        if not n: return
        info=self.NODE_INFO.get(n['type'],{})

        hf=tk.Frame(p,bg=info.get('fill',C['inp']),padx=8,pady=6); hf.pack(fill='x',padx=8,pady=4)
        mk_lbl(hf,f"{info.get('emoji','')} {info.get('label','')}",9,info.get('text',C['txt']),bold=True,bg=info.get('fill',C['inp'])).pack(anchor='w')
        mk_lbl(hf,info.get('desc',''),7,info.get('text',C['sub']),bg=info.get('fill',C['inp'])).pack(anchor='w')

        mk_lbl(p,'Matn:',8,C['sub'],bg=C['card']).pack(anchor='w',padx=10,pady=(8,0))
        tv=tk.StringVar(value=n.get('text',''))
        brd,_=mk_entry(p,tv,width=24,ipy=6); brd.pack(padx=8,fill='x')

        evars={}

        if n['type']=='decision':
            pv=tk.IntVar(value=n.get('probability',50)); evars['probability']=pv
            pf=tk.Frame(p,bg=C['bg']); pf.pack(fill='x',padx=8,pady=(6,0))
            pl=mk_lbl(pf,f"⚡ {pv.get()}%",9,C['yel2'],bold=True,bg=C['bg']); pl.pack(side='right')
            sl=ttk.Scale(pf,variable=pv,from_=0,to=100); sl.pack(side='left',fill='x',expand=True)
            pv.trace('w',lambda *a:pl.config(text=f"⚡ {pv.get()}%"))

        elif n['type']=='consequence':
            iv=tk.IntVar(value=n.get('impact',5)); evars['impact']=iv
            pf=tk.Frame(p,bg=C['bg']); pf.pack(fill='x',padx=8,pady=(6,0))
            il=mk_lbl(pf,f"Impact: {iv.get()}",9,C['grn2'],bold=True,bg=C['bg']); il.pack(side='right')
            ttk.Scale(pf,variable=iv,from_=-10,to=10).pack(side='left',fill='x',expand=True)
            iv.trace('w',lambda *a:il.config(text=f"Impact: {iv.get()}",fg=C['grn3'] if iv.get()>=0 else C['red3']))

        elif n['type']=='risk':
            rv=tk.IntVar(value=n.get('risk_level',5)); evars['risk_level']=rv
            pf=tk.Frame(p,bg=C['bg']); pf.pack(fill='x',padx=8,pady=(6,0))
            rl=mk_lbl(pf,f"⚠ Sev:{rv.get()}",9,C['red3'],bold=True,bg=C['bg']); rl.pack(side='right')
            ttk.Scale(pf,variable=rv,from_=1,to=10).pack(side='left',fill='x',expand=True)
            rv.trace('w',lambda *a:rl.config(text=f"⚠ Sev:{rv.get()}"))

        elif n['type']=='goal':
            mk_lbl(p,'Deadline:',8,C['sub'],bg=C['card']).pack(anchor='w',padx=10,pady=(4,0))
            dv=tk.StringVar(value=n.get('deadline','')); evars['deadline']=dv
            brd2,_=mk_entry(p,dv,width=24,ipy=5); brd2.pack(padx=8,fill='x')

        elif n['type']=='action':
            mk_lbl(p,'Kim:',8,C['sub'],bg=C['card']).pack(anchor='w',padx=10,pady=(4,0))
            wv=tk.StringVar(value=n.get('who','')); evars['who']=wv
            brd2,_=mk_entry(p,wv,width=24,ipy=5); brd2.pack(padx=8,fill='x')
            mk_lbl(p,'Muddat:',8,C['sub'],bg=C['card']).pack(anchor='w',padx=10,pady=(4,0))
            durv=tk.StringVar(value=n.get('duration','')); evars['duration']=durv
            brd3,_=mk_entry(p,durv,width=24,ipy=5); brd3.pack(padx=8,fill='x')

        mk_lbl(p,'Link:',8,C['sub'],bg=C['card']).pack(anchor='w',padx=10,pady=(6,0))
        lv=tk.StringVar(value=n.get('link',''))
        brd_l,_=mk_entry(p,lv,width=24,ipy=5); brd_l.pack(padx=8,fill='x')

        mk_lbl(p,'Vaqt qatlami:',8,C['sub'],bg=C['card']).pack(anchor='w',padx=10,pady=(6,0))
        tlv=tk.StringVar(value=n.get('time_layer','present'))
        ttk.Combobox(p,textvariable=tlv,values=self.TIME_LAYERS,state='readonly',
                     font=('Segoe UI',8),width=20).pack(padx=10,anchor='w')

        def do_save():
            n['text']=tv.get().strip() or info.get('label','')
            n['link']=lv.get().strip(); n['time_layer']=tlv.get()
            for k,v in evars.items(): n[k]=v.get()
            self._redraw_node(self.selected); self._unsaved=True

        nid=self.selected
        mk_btn(p,'✅ Saqlash',do_save,C['grn'],fs=9,px=10,py=6).pack(fill='x',padx=8,pady=6)
        mk_btn(p,'🗑 O\'chirish',lambda:self._del_node(nid),C['red'],fs=8,px=8,py=5).pack(fill='x',padx=8,pady=(0,4))

    # ── Drawing ───────────────────────────────────────────────
    def _draw_timeline(self):
        self.cv.delete('tl')
        zw=self.CW//4
        for i,(lbl,col,brd) in enumerate(zip(self.TIME_LABELS,self.TIME_COLORS,self.TIME_BORDER)):
            x0=i*zw; x1=x0+zw
            self.cv.create_rectangle(x0,0,x1,self.CH,fill=col,outline='',tags='tl')
            if i>0: self.cv.create_line(x0,0,x0,self.CH,fill=brd,dash=(6,4),tags='tl')
            self.cv.create_text(x0+zw//2,20,text=lbl,fill=brd,font=('Segoe UI',9,'bold'),tags='tl')
        self.cv.create_text(self.CW//2,self.CH-16,
            text='◄ ────── PAST ─── PRESENT ─── NEAR FUTURE ─── LONG TERM ────── ►',
            fill=C['sub'],font=('Segoe UI',8),tags='tl')

    def _make_node(self,ntype,x,y,text=None):
        self._nc+=1; nid=f'n{self._nc}'
        info=self.NODE_INFO[ntype]
        n={'id':nid,'type':ntype,'x':x,'y':y,'text':text or info['label'],
           'time_layer':'present','probability':50,'impact':5,'risk_level':5,
           'deadline':'','success_criteria':'','who':'','duration':'','link':''}
        self.nodes[nid]=n; self._unsaved=True; return n

    def _draw_node(self,nid):
        n=self.nodes.get(nid)
        if not n: return
        for cid in self._node_cids.get(nid,[]):
            self.cv.delete(cid); self._id2node.pop(cid,None)
        info=self.NODE_INFO[n['type']]; x,y=n['x'],n['y']
        w2=info['w']//2; h2=info['h']//2
        fill=info['fill']; outline='#ffffff' if nid==self.selected else info['outline']
        ow=3 if nid==self.selected else 2
        cids=[]
        shape=info['shape']
        if shape=='circle':
            cid=self.cv.create_oval(x-w2,y-h2,x+w2,y+h2,fill=fill,outline=outline,width=ow)
        elif shape=='hexagon':
            pts=[]
            for i in range(6): a=math.radians(60*i-30); pts+=[x+w2*math.cos(a),y+h2*math.sin(a)]
            cid=self.cv.create_polygon(pts,fill=fill,outline=outline,width=ow)
        elif shape=='diamond':
            cid=self.cv.create_polygon([x,y-h2,x+w2,y,x,y+h2,x-w2,y],fill=fill,outline=outline,width=ow)
        elif shape=='triangle':
            cid=self.cv.create_polygon([x,y-h2,x+w2,y+h2,x-w2,y+h2],fill=fill,outline=outline,width=ow)
        elif shape=='oval':
            cid=self.cv.create_oval(x-w2,y-h2//2*2,x+w2,y+h2,fill=fill,outline=outline,width=ow)
        else:
            r=6; pts=[x-w2+r,y-h2,x+w2-r,y-h2,x+w2,y-h2+r,x+w2,y+h2-r,x+w2-r,y+h2,x-w2+r,y+h2,x-w2,y+h2-r,x-w2,y-h2+r]
            cid=self.cv.create_polygon(pts,fill=fill,outline=outline,width=ow,smooth=True)
        cids.append(cid); self._id2node[cid]=nid
        txt=n['text'][:13]+'…' if len(n['text'])>13 else n['text']
        tcid=self.cv.create_text(x,y,text=txt,fill=info['text'],font=('Segoe UI',8,'bold'),width=info['w']-8,justify='center')
        cids.append(tcid); self._id2node[tcid]=nid
        # badges
        if n['type']=='decision' and n.get('probability') is not None:
            bid=self.cv.create_text(x,y+h2+10,text=f"⚡{n['probability']}%",fill=C['yel2'],font=('Segoe UI',7))
            cids.append(bid); self._id2node[bid]=nid
        elif n['type']=='consequence' and n.get('impact') is not None:
            imp=n['impact']; col=C['grn3'] if imp>=0 else C['red3']
            bid=self.cv.create_text(x,y+h2+10,text=f"Imp:{'+' if imp>=0 else ''}{imp}",fill=col,font=('Segoe UI',7))
            cids.append(bid); self._id2node[bid]=nid
        elif n['type']=='risk' and n.get('risk_level'):
            bid=self.cv.create_text(x,y+h2+10,text=f"⚠{n['risk_level']}/10",fill=C['red3'],font=('Segoe UI',7))
            cids.append(bid); self._id2node[bid]=nid
        if n.get('link'):
            lid=self.cv.create_text(x+w2-5,y-h2+6,text='🔗',font=('Segoe UI',7))
            cids.append(lid); self._id2node[lid]=nid
        self._node_cids[nid]=cids

    def _redraw_node(self,nid):
        self._draw_node(nid)
        for cid,c in list(self.conns.items()):
            if c['from']==nid or c['to']==nid: self._draw_conn(cid)

    def _draw_conn(self,cid):
        c=self.conns.get(cid)
        if not c: return
        for ci in self._conn_cids.get(cid,[]): self.cv.delete(ci)
        n1=self.nodes.get(c['from']); n2=self.nodes.get(c['to'])
        if not n1 or not n2: return
        x1,y1=n1['x'],n1['y']; x2,y2=n2['x'],n2['y']
        shadow=self.cv.create_line(x1+2,y1+2,x2+2,y2+2,fill=C['mut'],width=2,arrow=tk.LAST,arrowshape=(10,12,4))
        line=self.cv.create_line(x1,y1,x2,y2,fill=C['acc3'],width=2,arrow=tk.LAST,arrowshape=(10,12,4))
        cids=[shadow,line]
        if c.get('label'):
            mx,my=(x1+x2)//2,(y1+y2)//2
            cids.append(self.cv.create_rectangle(mx-22,my-8,mx+22,my+8,fill=C['card'],outline=''))
            cids.append(self.cv.create_text(mx,my,text=c['label'],fill=C['dim'],font=('Segoe UI',7)))
        self._conn_cids[cid]=cids
        for ci in cids: self.cv.tag_lower(ci)

    def _connect(self,f,t):
        if f==t: return
        for c in self.conns.values():
            if c['from']==f and c['to']==t: return
        self._cc+=1; cid=f'c{self._cc}'
        self.conns[cid]={'id':cid,'from':f,'to':t,'label':''}
        self._draw_conn(cid); self._unsaved=True

    # ── Events ────────────────────────────────────────────────
    def _cxy(self,event): return self.cv.canvasx(event.x),self.cv.canvasy(event.y)

    def _node_at(self,x,y):
        for item in reversed(self.cv.find_overlapping(x-3,y-3,x+3,y+3)):
            nid=self._id2node.get(item)
            if nid and nid in self.nodes: return nid
        return None

    def _click(self,event):
        x,y=self._cxy(event); nid=self._node_at(x,y)
        if self.mode=='select':
            prev=self.selected; self.selected=nid
            if prev: self._redraw_node(prev)
            if nid: self._redraw_node(nid)
            self._build_props()
            if nid: self._drag_node=nid; self._dox=x-self.nodes[nid]['x']; self._doy=y-self.nodes[nid]['y']
        elif self.mode=='connect':
            if nid:
                if self._conn_src is None:
                    self._conn_src=nid; self._redraw_node(nid)
                    self._hv.set(f"🔗 Ikkinchi nodeni tanlang — {self.nodes[nid]['text'][:20]}")
                else:
                    self._connect(self._conn_src,nid)
                    prev=self._conn_src; self._conn_src=None
                    self._redraw_node(prev); self._hv.set("✅ Ulandi!")
            else: self._conn_src=None; self._hv.set("🔗 Birinchi nodeni tanlang")
        elif self.mode.startswith('add_'):
            nt=self.mode[4:]
            n=self._make_node(nt,int(x),int(y))
            self._draw_node(n['id']); self.selected=n['id']
            self._build_props()
            self._hv.set(f"✅ {self.NODE_INFO[nt]['label']} qo'shildi — dbl-click tahrirlash")
        elif self.mode=='delete':
            if nid: self._del_node(nid)

    def _dblclick(self,event):
        x,y=self._cxy(event); nid=self._node_at(x,y)
        if nid: self._edit_dlg(nid)
        elif self.mode=='select':
            n=self._make_node(self.add_type,int(x),int(y))
            self._draw_node(n['id']); self.selected=n['id']; self._build_props()

    def _drag(self,event):
        if self.mode=='select' and self._drag_node:
            x,y=self._cxy(event)
            n=self.nodes[self._drag_node]
            n['x']=max(60,min(self.CW-60,int(x-self._dox)))
            n['y']=max(40,min(self.CH-40,int(y-self._doy)))
            self._redraw_node(self._drag_node)

    def _release(self,event): self._drag_node=None

    def _rclick(self,event):
        x,y=self._cxy(event); nid=self._node_at(x,y)
        if not nid: return
        menu=tk.Menu(self.cv,tearoff=0,bg=C['card'],fg=C['txt'],font=('Segoe UI',9),
                     activebackground=C['acc'],activeforeground=C['wht'])
        menu.add_command(label="✏ Tahrirlash",command=lambda:self._edit_dlg(nid))
        if self.nodes[nid].get('link'):
            menu.add_command(label="🔗 Ochish",command=lambda:__import__('webbrowser').open(self.nodes[nid]['link']))
        sub=tk.Menu(menu,tearoff=0,bg=C['card'],fg=C['txt'],font=('Segoe UI',9))
        for t,info in self.NODE_INFO.items():
            sub.add_command(label=f"{info['emoji']} {info['label']}",command=lambda tt=t:self._chg_type(nid,tt))
        menu.add_cascade(label="🔄 Tur o'zgartirish",menu=sub)
        menu.add_separator()
        menu.add_command(label="🗑 O'chirish",command=lambda:self._del_node(nid))
        menu.post(event.x_root,event.y_root)

    # ── Node operations ───────────────────────────────────────
    def _edit_dlg(self,nid):
        n=self.nodes.get(nid)
        if not n: return
        info=self.NODE_INFO[n['type']]
        dlg=tk.Toplevel(); dlg.title(f"Tahrirlash — {info['label']}")
        dlg.configure(bg=C['bg']); dlg.attributes('-topmost',True); dlg.resizable(False,False); dlg.geometry('420x360')
        hf=tk.Frame(dlg,bg=info['fill'],padx=12,pady=8); hf.pack(fill='x')
        mk_lbl(hf,f"{info['emoji']} {info['label']}",12,info['text'],bold=True,bg=info['fill']).pack(anchor='w')
        mk_lbl(hf,info['desc'],8,info['text'],bg=info['fill']).pack(anchor='w')
        mk_lbl(dlg,'Matn:',9,C['sub']).pack(anchor='w',padx=14,pady=(10,2))
        tv=tk.StringVar(value=n.get('text',''))
        brd,te=mk_entry(dlg,tv,width=42,ipy=8); brd.pack(padx=12,fill='x'); te.focus_set()
        evars={}
        if n['type']=='decision':
            mk_lbl(dlg,'Muvaffaqiyat ehtimoli (%):',9,C['sub']).pack(anchor='w',padx=14,pady=(8,2))
            pf=tk.Frame(dlg,bg=C['bg']); pf.pack(fill='x',padx=12)
            pv=tk.IntVar(value=n.get('probability',50)); evars['probability']=pv
            pl=mk_lbl(pf,f"{pv.get()}%",11,C['yel2'],bold=True,bg=C['bg']); pl.pack(side='right',padx=6)
            ttk.Scale(pf,variable=pv,from_=0,to=100).pack(side='left',fill='x',expand=True)
            pv.trace('w',lambda *a:pl.config(text=f"{pv.get()}%"))
        elif n['type']=='goal':
            mk_lbl(dlg,'Deadline:',9,C['sub']).pack(anchor='w',padx=14,pady=(8,2))
            dv=tk.StringVar(value=n.get('deadline','')); evars['deadline']=dv
            brd2,_=mk_entry(dlg,dv,width=20,ipy=6); brd2.pack(padx=12,anchor='w')
        elif n['type']=='action':
            mk_lbl(dlg,'Kim:',9,C['sub']).pack(anchor='w',padx=14,pady=(8,2))
            wv=tk.StringVar(value=n.get('who','')); evars['who']=wv
            brd2,_=mk_entry(dlg,wv,width=30,ipy=6); brd2.pack(padx=12,anchor='w')
        mk_lbl(dlg,'Link:',9,C['sub']).pack(anchor='w',padx=14,pady=(8,2))
        lv=tk.StringVar(value=n.get('link','')); brd_l,_=mk_entry(dlg,lv,width=42,ipy=6); brd_l.pack(padx=12,fill='x')
        def do_save():
            n['text']=tv.get().strip() or info['label']; n['link']=lv.get().strip()
            for k,v in evars.items(): n[k]=v.get()
            self._redraw_node(nid); self.selected=nid; self._build_props(); self._unsaved=True; dlg.destroy()
        bf=tk.Frame(dlg,bg=C['bg']); bf.pack(fill='x',padx=12,pady=10)
        mk_btn(bf,'✅ Saqlash',do_save,C['grn'],fs=11,px=20,py=9).pack(side='right',padx=4)
        mk_btn(bf,'Bekor',dlg.destroy,C['inp'],fg=C['dim'],fs=10,px=14,py=9).pack(side='right',padx=4)
        dlg.bind('<Return>',lambda e:do_save()); dlg.grab_set(); dlg.protocol('WM_DELETE_WINDOW',dlg.destroy)

    def _del_node(self,nid):
        if nid not in self.nodes: return
        for cid in self._node_cids.pop(nid,[]): self.cv.delete(cid); self._id2node.pop(cid,None)
        for cid in [c for c,conn in self.conns.items() if conn['from']==nid or conn['to']==nid]:
            for ci in self._conn_cids.pop(cid,[]): self.cv.delete(ci)
            self.conns.pop(cid,None)
        del self.nodes[nid]
        if self.selected==nid: self.selected=None; self._build_props()
        self._unsaved=True

    def _chg_type(self,nid,nt):
        if nid in self.nodes: self.nodes[nid]['type']=nt; self._redraw_node(nid)
        if self.selected==nid: self._build_props()

    def _set_mode(self,m):
        self.mode=m; self._conn_src=None
        for mm,b in self._mbtns.items(): b.config(bg=C['acc'] if mm==m else C['inp'])
        hints={'select':"🖱 Select/ko'chirish | Dbl-click → tahrirlash",
               'connect':"🔗 Birinchi node → ikkinchi node tanlang",
               'delete':"🗑 O'chirish uchun node ustiga bosing"}
        self._hv.set(hints.get(m,''))
        for t,b in self._tbtns.items(): b.config(bg=self.NODE_INFO[t]['fill'])

    def _set_add(self,nt):
        self.mode=f'add_{nt}'; self.add_type=nt; self._conn_src=None
        for m,b in self._mbtns.items(): b.config(bg=C['inp'])
        for t,b in self._tbtns.items():
            b.config(bg=self.NODE_INFO[t]['outline'] if t==nt else self.NODE_INFO[t]['fill'])
        self._hv.set(f"➕ Kanvasga bosing — {self.NODE_INFO[nt]['label']} qo'shish")

    def _set_title(self):
        self.plan_title=self._tv.get().strip() or 'Yangi Reja'; self._tv.set(self.plan_title)

    def _clear(self):
        if not messagebox.askyesno('Tozalash','Barcha nodelar o\'chirilsinmi?',parent=self.parent): return
        self.cv.delete('all'); self._draw_timeline()
        self.nodes.clear(); self.conns.clear()
        self._node_cids.clear(); self._conn_cids.clear(); self._id2node.clear()
        self.selected=None; self._nc=0; self._cc=0; self._unsaved=False; self._build_props()

    def _to_dict(self):
        return {'title':self.plan_title,'saved':now_str(),
                'nodes':list(self.nodes.values()),'connections':list(self.conns.values())}

    def _from_dict(self,d):
        self.cv.delete('all'); self._draw_timeline()
        self.nodes.clear(); self.conns.clear()
        self._node_cids.clear(); self._conn_cids.clear(); self._id2node.clear()
        self.selected=None; self._nc=0; self._cc=0
        self.plan_title=d.get('title','Reja'); self._tv.set(self.plan_title)
        for n in d.get('nodes',[]): self.nodes[n['id']]=n; self._nc=max(self._nc,int(n['id'].lstrip('n') or 0)); self._draw_node(n['id'])
        for c in d.get('connections',[]): self.conns[c['id']]=c; self._cc=max(self._cc,int(c['id'].lstrip('c') or 0)); self._draw_conn(c['id'])
        self._build_props(); self._unsaved=False

    def _save(self):
        self._set_title()
        if not self.vm.is_open(): messagebox.showwarning('Vault','Vault oching!',parent=self.parent); return
        self.vm.save_visual_plan(self._to_dict()); self._unsaved=False
        messagebox.showinfo('✅',f'"{self.plan_title}" saqlandi!',parent=self.parent)

    def _load(self):
        if not self.vm.is_open(): messagebox.showwarning('Vault','Vault oching!',parent=self.parent); return
        plans=self.vm.get_visual_plans()
        if not plans: messagebox.showinfo('Bo\'sh','Hali saqlangan diagramma yo\'q.',parent=self.parent); return
        dlg=tk.Toplevel(); dlg.title('📂 Rejani yuklash'); dlg.configure(bg=C['bg'])
        dlg.attributes('-topmost',True); dlg.geometry('440x340')
        mk_lbl(dlg,'📂  Saqlangan Rejalar',12,C['acc3'],bold=True).pack(pady=(10,6))
        fr=tk.Frame(dlg,bg=C['bg']); fr.pack(fill='both',expand=True,padx=10)
        cv2=tk.Canvas(fr,bg=C['bg'],highlightthickness=0); sb2=tk.Scrollbar(fr,orient='vertical',command=cv2.yview)
        cv2.configure(yscrollcommand=sb2.set); sb2.pack(side='right',fill='y'); cv2.pack(fill='both',expand=True)
        inn=tk.Frame(cv2,bg=C['bg']); cv2.create_window((0,0),window=inn,anchor='nw')
        inn.bind('<Configure>',lambda e:cv2.configure(scrollregion=cv2.bbox('all')))
        sel=[None]
        def pick(plan,row):
            sel[0]=plan
            for w in inn.winfo_children():
                w.config(bg=C['card'])
                for ch in w.winfo_children():
                    try: ch.config(bg=C['card'])
                    except: pass
            row.config(bg=C['sel'])
            for ch in row.winfo_children():
                try: ch.config(bg=C['sel'])
                except: pass
        for plan in reversed(plans):
            row=tk.Frame(inn,bg=C['card'],padx=10,pady=8,cursor='hand2'); row.pack(fill='x',pady=2)
            mk_lbl(row,plan['title'],10,C['txt'],bold=True,bg=C['card']).pack(anchor='w')
            nc=len(plan.get('nodes',[])); cc=len(plan.get('connections',[]))
            mk_lbl(row,f"💾 {plan.get('saved','')[:10]}  ·  {nc} node  ·  {cc} bog'lanish",8,C['sub'],bg=C['card']).pack(anchor='w')
            tk.Frame(row,bg=C['brd2'],height=1).pack(fill='x',pady=2)
            for w in [row]+row.winfo_children(): w.bind('<Button-1>',lambda e,p=plan,r=row:pick(p,r))
        def do_load():
            if sel[0]:
                if self._unsaved and not messagebox.askyesno('Saqlanmagan','O\'zgarishlar bor. Davom?'): return
                self._from_dict(sel[0]); dlg.destroy()
        def do_del():
            if sel[0]:
                if messagebox.askyesno('O\'chirish',f'"{sel[0]["title"]}" o\'chirilsinmi?'):
                    self.vm.delete_visual_plan(sel[0]['title']); dlg.destroy(); self._load()
        bf=tk.Frame(dlg,bg=C['bg']); bf.pack(fill='x',padx=10,pady=8)
        mk_btn(bf,'📂 Yuklash',do_load,C['acc'],fs=10,px=14,py=7).pack(side='left',padx=4)
        mk_btn(bf,'🗑 O\'chirish',do_del,C['red'],fs=9,px=10,py=7).pack(side='left',padx=4)
        mk_btn(bf,'Bekor',dlg.destroy,C['inp'],fg=C['dim'],fs=9,px=10,py=7).pack(side='right',padx=4)
        dlg.grab_set(); dlg.protocol('WM_DELETE_WINDOW',dlg.destroy)

    def _ai_advisor(self):
        api=self.get_api(); model=self.get_model()
        lines=[f"Plan: {self.plan_title}\n"]
        for n in self.nodes.values():
            info=self.NODE_INFO.get(n['type'],{})
            line=f"  [{info.get('label','?')}] {n['text']}"
            if n['type']=='decision': line+=f" (ehtimol:{n.get('probability',50)}%)"
            if n['type']=='consequence': line+=f" (impact:{n.get('impact',0)})"
            if n['type']=='risk': line+=f" (risk:{n.get('risk_level',5)}/10)"
            lines.append(line)
        for c in self.conns.values():
            n1=self.nodes.get(c['from']); n2=self.nodes.get(c['to'])
            if n1 and n2: lines.append(f"  {n1['text']} → {n2['text']}")
        dlg=tk.Toplevel(); dlg.title('🤖 AI Maslahat'); dlg.configure(bg=C['bg'])
        dlg.attributes('-topmost',True); dlg.geometry('620x480')
        tk.Frame(dlg,bg=C['acc'],pady=8).pack(fill='x')
        hf=dlg.winfo_children()[-1]
        mk_lbl(hf,'🤖  AI Strategik Maslahat',12,C['wht'],bold=True,bg=C['acc']).pack(padx=14)
        brd=tk.Frame(dlg,bg=C['brd2'],padx=1,pady=1); brd.pack(fill='both',expand=True,padx=12,pady=10)
        ta=scrolledtext.ScrolledText(brd,font=('Segoe UI',10),bg=C['inp'],fg=C['txt'],wrap='word',relief='flat',state='disabled')
        ta.pack(fill='both',expand=True,padx=2,pady=2)
        def write(t):
            ta.config(state='normal'); ta.delete('1.0','end'); ta.insert('end',t); ta.config(state='disabled')
        write('⏳ AI tahlil qilmoqda...')
        prompt='\n'.join(lines)+'\n\nShu rejani tahlil qil: kuchli/zaif tomonlar, yetishmayotgan qadamlar, optimal yo\'l.'
        sys_p="Sen strategik rejalashtirish ekspertisan. O'zbek tilida aniq, amaliy maslahatlar ber."
        def run():
            r=ai_call(api,[{'role':'user','content':prompt}],system=sys_p,model=model,max_tokens=2000)
            dlg.after(0,lambda:write(r))
        threading.Thread(target=run,daemon=True).start()
        mk_btn(dlg,'Yopish',dlg.destroy,C['inp'],fg=C['dim'],fs=10,px=14,py=7).pack(pady=8)
        dlg.grab_set(); dlg.protocol('WM_DELETE_WINDOW',dlg.destroy)

    def _simulate(self):
        dn=[n for n in self.nodes.values() if n['type']=='decision']
        rn=[n for n in self.nodes.values() if n['type']=='risk']
        cn=[n for n in self.nodes.values() if n['type']=='consequence']
        if not dn and not rn: messagebox.showinfo('Simulation','Decision yoki Risk node qo\'shing.',parent=self.parent); return
        avg_prob=sum(n.get('probability',50) for n in dn)/max(len(dn),1)
        avg_risk=sum(n.get('risk_level',5) for n in rn)/max(len(rn),1)
        total_impact=sum(n.get('impact',0) for n in cn)
        path_a=max(5,min(99,avg_prob-avg_risk*2))
        path_b=max(5,min(99,avg_prob*0.75-avg_risk*1.5))
        overall=(path_a+path_b)/2
        col=C['grn2'] if overall>=70 else C['yel2'] if overall>=40 else C['red3']
        dlg=tk.Toplevel(); dlg.title('📊 Simulation'); dlg.configure(bg=C['bg'])
        dlg.attributes('-topmost',True); dlg.geometry('480x460')
        hf=tk.Frame(dlg,bg=C['vio'],pady=8); hf.pack(fill='x')
        mk_lbl(hf,'📊  Scenario Simulation',13,C['wht'],bold=True,bg=C['vio']).pack(padx=14)
        cf=tk.Frame(dlg,bg=C['bg']); cf.pack(fill='both',expand=True,padx=14,pady=10)
        mk_lbl(cf,'🎯  Reja Baholash',12,C['acc3'],bold=True).pack(anchor='w',pady=(0,10))
        sf=tk.Frame(cf,bg=C['card'],padx=16,pady=14); sf.pack(fill='x',pady=(0,10))
        for lbl,val,c2 in [
            ('📊 Umumiy muvaffaqiyat',f'{overall:.0f}%',col),
            ('⚡ Path A (optimal)',f'{path_a:.0f}%',C['grn2']),
            ('📉 Path B (konservativ)',f'{path_b:.0f}%',C['yel2']),
            ('⚠  Xavf (o\'rtacha)',f'{avg_risk:.1f}/10',C['red3']),
            ('💎 Jami impact',f"{'+' if total_impact>=0 else ''}{total_impact}",C['grn3'] if total_impact>=0 else C['red3']),
        ]:
            r=tk.Frame(sf,bg=C['card']); r.pack(fill='x',pady=3)
            mk_lbl(r,lbl,10,C['sub'],bg=C['card']).pack(side='left',padx=6)
            mk_lbl(r,val,12,c2,bold=True,bg=C['card']).pack(side='right',padx=6)
        if dn:
            mk_lbl(cf,'🟡  Decision Nodelar:',10,C['yel2']).pack(anchor='w',pady=(6,4))
            df=tk.Frame(cf,bg=C['card'],padx=10,pady=8); df.pack(fill='x')
            for n in dn:
                p_val=n.get('probability',50); c3=C['grn3'] if p_val>=70 else C['yel2'] if p_val>=40 else C['red3']
                r=tk.Frame(df,bg=C['card']); r.pack(fill='x',pady=2)
                mk_lbl(r,f"  {n['text'][:32]}",9,C['dim'],bg=C['card']).pack(side='left')
                mk_lbl(r,f"{p_val}%",9,c3,bold=True,bg=C['card']).pack(side='right')
        mk_lbl(cf,'💡  Tavsiya:',10,C['acc3']).pack(anchor='w',pady=(8,4))
        rec_f=tk.Frame(cf,bg=C['inp'],padx=10,pady=8); rec_f.pack(fill='x')
        rec="✅ Reja kuchli. Path A ni tanlang!" if overall>=70 else "⚠ O'rtacha. Risk nodelarni kamaytiring." if overall>=50 else "🔴 Xavf yuqori. Rejani qayta ko'ring."
        mk_lbl(rec_f,rec,9,C['txt'],bg=C['inp'],wraplength=420,justify='left').pack()
        mk_btn(dlg,'Yopish',dlg.destroy,C['inp'],fg=C['dim'],fs=10,px=14,py=7).pack(pady=8)
        dlg.grab_set(); dlg.protocol('WM_DELETE_WINDOW',dlg.destroy)

# ══════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════
class SL:
    def __init__(self):
        self.cfg=CfgMgr(); self.tm=TaskMgr(); self.jm=JournalMgr()
        self.vm=VaultMgr(); self.pl=PowerLog()
        self.at=AppTracker(enabled=self.cfg.get('track_apps',True))
        self.running=False; self.paused=False; self.end_ts=0.0; self.total_s=0.0
        self.s_hours=0.0; self.s_goal=''; self.pomo=False; self.pomo_ph='work'
        self.pomo_end=0.0; self.p_start=0.0; self._pending=[]; self._notifs=[]
        atexit.register(self._on_exit)
        self.at.start(); register_startup(); self.cfg.save()
        self.root=tk.Tk(); self.root.title('SL — Selfish v2.0'); self.root.configure(bg=C['bg'])
        self.root.protocol('WM_DELETE_WINDOW',lambda:None)
        setup_style()
        try: self.root.iconphoto(True,tk.PhotoImage(data=_ICON_B64))
        except: pass
        log('=== SL v2.0 started ==='); log(f'Data: {DATA_DIR}')
        self._screen_lock(); self.root.mainloop()

    def _on_exit(self):
        self.running=False; self.at.stop(); self.pl.record_shutdown(); unblock_sites()

    def _clear(self):
        for w in self.root.winfo_children():
            try: w.destroy()
            except: pass

    def _fs(self):
        sw=self.root.winfo_screenwidth(); sh=self.root.winfo_screenheight()
        self.root.geometry(f'{sw}x{sh}+0+0'); self.root.attributes('-fullscreen',True)
        self.root.attributes('-topmost',True); self.root.resizable(False,False)

    # ── Lock Screen ───────────────────────────────────────────
    def _screen_lock(self):
        self._clear(); self._fs()
        self.root.bind('<Alt-F4>',lambda e:'break')
        self.root.bind('<Escape>',lambda e:'break')
        self.root.bind('<Return>',lambda e:self._chk_pw())
        sw=self.root.winfo_screenwidth(); sh=self.root.winfo_screenheight()
        bg_cv=tk.Canvas(self.root,bg=C['bg'],highlightthickness=0); bg_cv.place(relwidth=1,relheight=1)
        bg_cv.create_rectangle(0,0,sw,3,fill=C['acc'],outline='')
        c=tk.Frame(self.root,bg=C['bg']); c.place(relx=.5,rely=.5,anchor='center')
        tk.Label(c,text='SL',font=('Segoe UI',72,'bold'),bg=C['bg'],fg=C['acc']).pack()
        tk.Label(c,text='SELFISH  ·  PERSONAL PERFORMANCE SYSTEM v2.0',
                 font=('Segoe UI',11),bg=C['bg'],fg=C['sub']).pack(pady=(0,4))
        tk.Frame(c,bg=C['brd2'],height=1,width=340).pack(pady=24)
        mk_lbl(c,'Parolni kiriting',12,C['sub']).pack(pady=(0,8))
        brd=tk.Frame(c,bg=C['acc'],padx=1,pady=1); brd.pack()
        self._pw_var=tk.StringVar()
        self._pw_ent=tk.Entry(brd,textvariable=self._pw_var,show='●',
                              font=('Segoe UI Mono',18),bg=C['inp'],fg=C['txt'],
                              insertbackground=C['acc3'],relief='flat',width=24,justify='center')
        self._pw_ent.pack(ipady=13,ipadx=8); self._pw_ent.focus_set()
        self._pw_err=mk_lbl(c,'',11,C['red3']); self._pw_err.pack(pady=6)
        mk_btn(c,'  KIRISH  →',self._chk_pw,C['acc'],fs=12,px=44,py=14).pack(pady=4)
        self._clk_lbl=mk_lbl(c,'',10,C['sub']); self._clk_lbl.pack(pady=(22,0))
        self._tick()
        mk_lbl(c,'⚠  Noto\'g\'ri parol → kompyuter o\'chadi',9,C['sub']).pack(pady=(4,0))
        mk_lbl(self.root,'SL v2.0  ·  Selfish',8,C['brd2']).place(relx=1,rely=1,anchor='se',x=-12,y=-8)

    def _tick(self):
        if self._clk_lbl.winfo_exists():
            self._clk_lbl.config(text=datetime.now().strftime('%A, %d %B %Y    %H:%M:%S'))
            self.root.after(1000,self._tick)

    def _chk_pw(self):
        if self._pw_var.get()==self.cfg.get('password'):
            log('Auth OK'); self._screen_tasks()
        else:
            log('WRONG → SHUTDOWN'); self._pw_err.config(text='❌  Noto\'g\'ri parol! O\'chirilmoqda...')
            self._pw_ent.config(state='disabled'); self.root.update()
            for i in (3,2,1):
                self._pw_err.config(text=f'❌  {i} soniyada o\'chadi...'); self.root.update(); time.sleep(1)
            do_shutdown(); self.root.after(7000,self.root.destroy)

    # ── Task Input ────────────────────────────────────────────
    def _screen_tasks(self):
        self._clear(); self._fs()
        self.root.unbind('<Return>'); self.root.bind('<Alt-F4>',lambda e:'break')
        self._pending=[]
        c=tk.Frame(self.root,bg=C['bg']); c.place(relx=.5,rely=.5,anchor='center')
        tk.Label(c,text='📋',font=('Segoe UI Emoji',48),bg=C['bg'],fg=C['acc3']).pack(pady=(0,4))
        mk_lbl(c,'BUGUNGI VAZIFALAR',22,C['acc'],bold=True).pack()
        mk_lbl(c,'Ixtiyoriy — o\'tkazib yuborish mumkin',11,C['sub']).pack(pady=(2,0))
        tk.Frame(c,bg=C['brd2'],height=1,width=500).pack(pady=22)
        row=tk.Frame(c,bg=C['bg']); row.pack()
        self._te=tk.StringVar(); brd,te=mk_entry(row,self._te,width=40,ipy=10); brd.pack(side='left'); te.focus_set()
        lf=tk.Frame(c,bg=C['card'],width=520,height=200); lf.pack(pady=12); lf.pack_propagate(False)
        cv2=tk.Canvas(lf,bg=C['card'],highlightthickness=0); sb=tk.Scrollbar(lf,orient='vertical',command=cv2.yview)
        cv2.configure(yscrollcommand=sb.set); sb.pack(side='right',fill='y'); cv2.pack(fill='both',expand=True)
        inn=tk.Frame(cv2,bg=C['card']); cv2.create_window((0,0),window=inn,anchor='nw')
        inn.bind('<Configure>',lambda e:cv2.configure(scrollregion=cv2.bbox('all')))
        def refresh():
            for w in inn.winfo_children(): w.destroy()
            if not self._pending: mk_lbl(inn,'Hali vazifa qo\'shilmagan',9,C['sub'],bg=C['card']).pack(pady=16); return
            for i,t in enumerate(self._pending):
                r2=tk.Frame(inn,bg=C['card']); r2.pack(fill='x',padx=12,pady=3)
                mk_lbl(r2,f'{i+1}.',9,C['sub'],bg=C['card']).pack(side='left',padx=4)
                mk_lbl(r2,t,10,bg=C['card']).pack(side='left',fill='x',expand=True)
                mk_btn(r2,'✕',lambda ii=i:(self._pending.pop(ii),refresh()),C['card'],fg=C['red3'],fs=8,px=4,py=2).pack(side='right',padx=4)
        def add_t(e=None):
            t=self._te.get().strip()
            if t: self._pending.append(t); self._te.set(''); refresh(); te.focus_set()
        te.bind('<Return>',add_t)
        mk_btn(row,'+ Qo\'sh',add_t,C['acc'],fs=10,px=14,py=10).pack(side='left',padx=(8,0))
        refresh(); mk_lbl(c,'↵ Enter — qo\'shish',8,C['sub']).pack()
        br=tk.Frame(c,bg=C['bg']); br.pack(pady=18)
        mk_btn(br,'O\'TKAZIB YUBORISH',self._screen_dur,C['inp'],fg=C['dim'],fs=10,px=20,py=12).pack(side='left',padx=8)
        mk_btn(br,'  ✅  DAVOM ETISH',self._screen_dur,C['grn'],fs=12,px=28,py=13).pack(side='left',padx=8)

    # ── Duration ──────────────────────────────────────────────
    def _screen_dur(self):
        self._clear(); self._fs()
        self.root.bind('<Alt-F4>',lambda e:'break'); self.root.bind('<Return>',lambda e:self._start())
        c=tk.Frame(self.root,bg=C['bg']); c.place(relx=.5,rely=.5,anchor='center')
        tk.Label(c,text='⚡',font=('Segoe UI Emoji',48),bg=C['bg'],fg=C['yel3']).pack()
        mk_lbl(c,'ISH SESSIYASI',22,C['acc'],bold=True).pack()
        mk_lbl(c,'Vaqt va maqsadingizni belgilang',11,C['sub']).pack(pady=(2,0))
        tk.Frame(c,bg=C['brd2'],height=1,width=420).pack(pady=22)
        mk_lbl(c,'Necha soat?',13,C['sub']).pack()
        brd1=tk.Frame(c,bg=C['acc'],padx=1,pady=1); brd1.pack(pady=8)
        self._h_var=tk.StringVar(value='2')
        h_ent=tk.Entry(brd1,textvariable=self._h_var,font=('Segoe UI Mono',34,'bold'),
                       bg=C['inp'],fg=C['acc3'],insertbackground=C['acc3'],relief='flat',width=7,justify='center')
        h_ent.pack(ipady=10); h_ent.focus_set()
        mk_lbl(c,'soat  (1  ·  1.5  ·  2  ·  3)',10,C['sub']).pack()
        mk_lbl(c,'\nBugungi maqsad (ixtiyoriy):',12,C['sub']).pack()
        self._g_var=tk.StringVar(); brd2,_=mk_entry(c,self._g_var,width=42,ipy=9); brd2.pack(pady=6)
        opt=tk.Frame(c,bg=C['bg']); opt.pack(pady=10)
        self._pomo_v=tk.BooleanVar(value=False); self._blk_v=tk.BooleanVar(value=self.cfg.get('block_sites',True))
        for text,var in [('🍅  Pomodoro (25 min ish / 5 min tanaffus)',self._pomo_v),('🚫  Ijtimoiy tarmoqlarni bloklash',self._blk_v)]:
            tk.Checkbutton(opt,text=f'  {text}',variable=var,font=('Segoe UI',11),bg=C['bg'],fg=C['sub'],
                           activebackground=C['bg'],selectcolor=C['inp'],relief='flat',cursor='hand2').pack(pady=3,anchor='w')
        mk_btn(c,'   🚀  BOSHLASH   ',self._start,C['grn'],fs=13,px=36,py=14).pack(pady=16)
        mk_lbl(c,'↵ Enter — boshlash',9,C['sub']).pack()

    def _start(self):
        try:
            h=float(self._h_var.get().replace(',','.')); assert 0<h<=24
        except:
            messagebox.showerror('Xato','To\'g\'ri soat kiriting!',parent=self.root); return
        goal=self._g_var.get().strip(); do_blk=self._blk_v.get()
        self.cfg.set('block_sites',do_blk)
        self.s_hours=h; self.s_goal=goal; self.pomo=self._pomo_v.get()
        self.running=True; self.paused=False; self.total_s=h*3600
        self.end_ts=time.time()+self.total_s; self.pomo_ph='work'
        self.pomo_end=time.time()+self.cfg.get('pomo_work',25)*60
        self.tm.new(goal=goal,hours=h)
        for t in self._pending: self.tm.add(t)
        if do_blk: block_sites()
        log(f'Session: {h}h goal="{goal}"')
        self._dashboard()
        threading.Thread(target=self._timer_loop,daemon=True).start()
        threading.Thread(target=self._notif_loop,daemon=True).start()

    # ── Dashboard ─────────────────────────────────────────────
    def _dashboard(self):
        self._clear()
        sw=self.root.winfo_screenwidth(); W,H=500,680
        self.root.geometry(f'{W}x{H}+{sw-W-12}+10')
        self.root.attributes('-fullscreen',False); self.root.attributes('-topmost',True)
        self.root.resizable(False,False); self.root.configure(bg=C['card'])
        self.root.protocol('WM_DELETE_WINDOW',self._close_guard)
        self.root.unbind('<Return>'); self.root.unbind('<Alt-F4>')
        hdr=tk.Frame(self.root,bg=C['acc'],pady=7); hdr.pack(fill='x')
        tk.Label(hdr,text='SL  ·  SELFISH  ·  FOCUS MODE ON',font=('Segoe UI',11,'bold'),bg=C['acc'],fg=C['wht']).pack()
        self._nb=ttk.Notebook(self.root,style='SL.TNotebook'); self._nb.pack(fill='both',expand=True,padx=6,pady=4)
        self._tf=tk.Frame(self._nb,bg=C['card2']); self._tt=tk.Frame(self._nb,bg=C['card2'])
        self._ty=tk.Frame(self._nb,bg=C['card2']); self._tj=tk.Frame(self._nb,bg=C['card2'])
        self._nb.add(self._tf,text='⏱  Focus'); self._nb.add(self._tt,text='📋  Vazifalar')
        self._nb.add(self._ty,text='📥  YouTube'); self._nb.add(self._tj,text='📔  Journal')
        self._build_focus(); self._build_tasks(); self._build_yt(); self._build_jour()
        bar=tk.Frame(self.root,bg=C['card'],pady=6); bar.pack(fill='x',padx=8)
        self._pbtn=mk_btn(bar,'⏸  Pauza',self._toggle_pause,C['inp'],fg=C['dim'],fs=9,px=10,py=7)
        self._pbtn.pack(side='left',expand=True,fill='x',padx=2)
        mk_btn(bar,'🔐  Vault',self._open_vault,C['inp'],fg=C['acc3'],fs=9,px=10,py=7).pack(side='left',expand=True,fill='x',padx=2)
        mk_btn(bar,'✔  Tugatish',self._ask_done,C['acc'],fs=9,px=10,py=7).pack(side='right',expand=True,fill='x',padx=2)

    def _build_focus(self):
        p=self._tf; tk.Frame(p,bg=C['card2'],height=10).pack()
        mk_lbl(p,'⏱  Qolgan vaqt',9,C['sub'],bg=C['card2']).pack()
        self._tlbl=tk.Label(p,text='00:00:00',font=('Segoe UI Mono',44,'bold'),bg=C['card2'],fg=C['acc3']); self._tlbl.pack()
        self._pvar=tk.DoubleVar(value=0)
        ttk.Progressbar(p,variable=self._pvar,maximum=100,style='SL.Horizontal.TProgressbar',length=430).pack(pady=(4,2))
        self._pctlbl=mk_lbl(p,'0%  tamamlandi',8,C['sub'],bg=C['card2']); self._pctlbl.pack()
        self._actual_lbl=mk_lbl(p,'',8,C['dim'],bg=C['card2']); self._actual_lbl.pack()
        if self.s_goal:
            gf=tk.Frame(p,bg=C['inp'],padx=12,pady=8); gf.pack(fill='x',padx=14,pady=10)
            mk_lbl(gf,'🎯  Maqsad:',8,C['sub'],bold=True,bg=C['inp']).pack(anchor='w')
            mk_lbl(gf,self.s_goal,10,bold=True,bg=C['inp']).pack(anchor='w',pady=2)
        if self.pomo:
            self._plbl=mk_lbl(p,'🍅 ...',9,C['yel2'],bold=True,bg=C['card2']); self._plbl.pack(pady=4)
        bt='✅  Saytlar bloklangan' if self.cfg.get('block_sites') else '⚠  Bloklash o\'chirilgan'
        bc=C['grn2'] if self.cfg.get('block_sites') else C['yel2']
        self._stlbl=mk_lbl(p,bt,8,bc,bg=C['card2']); self._stlbl.pack(pady=(8,2))
        st=datetime.now().strftime('%H:%M'); et=datetime.fromtimestamp(self.end_ts).strftime('%H:%M')
        mk_lbl(p,f'Reja: {self.s_hours}h  ·  {st} → {et}',8,C['sub'],bg=C['card2']).pack()
        self._ticker=mk_lbl(p,'',8,C['sub'],bg=C['card2']); self._ticker.config(wraplength=440,justify='center'); self._ticker.pack(pady=8)
        self._spin()

    def _spin(self):
        if hasattr(self,'_ticker') and self._ticker.winfo_exists():
            q=random.choice(QUOTES); self._ticker.config(text=f'{q[0]}  {q[2]}')
            self.root.after(9000,self._spin)

    def _build_tasks(self):
        p=self._tt; mk_lbl(p,'📋  Vazifalar',10,C['acc3'],bold=True,bg=C['card2']).pack(anchor='w',padx=12,pady=(10,4))
        outer=tk.Frame(p,bg=C['card2']); outer.pack(fill='both',expand=True,padx=8)
        cv=tk.Canvas(outer,bg=C['card2'],highlightthickness=0); sb=tk.Scrollbar(outer,orient='vertical',command=cv.yview)
        cv.configure(yscrollcommand=sb.set); sb.pack(side='right',fill='y'); cv.pack(side='left',fill='both',expand=True)
        self._ti=tk.Frame(cv,bg=C['card2']); cv.create_window((0,0),window=self._ti,anchor='nw')
        self._ti.bind('<Configure>',lambda e:cv.configure(scrollregion=cv.bbox('all')))
        self._render_tasks()
        af=tk.Frame(p,bg=C['card2']); af.pack(fill='x',padx=8,pady=6)
        self._ntv=tk.StringVar(); brd=tk.Frame(af,bg=C['brd2'],padx=1,pady=1); brd.pack(side='left',fill='x',expand=True)
        nt=tk.Entry(brd,textvariable=self._ntv,font=('Segoe UI',10),bg=C['inp'],fg=C['txt'],insertbackground=C['acc3'],relief='flat')
        nt.pack(fill='x',ipady=6,ipadx=4)
        def _add(e=None):
            t=self._ntv.get().strip()
            if t: self.tm.add(t); self._ntv.set(''); self._render_tasks()
        nt.bind('<Return>',_add); mk_btn(af,'+',_add,C['acc'],fs=10,px=10,py=6).pack(side='left',padx=(4,0))

    def _render_tasks(self):
        for w in self._ti.winfo_children():
            try: w.destroy()
            except: pass
        tasks=(self.tm.cur or {}).get('tasks',[])
        if not tasks: mk_lbl(self._ti,'Vazifa yo\'q',9,C['sub'],bg=C['card2']).pack(pady=12); return
        for i,t in enumerate(tasks):
            bv=tk.BooleanVar(value=t['done'])
            row=tk.Frame(self._ti,bg=C['card2']); row.pack(fill='x',padx=4,pady=2)
            def tog(ii=i,var=bv): (self.tm.complete if var.get() else self.tm.uncomplete)(ii); self._render_tasks()
            tk.Checkbutton(row,variable=bv,command=tog,bg=C['card2'],activebackground=C['card2'],selectcolor=C['inp'],relief='flat',cursor='hand2').pack(side='left')
            fc=C['grn3'] if t['done'] else C['txt']; ff=('Segoe UI',9,'overstrike') if t['done'] else ('Segoe UI',9)
            lbl=tk.Label(row,text=t['text'],font=ff,bg=C['card2'],fg=fc,wraplength=390,justify='left',cursor='hand2'); lbl.pack(side='left',fill='x',expand=True)
            lbl.bind('<Button-1>',lambda e,ii=i,v=bv:(v.set(not v.get()),tog(ii,v)))

    def _build_yt(self):
        p=self._ty
        mk_lbl(p,'📥  YouTube Yuklovchi (yt-dlp)',10,C['acc3'],bold=True,bg=C['card2']).pack(anchor='w',padx=12,pady=(10,4))
        self._yt_url=tk.StringVar(); brd=tk.Frame(p,bg=C['brd2'],padx=1,pady=1); brd.pack(fill='x',padx=10)
        tk.Entry(brd,textvariable=self._yt_url,font=('Segoe UI',10),bg=C['inp'],fg=C['txt'],insertbackground=C['acc3'],relief='flat').pack(fill='x',ipady=8,ipadx=6)
        of=tk.Frame(p,bg=C['card2']); of.pack(fill='x',padx=10,pady=8)
        ql=tk.Frame(of,bg=C['card2']); ql.pack(side='left')
        self._yt_fmt=tk.StringVar(value='720')
        for v,t in [('1080','1080p'),('720','720p'),('480','480p'),('audio','🎵 MP3')]:
            tk.Radiobutton(ql,text=t,variable=self._yt_fmt,value=v,font=('Segoe UI',9),bg=C['card2'],fg=C['sub'],activebackground=C['card2'],selectcolor=C['inp'],relief='flat').pack(anchor='w',pady=1)
        ph2=tk.Frame(of,bg=C['card2']); ph2.pack(side='left',padx=(18,0))
        mk_lbl(ph2,'Papka:',8,C['sub'],bg=C['card2']).pack(anchor='w')
        self._yt_path=tk.StringVar(value=self.cfg.get('dl_path',''))
        brd2=tk.Frame(ph2,bg=C['brd2'],padx=1,pady=1); brd2.pack()
        tk.Entry(brd2,textvariable=self._yt_path,font=('Segoe UI',8),bg=C['inp'],fg=C['txt'],insertbackground=C['acc3'],relief='flat',width=22).pack(ipady=5,ipadx=4)
        def chdir():
            d=filedialog.askdirectory(parent=self.root,initialdir=self._yt_path.get())
            if d: self._yt_path.set(d); self.cfg.set('dl_path',d)
        mk_btn(ph2,'📁',chdir,C['inp'],fg=C['acc3'],fs=8,px=8,py=4).pack(pady=3)
        mk_btn(p,'  ⬇  YUKLAB OLISH  ',self._yt_go,C['acc'],fs=11,px=22,py=10).pack(pady=6)
        self._yt_pv=tk.DoubleVar(value=0)
        ttk.Progressbar(p,variable=self._yt_pv,maximum=100,style='SL.Horizontal.TProgressbar',length=450).pack(padx=12)
        self._yt_st=mk_lbl(p,'URL kiriting',8,C['sub'],bg=C['card2']); self._yt_st.pack(pady=4)
        self._yt_hf=tk.Frame(p,bg=C['card2']); self._yt_hf.pack(fill='x',padx=12); self._yt_hist=[]

    def _yt_go(self):
        url=self._yt_url.get().strip()
        if not url: messagebox.showwarning('URL','YouTube URL kiriting!',parent=self.root); return
        path=self._yt_path.get().strip()
        if not os.path.isdir(path): messagebox.showerror('Papka',path,parent=self.root); return
        self._yt_pv.set(0); self._yt_st.config(text='⚙ tekshirilmoqda...',fg=C['yel2']); self.root.update()
        def run():
            if not ensure_ytdlp():
                self.root.after(0,lambda:self._yt_st.config(text='❌ yt-dlp o\'rnatilmadi!',fg=C['red3'])); return
            self.root.after(0,lambda:self._yt_st.config(text='⬇ Yuklanmoqda...',fg=C['acc3']))
            yt_download(self._yt_url.get().strip(),self._yt_fmt.get(),path,
                        lambda pv:self.root.after(0,lambda pp=pv:self._yt_pv.set(pp)),
                        lambda s:self.root.after(0,lambda ss=s:self._yt_st.config(text=ss,fg=C['acc3'])),
                        self._yt_done,self._yt_err)
        threading.Thread(target=run,daemon=True).start()

    def _yt_done(self,title):
        self._yt_hist.append(f'✅ {title[:45]}')
        if len(self._yt_hist)>5: self._yt_hist=self._yt_hist[-5:]
        def upd():
            self._yt_pv.set(100); self._yt_st.config(text=f'✅ {title[:40]}',fg=C['grn2']); self._yt_url.set('')
            for w in self._yt_hf.winfo_children(): w.destroy()
            for h in reversed(self._yt_hist): mk_lbl(self._yt_hf,h,8,C['sub'],bg=C['card2']).pack(anchor='w')
        self.root.after(0,upd)

    def _yt_err(self,err): self.root.after(0,lambda:self._yt_st.config(text=f'❌ {err[:80]}',fg=C['red3']))

    def _build_jour(self):
        p=self._tj
        mk_lbl(p,f'📔  Journal  ·  {datetime.now().strftime("%d %B %Y")}',10,C['acc3'],bold=True,bg=C['card2']).pack(anchor='w',padx=12,pady=(10,4))
        if self.s_goal:
            gf=tk.Frame(p,bg=C['inp'],padx=10,pady=5); gf.pack(fill='x',padx=10,pady=(0,6))
            mk_lbl(gf,f'🎯 {self.s_goal}',9,C['sub'],bg=C['inp']).pack(anchor='w')
        pf=tk.Frame(p,bg=C['card2']); pf.pack(fill='x',padx=10,pady=(0,4))
        mk_lbl(pf,'💡 Tez:',8,C['sub'],bg=C['card2']).pack(side='left')
        self._jta=None
        for q in ['Bugun nima yaxshi?','Nima chalg\'itdi?','Ertaga reja?']:
            mk_btn(pf,f'+ {q.split("?")[0]}',
                   lambda qq=q:(self._jta and self._jta.insert('end',f'\n• {qq}\n')),
                   C['inp'],fg=C['acc3'],fs=7,px=6,py=3).pack(side='left',padx=2)
        brd=tk.Frame(p,bg=C['brd2'],padx=1,pady=1); brd.pack(fill='both',expand=True,padx=10,pady=4)
        self._jta=scrolledtext.ScrolledText(brd,font=('Segoe UI',10),bg=C['inp'],fg=C['txt'],
                                             insertbackground=C['acc3'],wrap='word',relief='flat',padx=10,pady=8)
        self._jta.pack(fill='both',expand=True); self._jta.focus_set()
        mk_btn(p,'  💾  SAQLASH  ',self._save_jour,C['grn'],fs=11,px=22,py=10).pack(pady=8)

    def _save_jour(self):
        content=self._jta.get('1.0','end-1c').strip()
        if not content: messagebox.showwarning('Bo\'sh','Journal yozing!',parent=self.root); return
        actual_h=round((time.time()-self.tm._start_ts)/3600,3) if self.tm._start_ts else 0
        self.jm.add(content,goal=self.s_goal,actual_h=actual_h)
        self._jta.delete('1.0','end')
        messagebox.showinfo('✅',f'Journal #{len(self.jm.entries)} saqlandi!\n{now_str()}',parent=self.root)

    # ── Timer loops ───────────────────────────────────────────
    def _timer_loop(self):
        while self.running:
            if not self.paused:
                rem=max(0.0,self.end_ts-time.time()); pct=min(100.0,(self.total_s-rem)/self.total_s*100 if self.total_s>0 else 0)
                col=C['red3'] if rem<300 else C['yel3'] if rem<900 else C['acc3']
                actual_s=time.time()-self.tm._start_ts if self.tm._start_ts else 0
                try:
                    self._tlbl.config(text=fmt_time(rem),fg=col); self._pvar.set(pct)
                    self._pctlbl.config(text=f'{pct:.0f}%  tamamlandi')
                    self._actual_lbl.config(text=f'Haqiqiy: {fmt_dur(actual_s)}  ·  Reja: {self.s_hours:.1f}h')
                except: break
                if self.pomo and hasattr(self,'_plbl'):
                    pr=max(0.0,self.pomo_end-time.time()); pn='ISH 🔥' if self.pomo_ph=='work' else 'TANAFFUS ☕'
                    try: self._plbl.config(text=f'🍅 {pn} · {fmt_time(pr)}',fg=C['grn2'] if self.pomo_ph=='work' else C['yel2'])
                    except: pass
                    if pr<=0: self._switch_pomo()
                if rem<=0: self.running=False; self.root.after(0,self._screen_done); break
            time.sleep(0.5)

    def _switch_pomo(self):
        if self.pomo_ph=='work':
            self.pomo_ph='break'; self.pomo_end=time.time()+self.cfg.get('pomo_break',5)*60
            self.root.after(0,lambda:self._show_notif('☕ Pomodoro — TANAFFUS','25 min tugadi! 5 min tanaffus.'))
        else:
            self.pomo_ph='work'; self.pomo_end=time.time()+self.cfg.get('pomo_work',25)*60
            self.root.after(0,lambda:self._show_notif('🔥 Pomodoro — ISH','Tanaffus tugadi! Focus! 🎯'))

    def _notif_loop(self):
        iv=self.cfg.get('notif_min',15)*60
        while self.running:
            time.sleep(iv)
            if not self.running or self.paused: continue
            q=random.choice(QUOTES); self.root.after(0,lambda t=f'{q[0]} {q[1]}',b=q[2]:self._show_notif(t,b))

    def _show_notif(self,title,msg):
        try:
            sw=self.root.winfo_screenwidth(); sh=self.root.winfo_screenheight(); W,H=375,160
            pop=tk.Toplevel(self.root); pop.attributes('-topmost',True); pop.overrideredirect(True)
            pop.configure(bg=C['card']); pop.geometry(f'{W}x{H}+{sw-W-10}+{sh-H-55}')
            brd=tk.Frame(pop,bg=C['acc'],padx=2,pady=2); brd.pack(fill='both',expand=True)
            inn=tk.Frame(brd,bg=C['card'],padx=14,pady=10); inn.pack(fill='both',expand=True)
            top=tk.Frame(inn,bg=C['card']); top.pack(fill='x')
            tk.Label(top,text=title,font=('Segoe UI',11,'bold'),bg=C['card'],fg=C['acc3']).pack(side='left')
            tk.Button(top,text='✕',font=('Segoe UI',9),bg=C['card'],fg=C['sub'],activebackground=C['card'],
                      activeforeground=C['red3'],relief='flat',bd=0,cursor='hand2',command=pop.destroy).pack(side='right')
            tk.Frame(inn,bg=C['brd2'],height=1).pack(fill='x',pady=4)
            tk.Label(inn,text=msg,font=('Segoe UI',9),bg=C['card'],fg=C['txt'],justify='left',wraplength=340).pack(anchor='w')
            mk_btn(inn,'OK 💪',pop.destroy,C['acc'],fs=8,px=10,py=4).pack(anchor='e',pady=(6,0))
            pop.after(10000,lambda:pop.destroy() if pop.winfo_exists() else None)
        except Exception as e: log(f'Notif: {e}')

    def _toggle_pause(self):
        if not self.paused:
            self.paused=True; self.p_start=time.time(); self._pbtn.config(text='▶  Davom et')
            self._stlbl.config(text='⏸ PAUZA',fg=C['yel2'])
        else:
            self.paused=False; self.end_ts+=time.time()-self.p_start; self._pbtn.config(text='⏸  Pauza')
            bt='✅ Bloklangan' if self.cfg.get('block_sites') else '⚠ Bloqsiz'
            self._stlbl.config(text=bt,fg=C['grn2'] if self.cfg.get('block_sites') else C['yel2'])

    def _ask_done(self):
        actual_s=time.time()-self.tm._start_ts if self.tm._start_ts else 0
        if messagebox.askyesno('Tugatish',f'Haqiqiy vaqt: {fmt_dur(actual_s)}\n\nHA → Kompyuter o\'chiriladi',parent=self.root):
            self.running=False; self.tm.end(); self.root.after(0,self._screen_done)

    def _close_guard(self):
        dlg=tk.Toplevel(self.root); dlg.title('Yopish'); dlg.configure(bg=C['bg'])
        dlg.attributes('-topmost',True); dlg.resizable(False,False)
        sw=self.root.winfo_screenwidth(); sh=self.root.winfo_screenheight()
        dlg.geometry(f'380x200+{(sw-380)//2}+{(sh-200)//2}')
        mk_lbl(dlg,'🔒  Parolni kiriting',14,bold=True).pack(pady=(18,4))
        var=tk.StringVar(); brd=tk.Frame(dlg,bg=C['brd2'],padx=1,pady=1); brd.pack(pady=8)
        ent=tk.Entry(brd,textvariable=var,show='●',font=('Segoe UI Mono',14),bg=C['inp'],fg=C['txt'],
                     insertbackground=C['wht'],relief='flat',width=24,justify='center')
        ent.pack(ipady=9); ent.focus_set()
        def confirm():
            if var.get()==self.cfg.get('password'):
                self.running=False; unblock_sites(); dlg.destroy()
                try: self.root.destroy()
                except: pass
                sys.exit(0)
            else: messagebox.showwarning('Xato','Noto\'g\'ri!',parent=dlg); dlg.destroy()
        mk_btn(dlg,'Tasdiqlash',confirm,C['acc'],fs=11,px=24,py=9).pack(pady=4)
        ent.bind('<Return>',lambda e:confirm()); dlg.grab_set(); dlg.protocol('WM_DELETE_WINDOW',dlg.destroy)

    # ── Vault ─────────────────────────────────────────────────
    def _open_vault(self):
        dlg=tk.Toplevel(self.root); dlg.title('Vault'); dlg.configure(bg=C['bg'])
        dlg.attributes('-topmost',True); dlg.resizable(False,False)
        sw=self.root.winfo_screenwidth(); sh=self.root.winfo_screenheight()
        dlg.geometry(f'400x260+{(sw-400)//2}+{(sh-260)//2}')
        tk.Label(dlg,text='🔐',font=('Segoe UI Emoji',40),bg=C['bg'],fg=C['acc3']).pack(pady=(18,4))
        mk_lbl(dlg,'VAULT',22,C['acc'],bold=True).pack(); mk_lbl(dlg,'Vault paroli:',9,C['sub']).pack(pady=(10,2))
        brd=tk.Frame(dlg,bg=C['acc'],padx=1,pady=1); brd.pack(pady=4)
        vv=tk.StringVar()
        ve=tk.Entry(brd,textvariable=vv,show='●',font=('Segoe UI Mono',15),bg=C['inp'],fg=C['txt'],
                    insertbackground=C['acc3'],relief='flat',width=24,justify='center')
        ve.pack(ipady=10,ipadx=8); ve.focus_set()
        el=mk_lbl(dlg,'',9,C['red3']); el.pack(pady=3)
        def try_open():
            if ph(vv.get())!=self.cfg.get('vault_pw_hash'): el.config(text='❌ Noto\'g\'ri!'); return
            if not self.vm.unlock(vv.get()): el.config(text='❌ Xato!'); return
            dlg.destroy(); self._vault_win()
        mk_btn(dlg,'  🔓  OCHISH  ',try_open,C['acc'],fs=12,px=30,py=11).pack(pady=6)
        ve.bind('<Return>',lambda e:try_open())
        mk_lbl(dlg,'Default: VAULT2024',7,C['sub']).pack()
        dlg.grab_set(); dlg.protocol('WM_DELETE_WINDOW',dlg.destroy)

    def _vault_win(self):
        vw=tk.Toplevel(self.root); vw.title('SL Vault'); vw.configure(bg=C['bg'])
        vw.attributes('-topmost',True); vw.resizable(True,True)
        sw=self.root.winfo_screenwidth(); sh=self.root.winfo_screenheight()
        W2,H2=min(1150,sw-40),min(740,sh-80); vw.geometry(f'{W2}x{H2}+{(sw-W2)//2}+{(sh-H2)//2}')
        hdr=tk.Frame(vw,bg=C['acc'],pady=8); hdr.pack(fill='x')
        tk.Label(hdr,text='🔐  SL  VAULT  v2.0',font=('Segoe UI',12,'bold'),bg=C['acc'],fg=C['wht']).pack(side='left',padx=16)
        mk_btn(hdr,'🔒 Yopish',lambda:(self.vm.lock(),vw.destroy()),C['acc2'],fs=9,px=12,py=5).pack(side='right',padx=10)
        nb=ttk.Notebook(vw,style='SL.TNotebook'); nb.pack(fill='both',expand=True,padx=8,pady=6)
        tabs={}
        for key,label in [('jour','📖 Jurnallar'),('sess','📊 Sessiyalar'),('apps','📱 App Tahlili'),
                           ('pwr','🔌 Quvvat'),('note','📝 Shaxsiy'),('ai','🤖 AI'),('plan','🗺 Reja Kanvasi')]:
            f=tk.Frame(nb,bg=C['bg']); tabs[key]=f; nb.add(f,text=label)
        self._build_v_journals(tabs['jour']); self._build_v_sessions(tabs['sess'])
        self._build_v_apps(tabs['apps']); self._build_v_power(tabs['pwr'])
        self._build_v_notes(tabs['note']); self._build_v_ai(tabs['ai'])
        self._build_v_plan(tabs['plan'])
        # Bottom bar
        bot=tk.Frame(vw,bg=C['card'],pady=4); bot.pack(fill='x',padx=8,pady=(0,4))
        mk_lbl(bot,f'Data: {DATA_DIR}',7,C['sub'],bg=C['card']).pack(side='left',padx=8)
        mk_btn(bot,'🗑 Uninstall',lambda:self._uninstall_dlg(vw),C['red'],fs=8,px=10,py=4).pack(side='right',padx=8)
        vw.protocol('WM_DELETE_WINDOW',lambda:(self.vm.lock(),vw.destroy()))

    def _build_v_journals(self,parent):
        entries=self.jm.entries
        top=tk.Frame(parent,bg=C['bg']); top.pack(fill='x',padx=12,pady=10)
        mk_lbl(top,f'📖 Jurnallar ({len(entries)} ta)',12,C['acc3'],bold=True).pack(side='left')
        sv=tk.StringVar(); brd,se=mk_entry(top,sv,width=22,ipy=4); brd.pack(side='right')
        paned=tk.PanedWindow(parent,orient='horizontal',bg=C['bg'],sashwidth=4)
        paned.pack(fill='both',expand=True,padx=8,pady=4)
        lf=tk.Frame(paned,bg=C['card'],width=220); paned.add(lf,minsize=180)
        rf=tk.Frame(paned,bg=C['card']); paned.add(rf,minsize=300)
        dh=mk_lbl(rf,'← Tanlang',9,C['sub'],bg=C['card']); dh.pack(anchor='w',padx=12,pady=8)
        dta=scrolledtext.ScrolledText(rf,font=('Segoe UI',10),bg=C['inp'],fg=C['txt'],insertbackground=C['acc3'],wrap='word',relief='flat',state='disabled')
        dta.pack(fill='both',expand=True,padx=6,pady=4)
        lf_cv=tk.Canvas(lf,bg=C['card'],highlightthickness=0); lf_sb=tk.Scrollbar(lf,orient='vertical',command=lf_cv.yview)
        lf_cv.configure(yscrollcommand=lf_sb.set); lf_sb.pack(side='right',fill='y'); lf_cv.pack(fill='both',expand=True)
        lf_in=tk.Frame(lf_cv,bg=C['card']); lf_cv.create_window((0,0),window=lf_in,anchor='nw')
        lf_in.bind('<Configure>',lambda e:lf_cv.configure(scrollregion=lf_cv.bbox('all')))
        def show(e):
            dta.config(state='normal'); dta.delete('1.0','end')
            dta.insert('end',f"📅 {e['datetime']}\n⏱ {e.get('actual_h',0):.2f}h  🎯 {e.get('goal','—')}\n{'─'*48}\n\n",'hdr')
            dta.insert('end',e['content']); dta.tag_config('hdr',foreground=C['sub'],font=('Segoe UI',8))
            dta.config(state='disabled'); dh.config(text=f"📅 {e['date']} {e['time']}")
        def refresh(q=''):
            for w in lf_in.winfo_children(): w.destroy()
            filt=[e for e in reversed(entries) if q.lower() in e.get('content','').lower() or q.lower() in e.get('date','').lower()]
            if not filt: mk_lbl(lf_in,'Topilmadi',8,C['sub'],bg=C['card']).pack(pady=10); return
            for e in filt:
                row=tk.Frame(lf_in,bg=C['card'],padx=8,pady=5,cursor='hand2'); row.pack(fill='x')
                mk_lbl(row,f"📅 {e['date']} {e['time']}",8,C['acc3'],bg=C['card']).pack(anchor='w')
                mk_lbl(row,e['content'][:40].replace('\n',' ')+'...',8,C['sub'],bg=C['card']).pack(anchor='w')
                if e.get('actual_h'): mk_lbl(row,f"⏱ {fmt_dur(e['actual_h']*3600)}",7,C['grn2'],bg=C['card']).pack(anchor='w')
                tk.Frame(row,bg=C['brd2'],height=1).pack(fill='x')
                for ch in [row]+row.winfo_children(): ch.bind('<Button-1>',lambda ev,ee=e:show(ee))
                row.bind('<Enter>',lambda ev,r=row:r.config(bg=C['hov']))
                row.bind('<Leave>',lambda ev,r=row:r.config(bg=C['card']))
        se.bind('<KeyRelease>',lambda e:refresh(sv.get())); refresh()

    def _build_v_sessions(self,parent):
        sessions=load_json(TASKS_FILE,[])
        top=tk.Frame(parent,bg=C['bg']); top.pack(fill='x',padx=12,pady=10)
        mk_lbl(top,f'📊 Sessiya Statistikasi ({len(sessions)} ta)',12,C['acc3'],bold=True).pack(side='left')
        total_h=sum(s.get('actual_h') or s.get('planned_h',0) for s in sessions)
        total_d=len(set(s.get('date','') for s in sessions))
        all_t=sum(len(s.get('tasks',[])) for s in sessions)
        done_t=sum(sum(1 for t in s.get('tasks',[]) if t.get('done')) for s in sessions)
        sf=tk.Frame(parent,bg=C['card'],padx=16,pady=12); sf.pack(fill='x',padx=12,pady=(0,8))
        for lbl,val,col in [('⏱ Jami vaqt',f'{total_h:.1f}h',C['acc3']),('📅 Kunlar',f'{total_d}',C['grn2']),
                             ('📋 Vazifalar',f'{all_t}',C['yel2']),('✅ Bajarilgan',f'{done_t}({int(done_t/max(all_t,1)*100)}%)',C['grn3'])]:
            cf=tk.Frame(sf,bg=C['card']); cf.pack(side='left',expand=True)
            mk_lbl(cf,val,16,col,bold=True,bg=C['card']).pack(); mk_lbl(cf,lbl,8,C['sub'],bg=C['card']).pack()
        chart_cv=tk.Canvas(parent,bg=C['card'],height=165,highlightthickness=0); chart_cv.pack(fill='x',padx=12,pady=4)
        today2=ddate.today(); day_map={}
        for s in sessions:
            try:
                d=ddate.fromisoformat(s.get('date','')); v=s.get('actual_h') or s.get('planned_h',0)
                day_map[d]=day_map.get(d,0)+v
            except: pass
        cdata=[((today2-timedelta(days=i)).strftime('%d'),day_map.get(today2-timedelta(days=i),0)) for i in range(13,-1,-1)]
        chart_cv.bind('<Configure>',lambda e:canvas_bar(chart_cv,cdata,e.width,165,'Ish soatlari (14 kun)',C['acc']))
        parent.after(300,lambda:canvas_bar(chart_cv,cdata,chart_cv.winfo_width() or 800,165,'Ish soatlari',C['acc']))
        lf=tk.Frame(parent,bg=C['card']); lf.pack(fill='both',expand=True,padx=12,pady=4)
        cv=tk.Canvas(lf,bg=C['card'],highlightthickness=0); sb=tk.Scrollbar(lf,orient='vertical',command=cv.yview)
        cv.configure(yscrollcommand=sb.set); sb.pack(side='right',fill='y'); cv.pack(fill='both',expand=True)
        inn=tk.Frame(cv,bg=C['card']); cv.create_window((0,0),window=inn,anchor='nw')
        inn.bind('<Configure>',lambda e:cv.configure(scrollregion=cv.bbox('all')))
        for s in reversed(sessions[-40:]):
            row=tk.Frame(inn,bg=C['card'],padx=10,pady=4); row.pack(fill='x')
            act=s.get('actual_h') or s.get('planned_h',0); pln=s.get('planned_h',0)
            eff=int(act/pln*100) if pln>0 else 0
            mk_lbl(row,f"📅 {s.get('date','')}  ⏱ {act:.2f}h (Reja:{pln:.1f}h ·{eff}%)  📋{s.get('summary','')}  {s.get('goal','')[:20]}",
                   8,C['sub'],bg=C['card']).pack(anchor='w')
            tk.Frame(row,bg=C['brd'],height=1).pack(fill='x')

    def _build_v_apps(self,parent):
        dates=self.at.get_available_dates(); today_iso=ddate.today().isoformat()
        top=tk.Frame(parent,bg=C['bg']); top.pack(fill='x',padx=12,pady=10)
        mk_lbl(top,'📱 App Tahlili (90 kunlik tarix)',12,C['acc3'],bold=True).pack(side='left')
        ctrl=tk.Frame(parent,bg=C['bg']); ctrl.pack(fill='x',padx=12,pady=(0,8))
        mk_lbl(ctrl,'Sana:',9,C['sub']).pack(side='left')
        date_var=tk.StringVar(value=today_iso if today_iso in dates else (dates[0] if dates else today_iso))
        if dates:
            combo=ttk.Combobox(ctrl,textvariable=date_var,values=dates,state='readonly',font=('Segoe UI',9),width=14)
            combo.pack(side='left',padx=6)
        chart_cv=tk.Canvas(parent,bg=C['card'],height=150,highlightthickness=0); chart_cv.pack(fill='x',padx=12,pady=(0,6))
        lf=tk.Frame(parent,bg=C['bg']); lf.pack(fill='both',expand=True,padx=12)
        scroll_f=tk.Frame(lf,bg=C['bg']); scroll_f.pack(fill='both',expand=True)
        cv=tk.Canvas(scroll_f,bg=C['bg'],highlightthickness=0); sb=tk.Scrollbar(scroll_f,orient='vertical',command=cv.yview)
        cv.configure(yscrollcommand=sb.set); sb.pack(side='right',fill='y'); cv.pack(fill='both',expand=True)
        list_in=tk.Frame(cv,bg=C['bg']); cv.create_window((0,0),window=list_in,anchor='nw')
        list_in.bind('<Configure>',lambda e:cv.configure(scrollregion=cv.bbox('all')))
        def refresh(dt=None):
            dt=dt or date_var.get(); data=self.at.get_date(dt)
            for w in list_in.winfo_children(): w.destroy()
            if not data: mk_lbl(list_in,'Bu kun uchun ma\'lumot yo\'q',9,C['sub']).pack(pady=16); return
            total=sum(s for _,s in data); top10=data[:10]
            canvas_bar(chart_cv,[(os.path.splitext(a)[0][:8],s/3600) for a,s in top10],
                       chart_cv.winfo_width() or 700,150,f'{dt} — App',C['acc'])
            for i,(app,secs) in enumerate(data[:30]):
                pct=secs/total*100 if total>0 else 0
                row=tk.Frame(list_in,bg=C['card'],padx=8,pady=5); row.pack(fill='x',pady=1)
                col=[C['acc3'],C['grn2'],C['yel2'],C['red3'],C['vio2']][i%5]
                mk_lbl(row,f'{i+1:2d}.',8,C['sub'],bg=C['card']).pack(side='left',padx=(0,4))
                mk_lbl(row,os.path.splitext(app)[0][:28],9,C['txt'],bg=C['card']).pack(side='left',fill='x',expand=True)
                mk_lbl(row,fmt_dur(secs),9,col,bold=True,bg=C['card']).pack(side='left',padx=6)
                mk_lbl(row,f'{pct:.0f}%',8,C['sub'],bg=C['card']).pack(side='left',padx=4)
        if dates: combo.bind('<<ComboboxSelected>>',lambda e:refresh(date_var.get()))
        parent.after(500,refresh)

    def _build_v_power(self,parent):
        mk_lbl(parent,'🔌 Kompyuter Quvvat Jurnali',12,C['acc3'],bold=True).pack(anchor='w',padx=12,pady=(10,4))
        today_iso=ddate.today().isoformat(); events=self.pl.get_recent(200)
        today_boots=[e for e in events if e['event']=='boot' and e['time'][:10]==today_iso]
        sf=tk.Frame(parent,bg=C['card'],padx=16,pady=10); sf.pack(fill='x',padx=12,pady=(0,8))
        for lbl,val,col in [('📅 Bugungi yoqish',f'{len(today_boots)} marta',C['grn2']),
                             ('⏱ Joriy sessiya',fmt_dur(time.time()-self.pl._boot_time),C['acc3']),
                             ('📊 Jami',f'{sum(1 for e in events if e["event"]=="boot")} ta',C['yel2'])]:
            cf=tk.Frame(sf,bg=C['card']); cf.pack(side='left',expand=True)
            mk_lbl(cf,val,15,col,bold=True,bg=C['card']).pack(); mk_lbl(cf,lbl,8,C['sub'],bg=C['card']).pack()
        pw_cv=tk.Canvas(parent,bg=C['card'],height=130,highlightthickness=0); pw_cv.pack(fill='x',padx=12,pady=4)
        day_up={};
        for e in events:
            if e['event']=='boot' and 'uptime_s' in e: d=e['time'][:10]; day_up[d]=day_up.get(d,0)+e['uptime_s']
        today2=ddate.today()
        pw_data=[((today2-timedelta(days=i)).strftime('%d'),day_up.get((today2-timedelta(days=i)).isoformat(),0)/3600) for i in range(13,-1,-1)]
        pw_cv.bind('<Configure>',lambda e:canvas_bar(pw_cv,pw_data,e.width,130,'Kunlik vaqt (soat)',C['vio2']))
        parent.after(400,lambda:canvas_bar(pw_cv,pw_data,pw_cv.winfo_width() or 700,130,'Kunlik vaqt',C['vio2']))
        lf=tk.Frame(parent,bg=C['bg']); lf.pack(fill='both',expand=True,padx=12,pady=4)
        cv=tk.Canvas(lf,bg=C['bg'],highlightthickness=0); sb=tk.Scrollbar(lf,orient='vertical',command=cv.yview)
        cv.configure(yscrollcommand=sb.set); sb.pack(side='right',fill='y'); cv.pack(fill='both',expand=True)
        inn=tk.Frame(cv,bg=C['bg']); cv.create_window((0,0),window=inn,anchor='nw')
        inn.bind('<Configure>',lambda e:cv.configure(scrollregion=cv.bbox('all')))
        for e in reversed(events[-60:]):
            row=tk.Frame(inn,bg=C['card'],padx=10,pady=4); row.pack(fill='x',pady=1)
            icon='🟢' if e['event']=='boot' else '🔴'; col=C['grn2'] if e['event']=='boot' else C['red3']
            up=e.get('uptime',''); upt=f' · {up}' if up else ''
            mk_lbl(row,f"{icon} {e['time']} — {'YOQILDI' if e['event']=='boot' else 'O\'CHIRILDI'}{upt}",9,col,bg=C['card']).pack(anchor='w')
            tk.Frame(row,bg=C['brd'],height=1).pack(fill='x')

    def _build_v_notes(self,parent):
        CATS=['💼 Ish','🎯 Maqsadlar','💡 G\'oyalar','🏥 Salomatlik','💰 Moliya','👥 Munosabatlar','📝 Boshqa']
        top=tk.Frame(parent,bg=C['bg']); top.pack(fill='x',padx=12,pady=10)
        mk_lbl(top,'📝 Shaxsiy Eslatmalar (Shifrlangan)',12,C['acc3'],bold=True).pack(side='left')
        nf=tk.Frame(parent,bg=C['bg']); nf.pack(fill='both',expand=True,padx=12,pady=4)
        def refresh():
            for w in nf.winfo_children():
                try: w.destroy()
                except: pass
            notes=self.vm.get_notes()
            if not notes:
                c2=tk.Frame(nf,bg=C['card'],padx=20,pady=30); c2.pack(expand=True)
                mk_lbl(c2,'🔒 Shifrlangan xavfsiz joy',14,C['sub'],bg=C['card']).pack()
                mk_btn(c2,'+ Eslatma qo\'sh',lambda:self._note_ed(None,None,refresh,CATS),C['acc'],fs=11,px=20,py=10).pack(pady=8)
                return
            cv2=tk.Canvas(nf,bg=C['bg'],highlightthickness=0); sb2=tk.Scrollbar(nf,orient='vertical',command=cv2.yview)
            cv2.configure(yscrollcommand=sb2.set); sb2.pack(side='right',fill='y'); cv2.pack(fill='both',expand=True)
            gr=tk.Frame(cv2,bg=C['bg']); cv2.create_window((0,0),window=gr,anchor='nw')
            gr.bind('<Configure>',lambda e:cv2.configure(scrollregion=cv2.bbox('all')))
            for i,note in enumerate(notes):
                r2,c2_idx=divmod(i,3)
                card=tk.Frame(gr,bg=C['card'],padx=12,pady=10); card.grid(row=r2,column=c2_idx,padx=4,pady=4,sticky='nsew')
                gr.columnconfigure(c2_idx,weight=1)
                cat_col={'💼':C['blu'],'🎯':C['acc3'],'💡':C['yel2'],'🏥':C['grn2'],'💰':C['yel3'],'👥':C['acc2'],'📝':C['sub']}.get(note['category'][:2],C['sub'])
                mk_lbl(card,note['category'],8,cat_col,bold=True,bg=C['card']).pack(anchor='w')
                mk_lbl(card,note['title'],10,C['txt'],bold=True,bg=C['card']).pack(anchor='w')
                mk_lbl(card,note['content'][:75].replace('\n',' ')+'...',8,C['sub'],bg=C['card']).pack(anchor='w',pady=2)
                mk_lbl(card,note['updated'][:10],7,C['brd2'],bg=C['card']).pack(anchor='e')
                br=tk.Frame(card,bg=C['card']); br.pack(fill='x',pady=(4,0)); ii=i
                mk_btn(br,'✏',lambda ii=ii,n=note:self._note_ed(ii,n,refresh,CATS),C['inp'],fg=C['acc3'],fs=7,px=6,py=3).pack(side='left',padx=2)
                mk_btn(br,'🗑',lambda ii=ii:(self.vm.delete_note(ii),refresh()),C['inp'],fg=C['red3'],fs=7,px=6,py=3).pack(side='right',padx=2)
            mk_btn(top,'+ Yangi',lambda:self._note_ed(None,None,refresh,CATS),C['acc'],fs=9,px=12,py=5).pack(side='right')
        refresh()

    def _note_ed(self,idx,note_obj,on_save,cats):
        dlg=tk.Toplevel(); dlg.title('Eslatma'); dlg.configure(bg=C['bg']); dlg.attributes('-topmost',True)
        dlg.resizable(True,True); dlg.geometry('600x480')
        mk_lbl(dlg,'✏ Eslatma',13,C['acc3'],bold=True).pack(pady=(14,8))
        tf=tk.Frame(dlg,bg=C['bg']); tf.pack(fill='x',padx=16,pady=3)
        mk_lbl(tf,'Sarlavha:',9,C['sub']).pack(anchor='w')
        tv=tk.StringVar(value=note_obj['title'] if note_obj else '')
        brd,_=mk_entry(tf,tv,width=50,ipy=8); brd.pack(fill='x')
        cf=tk.Frame(dlg,bg=C['bg']); cf.pack(fill='x',padx=16,pady=4)
        mk_lbl(cf,'Kategoriya:',9,C['sub']).pack(anchor='w')
        cv2=tk.StringVar(value=note_obj['category'] if note_obj else cats[0])
        ttk.Combobox(cf,textvariable=cv2,values=cats,state='readonly',font=('Segoe UI',10),width=30).pack(anchor='w',pady=2)
        cf2=tk.Frame(dlg,bg=C['bg']); cf2.pack(fill='both',expand=True,padx=16,pady=4)
        mk_lbl(cf2,'Mazmun:',9,C['sub']).pack(anchor='w')
        brd2=tk.Frame(cf2,bg=C['brd2'],padx=1,pady=1); brd2.pack(fill='both',expand=True)
        ta=scrolledtext.ScrolledText(brd2,font=('Segoe UI',10),bg=C['inp'],fg=C['txt'],insertbackground=C['acc3'],wrap='word',relief='flat')
        ta.pack(fill='both',expand=True,padx=2,pady=2)
        if note_obj: ta.insert('end',note_obj['content'])
        ta.focus_set()
        def do_save():
            t=tv.get().strip(); ct=cv2.get(); cont=ta.get('1.0','end-1c').strip()
            if not t or not cont: messagebox.showwarning('Bo\'sh','Sarlavha va mazmun kiriting!',parent=dlg); return
            if idx is None: self.vm.add_note(t,ct,cont)
            else: self.vm.update_note(idx,t,ct,cont)
            dlg.destroy()
            if on_save: on_save()
        br=tk.Frame(dlg,bg=C['bg']); br.pack(fill='x',padx=16,pady=8)
        mk_btn(br,'💾 Saqlash',do_save,C['grn'],fs=11,px=20,py=9).pack(side='right',padx=4)
        mk_btn(br,'Bekor',dlg.destroy,C['inp'],fg=C['dim'],fs=10,px=14,py=9).pack(side='right',padx=4)
        dlg.grab_set(); dlg.protocol('WM_DELETE_WINDOW',dlg.destroy)

    def _build_v_ai(self,parent):
        self._ai_hist=[]
        ai_sys='Sen SL tizimining AI yordamchisisiz. O\'zbek tilida qisqa, amaliy javoblar ber.'
        top=tk.Frame(parent,bg=C['bg']); top.pack(fill='x',padx=12,pady=(10,4))
        mk_lbl(top,'🤖 Claude AI Yordamchi',12,C['acc3'],bold=True).pack(side='left')
        def open_settings():
            sd=tk.Toplevel(); sd.title('AI Sozlamalar'); sd.configure(bg=C['bg']); sd.attributes('-topmost',True)
            sd.resizable(False,False); sd.geometry('480x260')
            mk_lbl(sd,'⚙ AI API Sozlamalar',13,C['acc3'],bold=True).pack(pady=(14,6))
            mv=tk.StringVar(value=self.cfg.get('ai_model',''))
            mk_lbl(sd,'Model:',8,C['sub']).pack(anchor='w',padx=20)
            brd,_=mk_entry(sd,mv,width=42,ipy=6); brd.pack(padx=20,fill='x')
            kv=tk.StringVar(value=self.cfg.get('ai_api_key',''))
            mk_lbl(sd,'API kalit:',8,C['sub']).pack(anchor='w',padx=20,pady=(8,0))
            brd2,ke=mk_entry(sd,kv,width=42,ipy=6,show='●'); brd2.pack(padx=20,fill='x')
            def save_ai():
                self.cfg.set('ai_model',mv.get().strip()); self.cfg.set('ai_api_key',kv.get().strip()); sd.destroy()
            mk_btn(sd,'Saqlash',save_ai,C['grn'],fs=11,px=24,py=9).pack(pady=12)
            sd.grab_set(); sd.protocol('WM_DELETE_WINDOW',sd.destroy)
        mk_btn(top,'⚙ Sozlamalar',open_settings,C['inp'],fg=C['acc3'],fs=8,px=10,py=5).pack(side='right')
        chat_brd=tk.Frame(parent,bg=C['brd2'],padx=1,pady=1); chat_brd.pack(fill='both',expand=True,padx=12,pady=4)
        self._aichat=scrolledtext.ScrolledText(chat_brd,font=('Segoe UI',10),bg=C['inp'],fg=C['txt'],insertbackground=C['acc3'],wrap='word',relief='flat',state='disabled')
        self._aichat.pack(fill='both',expand=True,padx=2,pady=2)
        self._aichat.tag_config('user',foreground=C['acc3'],font=('Segoe UI',10,'bold'))
        self._aichat.tag_config('ai',foreground=C['txt']); self._aichat.tag_config('sys',foreground=C['sub'],font=('Segoe UI',8,'italic'))
        qp=tk.Frame(parent,bg=C['bg']); qp.pack(fill='x',padx=12,pady=(4,0))
        for q in ['Bugungi reja','Focus usullari','Maqsad tahlili','Motivatsiya']:
            mk_btn(qp,q,lambda qq=q:self._ai_send(qq,ai_sys),C['inp'],fg=C['acc3'],fs=7,px=7,py=4).pack(side='left',padx=2)
        inp=tk.Frame(parent,bg=C['bg']); inp.pack(fill='x',padx=12,pady=8)
        self._aiv=tk.StringVar(); brd,ai_ent=mk_entry(inp,self._aiv,width=55,ipy=9); brd.pack(side='left',fill='x',expand=True)
        ai_ent.bind('<Return>',lambda e:self._ai_send(self._aiv.get(),ai_sys))
        self._aisb=mk_btn(inp,'  ↑ Yuborish  ',lambda:self._ai_send(self._aiv.get(),ai_sys),C['acc'],fs=10,px=14,py=9)
        self._aisb.pack(side='left',padx=(8,0))
        self._ai_append('🤖 Salom! SL AI. Sozlamalar → API kalit kiriting.\n','sys')

    def _ai_append(self,text,tag='ai'):
        self._aichat.config(state='normal'); self._aichat.insert('end',text+'\n',tag)
        self._aichat.config(state='disabled'); self._aichat.see('end')

    def _ai_send(self,text,sys_p):
        text=text.strip()
        if not text: return
        self._aiv.set(''); self._ai_append(f'\n👤 Sen:\n{text}\n','user')
        self._ai_hist.append({'role':'user','content':text})
        self._aisb.config(state='disabled',text='⏳...')
        self._ai_append('🤖 yozmoqda...\n','sys')
        api=self.cfg.get('ai_api_key',''); model=self.cfg.get('ai_model','claude-haiku-4-5-20251001')
        hist=self._ai_hist.copy()
        def run():
            resp=ai_call(api,hist,system=sys_p,model=model)
            def upd():
                self._aichat.config(state='normal')
                idx=self._aichat.index('end-2l'); self._aichat.delete(idx,'end')
                self._aichat.config(state='disabled')
                self._ai_append(f'\n🤖 AI:\n{resp}\n','ai')
                self._ai_hist.append({'role':'assistant','content':resp})
                self._aisb.config(state='normal',text='  ↑ Yuborish  ')
            self.root.after(0,upd)
        threading.Thread(target=run,daemon=True).start()

    def _build_v_plan(self,parent):
        # The Strategic Planning Visual Tool lives here
        self._plan_tool=StrategicPlanTool(
            parent, self.vm,
            lambda:self.cfg.get('ai_api_key',''),
            lambda:self.cfg.get('ai_model','claude-haiku-4-5-20251001')
        )

    # ── Done Screen ───────────────────────────────────────────
    def _screen_done(self):
        self.running=False; log('Session done'); self.tm.end()
        sessions=load_json(TASKS_FILE,[]); last_s=sessions[-1] if sessions else {}
        actual_h=last_s.get('actual_h',self.s_hours); actual_s=actual_h*3600
        planned_h=last_s.get('planned_h',self.s_hours); eff=int(actual_h/planned_h*100) if planned_h>0 else 0
        lt=last_s.get('tasks',[]); done_n=sum(1 for t in lt if t.get('done')); total_n=len(lt)
        self._clear(); self._fs(); self.root.configure(bg=C['bg'])
        self.root.protocol('WM_DELETE_WINDOW',lambda:None); self.root.bind('<Alt-F4>',lambda e:'break')
        c=tk.Frame(self.root,bg=C['bg']); c.place(relx=.5,rely=.5,anchor='center')
        tk.Label(c,text='🏆',font=('Segoe UI Emoji',72),bg=C['bg'],fg=C['yel3']).pack()
        mk_lbl(c,'SESSIYA TUGADI',30,C['acc'],bold=True).pack()
        mk_lbl(c,'Yaxshi ish qilding. Selfish. 💎',12,C['acc3']).pack(pady=4)
        sf=tk.Frame(c,bg=C['card'],padx=28,pady=16); sf.pack(pady=14)
        for lbl,val,col in [
            ('⏱ Haqiqiy vaqt:',fmt_dur(actual_s),C['acc3']),('📋 Reja:',f'{planned_h:.1f}h',C['dim']),
            ('📊 Samaradorlik:',f'{eff}%',C['grn2'] if eff>=80 else C['yel2']),
            ('🎯 Maqsad:',self.s_goal or '—',C['grn2']),('📋 Vazifalar:',f'{done_n}/{total_n}',C['grn3'] if done_n==total_n else C['yel2']),
        ]:
            r=tk.Frame(sf,bg=C['card']); r.pack(pady=3)
            mk_lbl(r,lbl,11,C['sub'],bg=C['card']).pack(side='left',padx=8)
            mk_lbl(r,val,11,col,bold=True,bg=C['card']).pack(side='left',padx=8)
        tk.Frame(c,bg=C['brd2'],height=1,width=540).pack(pady=16)
        def open_j():
            dlg=tk.Toplevel(self.root); dlg.title('Journal'); dlg.configure(bg=C['bg']); dlg.attributes('-topmost',True)
            dlg.resizable(True,True); dlg.geometry('560x440')
            mk_lbl(dlg,f'📔 Journal · {datetime.now().strftime("%d %B %Y")}',12,C['acc3'],bold=True).pack(pady=(14,8))
            brd=tk.Frame(dlg,bg=C['brd2'],padx=1,pady=1); brd.pack(fill='both',expand=True,padx=14,pady=4)
            ta2=scrolledtext.ScrolledText(brd,font=('Segoe UI',10),bg=C['inp'],fg=C['txt'],insertbackground=C['acc3'],wrap='word',relief='flat')
            ta2.pack(fill='both',expand=True,padx=2,pady=2); ta2.focus_set()
            def save_j():
                content=ta2.get('1.0','end-1c').strip()
                if not content: messagebox.showwarning('Bo\'sh','Journal yozing!',parent=dlg); return
                self.jm.add(content,goal=self.s_goal,actual_h=actual_h); j_btn.config(text='✅ Saqlandi',bg=C['grn2'],state='disabled'); dlg.destroy()
            mk_btn(dlg,'💾 SAQLASH',save_j,C['grn'],fs=11,px=24,py=10).pack(pady=8)
            dlg.grab_set(); dlg.protocol('WM_DELETE_WINDOW',dlg.destroy)
        j_btn=mk_btn(c,'📔 Journal yozish',open_j,C['acc2'],fs=12,px=22,py=11); j_btn.pack()
        mk_lbl(c,'(Kuchli odatlar shu yerda quriladi)',8,C['sub']).pack(pady=2)
        tk.Frame(c,bg=C['brd2'],height=1,width=540).pack(pady=14)
        mk_lbl(c,'Kompyuterni o\'chirish yoki davom etish?',14,bold=True).pack()
        btns=tk.Frame(c,bg=C['bg']); btns.pack(pady=16)
        mk_btn(btns,'🔴  Kompyuterni o\'chir',self._do_end,C['red'],fs=12,px=26,py=13).pack(side='left',padx=10)
        ext=tk.Frame(c,bg=C['bg']); ext.pack()
        mk_lbl(ext,'Yoki davom:',10,C['sub']).pack(side='left',padx=6)
        self._ext_v=tk.StringVar(value='30')
        brd3=tk.Frame(ext,bg=C['brd2'],padx=1,pady=1); brd3.pack(side='left')
        tk.Entry(brd3,textvariable=self._ext_v,font=('Segoe UI Mono',13),bg=C['inp'],fg=C['acc3'],relief='flat',width=5,justify='center').pack(ipady=6)
        mk_lbl(ext,'daqiqa',10,C['sub']).pack(side='left',padx=6)
        mk_btn(ext,'Davom →',self._extend,C['acc'],fs=11,px=16,py=8).pack(side='left',padx=8)

    def _do_end(self):
        self.running=False; unblock_sites(); self._clear(); self._fs(); self.root.configure(bg=C['bg'])
        c=tk.Frame(self.root,bg=C['bg']); c.place(relx=.5,rely=.5,anchor='center')
        tk.Label(c,text='🔒',font=('Segoe UI Emoji',64),bg=C['bg'],fg=C['acc']).pack()
        mk_lbl(c,'Yaxshi ish. Selfish.',24,bold=True).pack(pady=6)
        mk_lbl(c,'Kompyuter 5 soniyada o\'chirilmoqda...',13,C['sub']).pack()
        self.root.update(); time.sleep(2); do_shutdown(); self.root.after(8000,self.root.destroy)

    def _extend(self):
        try: extra=int(self._ext_v.get()); assert extra>0
        except: messagebox.showerror('Xato','To\'g\'ri daqiqa!',parent=self.root); return
        self.s_hours=extra/60; self.total_s=extra*60; self.end_ts=time.time()+extra*60; self.running=True
        self.tm.new(goal=self.s_goal,hours=self.s_hours)
        self._dashboard(); threading.Thread(target=self._timer_loop,daemon=True).start()

    # ── Uninstall ─────────────────────────────────────────────
    def _uninstall_dlg(self,parent_win):
        dlg=tk.Toplevel(); dlg.title('🗑 Uninstall SL'); dlg.configure(bg=C['bg'])
        dlg.attributes('-topmost',True); dlg.resizable(False,False); dlg.geometry('520x440')
        hf=tk.Frame(dlg,bg=C['red'],pady=10); hf.pack(fill='x')
        mk_lbl(hf,'🗑  SL Selfish — Uninstall',14,C['wht'],bold=True,bg=C['red']).pack(padx=16)
        mk_lbl(dlg,'Quyidagi narsalarni o\'chirish uchun belgilang:',10,C['sub']).pack(anchor='w',padx=16,pady=(14,6))
        opts=tk.Frame(dlg,bg=C['bg']); opts.pack(fill='x',padx=16)
        del_startup=tk.BooleanVar(value=True)
        del_data=tk.BooleanVar(value=False)
        del_config=tk.BooleanVar(value=False)
        for text,var,desc in [
            ('🚀  Startup (Startup Folder / TaskSched / Registry)',del_startup,'Avtomatik ishga tushish o\'chiriladi'),
            ('📂  Barcha ma\'lumotlar (%APPDATA%\\SL_Selfish\\)',del_data,'Journal, sessiyalar, vault, applog — hammasi'),
            ('⚙️   Config fayl (sl_config.json)',del_config,'Parol, sozlamalar'),
        ]:
            fr=tk.Frame(opts,bg=C['card'],padx=12,pady=10); fr.pack(fill='x',pady=3)
            tk.Checkbutton(fr,text=text,variable=var,font=('Segoe UI',10,'bold'),
                           bg=C['card'],fg=C['txt'],activebackground=C['card'],selectcolor=C['inp'],
                           relief='flat',cursor='hand2').pack(anchor='w')
            mk_lbl(fr,f'  {desc}',8,C['sub'],bg=C['card']).pack(anchor='w')
        tk.Frame(dlg,bg=C['brd2'],height=1).pack(fill='x',padx=16,pady=12)
        mk_lbl(dlg,'⚠  EXE fayli o\'chirilmaydi (qo\'lda o\'chiring)',9,C['yel2']).pack(anchor='w',padx=16)
        def do_uninstall():
            if not messagebox.askyesno('Tasdiqlash','Rostdan ham o\'chirmoqchimisiz?',parent=dlg): return
            results=[]
            if del_startup.get():
                unregister_startup(); results.append('✅  Startup o\'chirildi')
            if del_data.get():
                try:
                    import shutil; shutil.rmtree(DATA_DIR,ignore_errors=True)
                    results.append('✅  Data papka o\'chirildi')
                except Exception as e: results.append(f'❌  Data: {e}')
            if del_config.get():
                try:
                    if os.path.exists(CFG_FILE): os.remove(CFG_FILE)
                    results.append('✅  Config o\'chirildi')
                except Exception as e: results.append(f'❌  Config: {e}')
            log(f'Uninstall: {results}')
            messagebox.showinfo('Natija','\n'.join(results)+'\n\nSL.exe ni qo\'lda o\'chiring.',parent=dlg)
            dlg.destroy()
            try: parent_win.destroy()
            except: pass
        bf=tk.Frame(dlg,bg=C['bg']); bf.pack(fill='x',padx=16,pady=10)
        mk_btn(bf,'🗑  O\'CHIRISH',do_uninstall,C['red'],fs=12,px=24,py=10).pack(side='left',padx=4)
        mk_btn(bf,'Bekor',dlg.destroy,C['inp'],fg=C['dim'],fs=10,px=14,py=10).pack(side='right',padx=4)
        dlg.grab_set(); dlg.protocol('WM_DELETE_WINDOW',dlg.destroy)

# ══════════════════════════════════════════════════════════════
#  ENTRY
# ══════════════════════════════════════════════════════════════
if __name__=='__main__':
    req_admin()
    SL()
