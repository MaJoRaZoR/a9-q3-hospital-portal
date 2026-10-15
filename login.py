import os,subprocess
subprocess.run(['docker','login','-u',os.environ['DH_USER'],'--password-stdin'],input=os.environ['DH_TOKEN'],text=True,check=True)
