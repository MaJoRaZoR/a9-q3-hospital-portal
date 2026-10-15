import os,sys,json,time,subprocess,urllib.request
from pathlib import Path
from string import Template
APP=os.environ['APP']; IMAGE=os.environ['IMAGE']; NS='devops-assignment'
BG=APP=='food'
def run(args,check=True,capture=False):
    print('+',' '.join(args),flush=True)
    return subprocess.run(args,check=check,text=True,encoding='utf-8',errors='replace',stdout=subprocess.PIPE if capture else None)
def k(*args,**kw):return run(['kubectl','-n',NS,*args],**kw)
def obj(kind,name):
    p=k('get',kind,name,'-o','json',capture=True,check=False)
    return json.loads(p.stdout) if p.returncode==0 else None
def probe(service,expected):
    last=None
    for attempt in range(5):
        p=subprocess.Popen(['kubectl','-n',NS,'port-forward','service/'+service,'18080:80'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            for _ in range(15):
                try:
                    def get(path):
                        with urllib.request.urlopen('http://127.0.0.1:18080/'+path,timeout=3) as r:
                            assert r.status==200
                            return r.read().decode()
                    assert get('healthz').strip()=='ok'
                    assert '<html' in get('')
                    assert get('release.txt').strip()==expected
                    print('HTTP 200 AND RELEASE VERIFIED:',service,expected,flush=True)
                    return
                except Exception as e:last=e;time.sleep(1)
        finally:p.terminate();p.wait(timeout=10)
    raise RuntimeError('Service validation failed: '+str(last))
run(['kubectl','create','namespace',NS],check=False)
current=obj('service',APP) if BG else obj('deployment',APP)
active=current['spec']['selector']['slot'] if BG and current else None
slot=('green' if active=='blue' else 'blue') if BG else None
previous=None; switched=False
if current:
    name=APP+'-'+active if BG else APP
    k('rollout','status','deployment/'+name,'--timeout=180s')
    previous=obj('deployment',name)['spec']['template']['spec']['containers'][0]['image']
    probe(APP,previous)
os.environ['HEALTH_PATH']='/healthz'
if BG:os.environ['SLOT']=slot
def apply(file):
    text=Template(Path(file).read_text(encoding='utf-8')).substitute(os.environ)
    Path('rendered.yaml').write_text(text,encoding='utf-8')
    k('apply','-f','rendered.yaml')
name=APP+'-'+slot if BG else APP
try:
    apply('deployment.yaml')
    k('rollout','status','deployment/'+name,'--timeout=180s')
    if BG:
        probe(name+'-preview',IMAGE)
        if active:
            switched=True
            k('patch','service',APP,'--type=merge','-p',json.dumps({'spec':{'selector':{'app':APP,'slot':slot}}}))
        else:apply('service.yaml')
    probe(APP,IMAGE)
    k('get','deployments')
    k('get','pods','-l','app='+APP,'-o','wide')
    k('get','service',APP)
    print('RELEASE VERIFIED:',IMAGE,flush=True)
except Exception as err:
    print('FAILED ROLLOUT:',err,flush=True)
    k('describe','deployment',name,check=False)
    k('get','pods','-l','app='+APP,'-o','wide',check=False)
    if previous:
        if BG:
            if switched:k('patch','service',APP,'--type=merge','-p',json.dumps({'spec':{'selector':{'app':APP,'slot':active}}}))
            k('scale','deployment/'+name,'--replicas=0')
        else:
            k('rollout','undo','deployment/'+APP)
            k('rollout','status','deployment/'+APP,'--timeout=180s')
        probe(APP,previous)
        k('get','pods','-l','app='+APP,'-o','wide')
        print('AUTOMATIC ROLLBACK VERIFIED:',previous,flush=True)
    else:print('No previous stable release exists',flush=True)
    sys.exit(1)
