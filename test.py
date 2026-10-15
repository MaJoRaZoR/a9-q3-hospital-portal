import os,time,subprocess,urllib.request
image=os.environ['IMAGE']
container=subprocess.check_output(['docker','run','-d','-p','127.0.0.1::80',image],text=True).strip()
try:
    port=subprocess.check_output(['docker','port',container,'80/tcp'],text=True).strip().rsplit(':',1)[1]
    for attempt in range(30):
        try:
            def get(path):
                with urllib.request.urlopen('http://127.0.0.1:'+port+'/'+path,timeout=3) as r:
                    assert r.status==200
                    return r.read().decode()
            assert get('healthz').strip()=='ok'
            assert '<h1>' in get('') and '<section>' in get('')
            assert get('release.txt').strip()==image
            print('CONTAINER HTTP AND CONTENT TESTS PASSED:',image)
            break
        except Exception:
            if attempt==29:raise
            time.sleep(1)
finally:subprocess.run(['docker','rm','-f',container],check=True)
