"""Flask front end - computation only."""
import argparse, threading, uuid
from flask import Flask, jsonify, render_template_string, request, Response
from . import compute as dc
from .engine import FORM_KEYS, analyze
from .presets import BASE, PRESETS, HIGHLIGHTS
app=Flask(__name__); JOBS={}
def run_job(jid,form):
    job=JOBS[jid]
    def sp(p,l): job['progress']=p; job['label']=l
    try: job['result']=analyze(form,sp); job['status']='done'
    except Exception as e: job['status']='error'; job['error']=str(e) or e.__class__.__name__
def start_job(form):
    jid=str(uuid.uuid4()); JOBS[jid]={'status':'running','progress':0,'label':'Starting ...','result':None,'error':None,'preset':form.get('preset','')}
    threading.Thread(target=run_job,args=(jid,form),daemon=True).start(); return jid
def form_from_request():
    form={k: request.form.get(k,'') for k in FORM_KEYS}
    preset_name=(request.form.get('preset','') or '').strip(); preset=PRESETS.get(preset_name)
    if preset and (not (form.get('g') or '').strip()):
        for k,v in preset.items():
            if k in form and not (form.get(k) or '').strip(): form[k]=v
        form['preset']=preset_name
    form['preset']=preset_name
    if not (form.get('g') or '').strip(): raise ValueError('g is empty: pick a preset (not Custom blank) or paste a metric into g.')
    return form
