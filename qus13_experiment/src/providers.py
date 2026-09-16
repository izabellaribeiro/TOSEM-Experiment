from __future__ import annotations
import os,time,requests

RETRYABLE={429,500,502,503,504}

def _post(url,headers,body,timeout=600,max_attempts=6):
    last=None
    for attempt in range(1,max_attempts+1):
        r=requests.post(url,headers=headers,json=body,timeout=timeout)
        if r.status_code not in RETRYABLE:
            r.raise_for_status(); return r
        last=r
        if attempt==max_attempts: break
        wait=min(60,2**attempt)
        retry_after=r.headers.get('Retry-After')
        if retry_after:
            try: wait=max(wait,float(retry_after))
            except: pass
        print(f'RETRY HTTP {r.status_code}: waiting {wait:.1f}s (attempt {attempt}/{max_attempts})')
        time.sleep(wait)
    last.raise_for_status()

def _openai_text(resp:dict)->str:
    if resp.get('output_text'): return resp['output_text']
    chunks=[]
    for item in resp.get('output',[]):
        for c in item.get('content',[]):
            if c.get('type') in ('output_text','text') and c.get('text'): chunks.append(c['text'])
    if chunks:return '\n'.join(chunks)
    raise ValueError('Could not extract text from OpenAI response')

def call_openai(model,system,user,temperature=0,timeout=600,request_options=None):
    key=os.environ['OPENAI_API_KEY']
    request_options=request_options or {}
    body={'model':model,'input':[{'role':'system','content':system},{'role':'user','content':user}]}
    # Older GPT-5 family models such as gpt-5-mini reject the temperature field.
    # Keep the global experiment temperature for providers/models that support it,
    # but omit it explicitly when requested by the model configuration.
    if not request_options.get('omit_temperature', False):
        body['temperature']=temperature
    r=_post('https://api.openai.com/v1/responses',{'Authorization':f'Bearer {key}','Content-Type':'application/json'},body,timeout)
    raw=r.json(); return body,raw,_openai_text(raw)

def call_google(model,system,user,temperature=0,timeout=600,request_options=None):
    key=os.environ['GEMINI_API_KEY']; url=f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}'
    body={'systemInstruction':{'parts':[{'text':system}]},'contents':[{'role':'user','parts':[{'text':user}]}],
          'generationConfig':{'temperature':temperature,'responseMimeType':'application/json'}}
    r=_post(url,{'Content-Type':'application/json'},body,timeout); raw=r.json()
    text=''.join(p.get('text','') for c in raw.get('candidates',[]) for p in c.get('content',{}).get('parts',[]))
    return body,raw,text

def call_deepseek(model,system,user,temperature=0,timeout=600,request_options=None):
    key=os.environ['DEEPSEEK_API_KEY']
    body={'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':user}],'temperature':temperature}
    r=_post('https://api.deepseek.com/chat/completions',{'Authorization':f'Bearer {key}','Content-Type':'application/json'},body,timeout)
    raw=r.json(); return body,raw,raw['choices'][0]['message']['content']

def call(provider,model,system,user,temperature=0,timeout=600,request_options=None):
    if provider=='openai':return call_openai(model,system,user,temperature,timeout,request_options)
    if provider=='google':return call_google(model,system,user,temperature,timeout,request_options)
    if provider=='deepseek':return call_deepseek(model,system,user,temperature,timeout,request_options)
    raise ValueError(f'Unknown provider: {provider}')
