#!/usr/bin/env python3
"""PE explicit local prompt helper. No plaintext token fallback."""
import argparse, getpass, json, sys, uuid, urllib.request, urllib.error
ORIGIN='https://promptefficiently.com'
SERVICE='com.promptefficiently.desktop'
def vault():
    import keyring
    backend=keyring.get_keyring()
    if backend.priority <= 0 or backend.__class__.__module__ not in ('keyring.backends.macOS', 'keyring.backends.Windows', 'keyring.backends.SecretService', 'keyring.backends.kwallet'):
        raise RuntimeError('A secure OS keyring is required. No plaintext token fallback is allowed.')
    return keyring
def api(path,token=None,data=None):
    headers={'Content-Type':'application/json','User-Agent':'PromptEfficiently-Desktop/0.1.1'}
    if token: headers['Authorization']='Bearer '+token
    req=urllib.request.Request(ORIGIN+path,data=None if data is None else json.dumps(data).encode(),headers=headers,method='GET' if data is None else 'POST')
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*a): raise RuntimeError('Unexpected API redirect refused.')
    try:
        with urllib.request.build_opener(NoRedirect).open(req,timeout=20) as res: return json.load(res)
    except urllib.error.HTTPError as e:
        raise RuntimeError({401:'Sign in required or session expired.',429:'Five free uses used today. Open PE account to upgrade.',503:'PE temporarily unavailable; no estimate granted.'}.get(e.code,'PE request failed (%s).'%e.code)) from None
def estimate(text):
    return {'words':len(text.split()),'roughInputTokens':int(len(text.split())*1.3+0.5),'note':'Rough input tokens, not model-tokenized. Excludes context, output, tools and subscription credits. Not a cost or balance reading.'}
def tighten(text):
    import re
    out=re.sub(r'^(?:(?:can|could|would) you (?:please )?|please (?:could you )?|i would like you to |i want you to |i need you to )','',text.strip(),flags=re.I)
    return (out[0].upper()+out[1:]) if out else out

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['login','logout','status','estimate','tighten','upgrade']);args=p.parse_args()
    if args.command=='upgrade':
        import webbrowser
        webbrowser.open(ORIGIN+'/app'); print('Opened PE account. Sign in there for billing.');return
    k=vault()
    if args.command=='login':
        if not sys.stdin.isatty(): raise RuntimeError('Login requires your own interactive terminal. Never give codes or tokens to the AI assistant.')
        email=input('PE email: ').strip();api('/api/send-code',data={'email':email});code=getpass.getpass('Emailed six-digit code: ')
        if len(code)!=6 or not code.isdigit():raise RuntimeError('Enter a six-digit code.')
        r=api('/api/verify-code',data={'email':email,'code':code})
        if not r.get('ok') or not r.get('token'):raise RuntimeError('Sign-in could not be verified.')
        k.set_password(SERVICE,'session',r['token']);print('Signed in to PE.');return
    t=k.get_password(SERVICE,'session')
    if not t:raise RuntimeError('Run login in your own terminal first.')
    if args.command=='logout':api('/api/signout',t,{});k.delete_password(SERVICE,'session');print('Signed out.');return
    if args.command=='status':print(json.dumps(api('/api/billing/status',t),indent=2));return
    text=sys.stdin.read(1000001)
    if len(text)>1000000:raise RuntimeError('Prompt too large; maximum one million characters.')
    if not text.strip():raise RuntimeError('Pass the prompt through stdin. No workspace is read automatically.')
    r=api('/api/usage',t,{'requestId':str(uuid.uuid4())})
    if type(r.get('pro')) is not bool:raise RuntimeError('Unrecognized quota response. No estimate granted.')
    result={'input':estimate(text),'plan':'Pro' if r['pro'] else 'Free','remaining':r.get('remaining')}
    if args.command=='tighten':result.update(suggestion=tighten(text),review='Review before using. Never applied or submitted automatically.')
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    try:main()
    except Exception as e:print('PE: '+str(e),file=sys.stderr);sys.exit(1)
