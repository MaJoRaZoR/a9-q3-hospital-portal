import subprocess,json,time,urllib.request
from pathlib import Path
def run(args,check=True,capture=False):
 print('+',' '.join(args),flush=True)
 return subprocess.run(args,check=check,stdout=subprocess.PIPE if capture else None,text=True,encoding='utf-8',errors='replace')
def docker(*args,**kw):return run(['docker',*args],**kw)
nodes=json.loads(run(['kubectl','get','nodes','-o','json'],capture=True).stdout)
node=nodes['items'][0]['metadata']['name']
ip=next(a['address'] for a in nodes['items'][0]['status']['addresses'] if a['type']=='InternalIP')
info=json.loads(docker('inspect',node,capture=True).stdout)[0]
networks=[name for name,value in info['NetworkSettings']['Networks'].items() if value['IPAddress']==ip]
assert len(networks)==1,networks
network=networks[0]
print('NodePort host bridge network:',network,'node address:',ip,flush=True)
conf='\n'.join('server { listen '+str(port)+'; location / { proxy_pass http://'+ip+':'+str(port)+'; } }' for port in [30081,30082,30083])
Path('nodeport-bridge.conf').write_text(conf,encoding='utf-8')
if docker('inspect','a9-nodeport-bridge',check=False,capture=True).returncode:
 docker('run','-d','--name','a9-nodeport-bridge','--network',network,'-p','127.0.0.1:30081:30081','-p','127.0.0.1:30082:30082','-p','127.0.0.1:30083:30083','nginx:stable-alpine')
docker('cp','nodeport-bridge.conf','a9-nodeport-bridge:/etc/nginx/conf.d/default.conf')
docker('exec','a9-nodeport-bridge','nginx','-s','reload')
for app,port,local in [('university',30081,8091),('food',30082,8092),('hospital',30083,8093)]:
 service=json.loads(run(['kubectl','-n','devops-assignment','get','svc',app,'-o','json'],capture=True).stdout)
 deployment=app+'-'+service['spec']['selector']['slot'] if app=='food' else app
 dep=json.loads(run(['kubectl','-n','devops-assignment','get','deployment',deployment,'-o','json'],capture=True).stdout)
 image=dep['spec']['template']['spec']['containers'][0]['image']
 name='a9-'+app+'-local'
 if docker('inspect',name,check=False,capture=True).returncode:
  docker('run','-d','--name',name,'-p',f'127.0.0.1:{local}:80',image)
 for attempt in range(30):
  try:
   for p in [port,local]:
    with urllib.request.urlopen(f'http://127.0.0.1:{p}/release.txt',timeout=3) as r:
     identity=r.read().decode().strip();assert r.status==200
     print('HTTP 200:',p,identity,flush=True)
   break
  except Exception:
   if attempt==29:raise
   time.sleep(1)
docker('ps','--filter','name=a9-')