HTML="""<!doctype html><!-- DGR-HTML-v4 --><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HLPL - Dual General Relativity</title>
<script>window.MathJax={tex:{inlineMath:[['\\\\(','\\\\)',['$','$']]]},displayAlign:'left',displayIndent:'0',svg:{fontCache:'global'}};</script>
<script src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js' async></script>
<style>
:root{--bg:#f7f8fa;--card:#ffffff;--card2:#eef1f5;--line:#d5dae4;--txt:#111827;--mut:#5b6478;--acc:#e11d48;--acc2:#b45309}
body.dark{--bg:#0b0e1a;--card:#141a2e;--card2:#1a2140;--line:#2a3460;--txt:#eef1ff;--mut:#aab3d6;--acc:#ff4d6d;--acc2:#ffb703}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font-family:Inter,system-ui,sans-serif}
.wrap{max-width:1320px;margin:0 auto;padding:10px 14px 24px}
.topbar{display:flex;justify-content:space-between;align-items:center;padding:2px 0 6px}.apptitle{margin:0;font-size:15px;font-weight:800;color:#4338ca}body.dark .apptitle{color:#a5b4fc}.themebtn{border:1px solid var(--line);background:var(--card);color:var(--txt);border-radius:999px;padding:6px 12px;font-weight:800;cursor:pointer;font-size:13px}.themebtn.fast{background:#059669;color:#fff;border-color:#059669}
.top{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px}
.topgrid{display:grid;grid-template-columns:1.1fr 1.4fr 1fr 1.2fr 1fr;gap:8px}@media(max-width:1100px){.topgrid{grid-template-columns:repeat(2,1fr)}}@media(max-width:600px){.topgrid{grid-template-columns:1fr}}
.col{background:var(--card2);border:1px solid var(--line);border-radius:10px;padding:7px}
.col h3{margin:0 0 3px;font-size:13px;color:var(--acc2)}
.hint{color:var(--mut);font-size:11px;line-height:1.35;margin:3px 0}
label{display:block;font-weight:700;font-size:12px;margin:5px 0 2px}input,textarea,select{width:100%;background:var(--card);color:var(--txt);border:1px solid var(--line);border-radius:7px;padding:6px;font-size:13px}textarea{min-height:42px;font-family:ui-monospace,monospace}input:focus,textarea:focus,select:focus{outline:2px solid var(--acc)}
.row4{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px}
.seg{display:flex;background:var(--card);border:1px solid var(--line);border-radius:7px;padding:2px;gap:2px}.seg label{margin:0;flex:1;text-align:center;padding:5px;border-radius:5px;cursor:pointer;font-size:12px}.seg input{display:none}.seg input:checked+span{background:var(--acc);color:#fff;border-radius:5px;display:block}
.btn{width:100%;border:0;border-radius:9px;padding:8px;font-size:15px;font-weight:900;cursor:pointer;background:linear-gradient(90deg,#4f46e5,#06b6d4);color:#fff;margin-top:8px;box-shadow:0 6px 18px #4f46e533}.btn:hover{background:linear-gradient(90deg,#4338ca,#0891b2)}.btn:disabled{opacity:.55;cursor:wait}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px;margin-top:12px}
.card h2{margin:0 0 5px;font-size:17px;color:#4338ca}body.dark .card h2{color:#a5b4fc}.card h3{color:#0e7490}body.dark .card h3{color:#67e8f9}
.verdict{border-radius:10px;padding:9px;margin:7px 0;font-weight:400}.pass{background:#d1fae5;border:1px solid #6ee7b7}body.dark .pass{background:#2ee6a822;border-color:#2ee6a855}.fail{background:#fee2e2;border:1px solid #fca5a5}body.dark .fail{background:#ff5d5d22;border-color:#ff5d5d66}
details{background:var(--card2);border:1px solid var(--line);border-radius:9px;padding:8px 10px;margin:6px 0}summary{cursor:pointer;font-weight:800}.formula{overflow-x:auto;font-size:15px;text-align:left}.notes{margin-top:10px;border-top:1px solid var(--line);padding-top:8px}.notes h3{margin:0 0 4px;font-size:14px;color:#0e7490}body.dark .notes h3{color:#67e8f9}.notes ol{margin:4px 0 0 18px;padding:0;line-height:1.55;font-size:14px}.notes li{margin:3px 0}.explain{border-left:4px solid var(--acc2);background:var(--card);border-radius:12px;padding:12px;margin-top:12px}.explain h2{margin:0 0 6px;font-size:17px;color:#7c3aed}body.dark .explain h2{color:#c4b5fd}.explain p b{color:#be185d}body.dark .explain p b{color:#f9a8d4}.explain .term b{color:#047857}body.dark .explain .term b{color:#6ee7b7}.explain .badge{display:inline-block;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;border-radius:999px;padding:3px 9px;font-size:12px;font-weight:800}.explain p{line-height:1.55;font-size:14px;margin:6px 0}.explain .term{background:var(--card2);border:1px solid var(--line);border-radius:9px;padding:9px;font-size:14px;line-height:1.5}.formula mjx-container{margin:0 !important;text-align:left !important;justify-content:flex-start !important}summary mjx-container{margin:0 !important}
#progress{height:8px;background:#00000014;border-radius:999px;overflow:hidden;margin-top:7px;display:none}#bar{height:100%;width:0%;background:linear-gradient(90deg,#4f46e5,#06b6d4,#10b981);transition:width .3s}
footer{color:var(--mut);font-size:12px;margin-top:10px}
</style></head><body>
<div class='wrap'>
<div class='topbar'><p class='apptitle'>HLPL - Dual General Relativity</p><span style='display:flex;gap:6px'><button class='themebtn' id='modeBtn' type='button' onclick='toggleMode()'>Mode: Normal</button><button class='themebtn' id='themeBtn' type='button' onclick='toggleTheme()'>White / Dark</button></span></div>
<form id='calc-form' onsubmit='return false'>
<div class='top'><div class='topgrid'>
<div class='col'><h3>Preset — just a starting point</h3>
<label>Preset</label><select id='preset' name='preset' onchange='loadPreset(this.value)'><option value='' selected disabled>— pick a preset —</option>{% for glabel,items in preset_groups %}<optgroup label='{{glabel}}'>{% for k,badge in items %}<option value='{{k}}'>{% if badge %}★ {{badge}} — {% endif %}{{k}}</option>{% endfor %}</optgroup>{% endfor %}</select><p class='hint'>★ = highlighted: GR test, dark matter, or dark energy (see explanation below the output).</p>
<label>Coordinates</label><input name='coords' value='{{first.coords}}'>
<p class='hint'>Swap exchanges the first two coordinates. Matrix: rows by ; , entries by , .</p></div>
<div class='col'><h3>Inputs</h3>
<label>g<sub>μν</sub> — any metric</label><textarea name='g'>{{first.g}}</textarea>
<label>T<sup>g</sup><sub>μν</sub> — blank = vacuum (0)</label><textarea name='Tg'>{{first.Tg}}</textarea></div>
<div class='col'><h3>T<sup>f</sup> rule</h3>
<div class='seg'><label><input type='radio' name='Tf_mode' value='same'><span>Same</span></label><label><input type='radio' name='Tf_mode' value='vacuum' checked><span>Vacuum</span></label><label><input type='radio' name='Tf_mode' value='set'><span>Set</span></label></div>
<label>T<sup>f</sup><sub>μν</sub> — only if Set (blank = vacuum)</label><textarea name='Tf'>{{first.Tf}}</textarea>
<p class='hint'>f has its own parameters: r_s → r_t, others → name_t. Both metrics solve EE.</p></div>
<div class='col'><h3>Parameters</h3>
<div class='row4'><div><label>α</label><input name='alpha' value='{{first.alpha}}'></div><div><label>β</label><input name='beta' value='{{first.beta}}'></div><div><label>γ</label><input name='gamma' value='{{first.gamma}}'></div><div><label>ε</label><select name='eps'><option value='-1' selected>-1</option><option value='1'>+1</option></select></div></div>
<label>κ in ε = G − κT</label><input name='kappa' value='{{first.kappa}}'>
<label>η — only for D / h info</label><select name='eta_preset'><option value='spherical'>Spherical</option><option value='cartesian'>Cartesian</option><option value='custom'>Custom</option></select>
<label>Custom η</label><textarea name='eta' style='min-height:32px'>{{first.eta}}</textarea></div>
<div class='col'><h3>Geodesics</h3>
<p class='hint'>ẍ<sup>μ</sup> = −Γ<sup>μ</sup><sub>ab</sub> v<sup>a</sup>v<sup>b</sup></p>
<label>v<sup>μ</sup> = dx<sup>μ</sup>/dt for g</label><input name='vg' value='{{first.vg}}'>
<label>v<sup>μ</sup> = dx<sup>μ</sup>/dr for f</label><input name='vf' value='{{first.vf}}'>
<label>Evaluation point</label><input name='point' value='{{first.point}}'>
<p class='hint'>Give f its own value in the point, e.g. r_s=1, r_t=2. If r_t is omitted it defaults to r_s.</p>
<p><label style='display:inline'><input type='checkbox' name='opt_K' value='1' checked> Kretschmann K</label></p></div>
</div>
<button class='btn' id='computeBtn' type='button' onclick='compute()'>Compute →</button><div id='progress'><div id='bar'></div></div><div id='plabel' class='hint'></div>
</div>
</form>
<div id='results'><div class='card'><h2>Results</h2><p class='hint'>After Compute you get: f (own params), T<sup>f</sup>, G[g], ε[g], G[f], ε[f], ẍ<sup>μ</sup> for both, EE satisfied? for both, plus R, det, K, Γ, D, h.</p></div></div>
<div id='explanation'></div>
<footer>\\(f = \\epsilon\\,\\varphi^* g,\\ \\varepsilon = G - \\kappa T,\\ \\ddot{x}^\\mu + \\Gamma^\\mu_{ab}\\,\\dot{x}^a\\dot{x}^b = 0\\). Local use only.</footer>
<div class='card' id='mode-note'><details><summary>Fast mode vs Normal mode</summary>
<p><b>Normal mode</b> (the default) is the full calculation: full simplification (factor + cancel + together), Kretschmann scalar \\(K\\) computed when ticked, and the Einstein equations checked <b>symbolically</b> — \\(G - \\kappa T\\) is simplified to exactly zero. Use Normal when you want the cleanest, fully simplified expressions and a symbolic EE proof.</p>
<p><b>Fast mode</b> trades simplification for speed, and changes three things:</p>
<ul><li><b>Kretschmann skipped.</b> \\(K\\) is the single most expensive scalar, and nothing else needs it.</li>
<li><b>Light simplification.</b> Only <code>together()</code> — no <code>cancel()</code>, no <code>factor()</code>. Same maths, the expressions just stay as single fractions instead of fully factored.</li>
<li><b>EE checked numerically at your point.</b> Instead of a second full symbolic simplification of \\(G - \\kappa T\\), Fast checks \\(|G - \\kappa T| < 10^{-6}\\) at the evaluation point you entered.</li></ul>
<p><b>Measured examples (fresh runs):</b> Schwarzschild — about 0.4s in both modes. Schwarzschild interior (constant density star) — Normal about 39s vs Fast about 3s. Fast helps where Kretschmann or the symbolic EE re-simplification is the bottleneck, but it is not guaranteed faster on every metric: the lighter simplification leaves larger, less-factored expressions, which can offset the saving.</p>
<p><b>Honest limit:</b> Kerr and Alcubierre stay slow in <b>both</b> modes. Their symbolic expressions are so huge that every downstream step (curvature, geodesic acceleration, EE check, rendering) chokes on them too. That is a symbolic-expression-size problem, not a simplification-setting problem — Fast mode does not make them fast.</p>
</details></div>
</div>
<script>var FORM=document.getElementById('calc-form');
function setForm(p){for(var k in p){var el=FORM.elements[k];if(!el)continue;if(el.type=='checkbox')el.checked=!!p[k];else if(el.type=='radio'){FORM.querySelectorAll('[name='+k+']').forEach(r=>{r.checked=(r.value==p[k])});}else el.value=p[k];}}
function enableCompute(){var b=document.getElementById('computeBtn');if(b){b.disabled=false;b.textContent='Compute →';}}
function showExplanation(h,n){var el=document.getElementById('explanation');if(!el)return;if(!h){el.innerHTML='';return;}el.innerHTML='<div class="explain"><h2>Why this metric matters</h2><p><b>'+n+'</b> — <span class="badge">'+h.badge+'</span></p><p><b>Why:</b> '+h.why+'</p><p class="term"><b>Which term does it:</b> '+h.term+'</p><p class="hint">Dark matter and dark energy are not tests - they are explanations of observed data. GR tests are the measured effects listed above.</p></div>';} function loadPreset(n){return fetch('/api/preset?name='+encodeURIComponent(n)).then(r=>{if(!r.ok)throw new Error('preset fetch '+r.status);return r.json();}).then(p=>{p.preset=n;setForm(p);showExplanation(p.highlight,n);enableCompute();}).catch(e=>{enableCompute();});}
function formData(){var d=new FormData(FORM);if(!FORM.elements['opt_K'].checked)d.delete('opt_K');if(window.MODE==='fast')d.set('fast','1');else d.delete('fast');return d;}
var T0=0,TTIMER=null,LASTP=0,LASTL='';function fmtMMSS(ms){var t=Math.floor(ms/1000);var m=Math.floor(t/60),ss=t%60;return (m<10?'0'+m:m)+':'+(ss<10?'0'+ss:ss);}function tickLabel(){var el=document.getElementById('plabel');if(el)el.textContent=LASTP+'% - '+LASTL+' '+fmtMMSS(Date.now()-T0);}function poll(id){fetch('/api/progress/'+id).then(r=>r.json()).then(j=>{document.getElementById('progress').style.display='block';document.getElementById('bar').style.width=j.progress+'%';LASTP=j.progress;LASTL=j.label;tickLabel();if(j.status=='running')setTimeout(()=>poll(id),400);else {if(TTIMER){clearInterval(TTIMER);TTIMER=null;}var el2=document.getElementById('plabel');if(el2)el2.textContent='Done - '+fmtMMSS(Date.now()-T0);fetch('/api/result/'+id).then(r=>r.text()).then(t=>{var el=document.getElementById('results');el.innerHTML=t;if(window.MathJax&&MathJax.typesetPromise){MathJax.typesetPromise([el]).catch(function(){MathJax.typesetPromise();});}});}});}
function compute(){if(!(FORM.elements['g'].value||'').trim()){document.getElementById('results').innerHTML="<div class='card'><div class='verdict fail'>g is empty: pick a preset (not Custom blank) or paste a metric into g, then Compute.</div></div>";return;}T0=Date.now();LASTP=0;LASTL='Starting ...';if(TTIMER)clearInterval(TTIMER);TTIMER=setInterval(tickLabel,1000);fetch('/api/start',{method:'POST',body:formData()}).then(r=>{if(!r.ok)return r.json().then(e=>{throw new Error(e.error||'Compute failed');});return r.json();}).then(j=>poll(j.job_id)).catch(e=>{document.getElementById('results').innerHTML="<div class='card'><div class='verdict fail'>"+e.message+"</div></div>";});}
var MODE=localStorage.getItem('dgr-mode')||'normal';function applyMode(){var b=document.getElementById('modeBtn');if(!b)return;b.textContent=(MODE==='fast'?'Mode: Fast':'Mode: Normal');b.classList.toggle('fast',MODE==='fast');}function toggleMode(){MODE=(MODE==='fast'?'normal':'fast');localStorage.setItem('dgr-mode',MODE);applyMode();}applyMode();
if(localStorage.getItem('dgr-theme')==='dark')document.body.classList.add('dark');function toggleTheme(){document.body.classList.toggle('dark');localStorage.setItem('dgr-theme',document.body.classList.contains('dark')?'dark':'light');}
if(window.MathJax)MathJax.typesetPromise();
</script></body></html>"""
RESULT_HTML="""{% if error %}<div class='card'><div class='verdict fail'>{{error}}</div></div>{% endif %}{% if result %}
<div class='card'><h2>Einstein equations</h2>{% for name,ok,kind in checks %}<div class='verdict {{'pass' if ok else 'fail'}}'>{{name}} — {{'SATISFIED' if ok else 'NOT SATISFIED'}}</div>{% endfor %}{% if notes %}<div class='notes'><h3>Notes:</h3><ol>{% for note in notes %}<li>{{note}}</li>{% endfor %}</ol></div>{% endif %}<p class='hint'>This is just ε = 0 checked.</p></div>
<div class='card'><h2>Scalars &amp; geodesics</h2>{% for name,val in scalars %}<div class='formula'>$$ {{name}} = {{val}} $$</div>{% endfor %}{% if numeric %}<h3>At the point</h3><div class='formula'>$$ {{numeric}} $$</div>{% endif %}</div>
<div class='card'><h2>All tensors</h2>{% for title,body in sections %}<details><summary>$$ {{title}} $$</summary><div class='formula'>$$ {{body}} $$</div></details>{% endfor %}</div>{% if explanation %}<div class='explain'><h2>Why this metric matters</h2><span class='badge'>{{explanation.badge}}</span><p><b>Why:</b> {{explanation.why}}</p><p class='term'><b>Which term does it:</b> {{explanation.term}}</p><p class='hint'>Dark matter and dark energy are not tests - they are explanations of observed data.</p></div>{% endif %}{% endif %}"""
def _preset_groups():
    gr=[(k,HIGHLIGHTS[k]['badge']) for k in PRESETS if k in HIGHLIGHTS and HIGHLIGHTS[k]['kind']=='gr-test']
    de=[(k,HIGHLIGHTS[k]['badge']) for k in PRESETS if k in HIGHLIGHTS and HIGHLIGHTS[k]['kind']=='dark-energy']
    other=[(k,'') for k in PRESETS if k not in HIGHLIGHTS]
    return [('GR TESTS + DARK MATTER (highlighted)',gr),('DARK ENERGY (highlighted)',de),('OTHER METRICS',other)]
@app.route('/')
def index():
    names=list(PRESETS); first=dict(PRESETS[names[0]]) if names else dict(BASE); first['preset']=names[0] if names else ''
    for k in ('coords','g','Tg','Tf','alpha','beta','gamma','kappa','eta','vg','vf','point'): first.setdefault(k,'')
    html = render_template_string(HTML,presets=names,first=first,preset_groups=_preset_groups())
    return Response(html, mimetype='text/html; charset=utf-8')
@app.route('/api/preset')
def api_preset():
    name=request.args.get('name',''); d=dict(PRESETS.get(name,BASE)); d['highlight']=HIGHLIGHTS.get(name); return jsonify(d)
@app.route('/api/start',methods=['POST'])
def api_start():
    try: form=form_from_request()
    except ValueError as e: return jsonify({'error':str(e)}),400
    return jsonify({'job_id':start_job(form)})
@app.route('/api/progress/<job_id>')
def api_progress(job_id):
    job=JOBS.get(job_id)
    if not job: return jsonify({'status':'error','progress':0,'label':'unknown job'}),404
    return jsonify({'status':job['status'],'progress':job['progress'],'label':job['label']})
@app.route('/api/result/<job_id>')
def api_result(job_id):
    job=JOBS.get(job_id)
    if not job: return 'Unknown job',404
    if job['status']=='error': return Response(render_template_string(RESULT_HTML,error=job['error'],result=False,notes=[]), mimetype='text/html; charset=utf-8')
    if job['status']!='done': return 'Not ready yet',409
    r=job['result']; return render_template_string(RESULT_HTML,error=None,result=True,sections=r['sections'],scalars=r['scalars'],checks=r['checks'],numeric=r['numeric'],events=r['events'],explanation=HIGHLIGHTS.get(job.get('preset','')),notes=r.get('notes',[]))
@app.route('/api/events')
def api_events():
    try: a,b,c,rs=(float(request.args[k]) for k in ('a','b','c','rs'))
    except Exception: return jsonify({'error':'alpha, beta, gamma, r_s must be numbers'})
    out=dc.schwarzschild_pair_events(a,b,c,rs); out['rs']=rs; return jsonify(out)
@app.route('/health')
def health(): return Response('DGR-HTML-v4 ok', mimetype='text/plain')
def create_app(): return app
def main(argv=None):
    ap=argparse.ArgumentParser(prog='dual-general-relativity'); ap.add_argument('--host',default='127.0.0.1'); ap.add_argument('--port',type=int,default=5000); ap.add_argument('--debug',action='store_true'); a=ap.parse_args(argv)
    for port in (a.port, 5001, 5002):
        try:
            print(f'DGR Calculator v4 - open http://{a.host}:{port} - if you see JSON, an OLD server is still on the old port: close it and use this URL')
            app.run(host=a.host,port=port,debug=a.debug)
            break
        except OSError as e:
            print(f'Port {port} in use ({e}) - trying next port...')
if __name__=='__main__': main()
