import os, tempfile, functools
from flask import Flask, request, jsonify, session
from generate_proposal import build
import requests as http

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'hd-hauling-dev-key')

APP_PIN         = os.environ.get('APP_PIN', '2025')
NOTION_KEY      = os.environ.get('NOTION_KEY', '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')
NOTION_PIPELINE = os.environ.get('NOTION_PIPELINE', '2ada1cc5891b80bebe53fde6c337bf8b')
NOTION_CLIENTS  = os.environ.get('NOTION_CLIENTS',  '2ada1cc5891b804cbaa1c4d2577b674c')
NOTION_VER      = '2022-06-28'

def require_auth(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
                    if not session.get('authenticated'):
                                    return jsonify({'error': 'Unauthorized'}), 401
                                return f(*args, **kwargs)
                return decorated

@app.route('/')
def index():
        return app.send_static_file('index.html')

@app.route('/auth/login', methods=['POST'])
def login():
        pin = str((request.get_json() or {}).get('pin', '')).strip()
    if pin == APP_PIN:
                session['authenticated'] = True
                session.permanent = True
                return jsonify({'ok': True})
            return jsonify({'error': 'Incorrect PIN'}), 401

@app.route('/auth/logout', methods=['POST'])
def logout():
        session.clear()
    return jsonify({'ok': True})

@app.route('/auth/check')
def auth_check():
        return jsonify({'authenticated': bool(session.get('authenticated'))})

@app.route('/generate-pdf', methods=['POST'])
@require_auth
def generate_pdf():
        tmp_path = None
    try:
                data = request.get_json()
                if not data:
                                return jsonify({'error': 'No data provided'}), 400
                            if not data.get('project_name'):
                                            return jsonify({'error': 'project_name is required'}), 400
                                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                                                        tmp_path = tmp.name
                                                    build(data, tmp_path)
        with open(tmp_path, 'rb') as f:
                        pdf_bytes = f.read()
                    project_name = data.get('project_name', 'Proposal').replace(' ', '_')
        return app.response_class(
                        pdf_bytes,
                        mimetype='application/pdf',
                        headers={
                                            'Content-Disposition': f'attachment; filename="HD_Proposal_{project_name}.pdf"',
                                            'Content-Length': len(pdf_bytes),
                        }
        )
except Exception as e:
        return jsonify({'error': str(e)}), 500
finally:
        if tmp_path and os.path.exists(tmp_path):
                        try: os.unlink(tmp_path)
                                        except: pass

            @app.route('/notion/clients')
@require_auth
def notion_clients():
        try:
                    r = http.post(
                                    f'https://api.notion.com/v1/databases/{NOTION_CLIENTS}/query',
                                    headers={'Authorization': f'Bearer {NOTION_KEY}', 'Notion-Version': NOTION_VER, 'Content-Type': 'application/json'},
                                    json={'page_size': 100}, timeout=10
                    )
                    return jsonify(r.json()), r.status_code
        except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notion/push', methods=['POST'])
@require_auth
def notion_push():
        try:
                    data = request.get_json() or {}
                    payload = {
                        'parent': {'database_id': NOTION_PIPELINE},
                        'properties': {
                            'Name':       {'title': [{'text': {'content': data.get('project_name','')}}]},
                            'Client':     {'rich_text': [{'text': {'content': data.igmepto(r'tc loise,n tt_enmapmfei'l,e',' )f}u}n]c}t,o
            o l s 
             f r o m   f l a s k   i m'pAodrdtr eFslsa's:k ,   r e{q'ureiscth,_ tjesxotn'i:f y[,{ 'steesxsti'o:n 
            {f'rcoomn tgeennte'r:a tdea_tpar.ogpeots(a'la didmrpeosrst' ,b'u'i)l}d}
            ]i}m,p
            o r t   r e q u e s t s   a s   h'tDtapt
            e
            'a:p p   =   F l a{s'kd(a_t_en'a:m e{_'_s,t asrtta't:i cd_aftoal.dgeert=(''.d'a,t es_tiastoi'c,_ u'r'l)_}p}a,t
            h = ' ' ) 
             a p p . s e c r e t _'kSetya t=u so's:. e n v i r{o'ns.egleetc(t''S:E C{R'EnTa_mKeE'Y:' ,' Q'uhodt-ehda'u}l}i,n
            g - d e v - k e y ' ) 

             A P P _'PBIiNd   T o t a l ' :  =  {o'sn.uemnbveirr'o:n .dgaetta(.'gAePtP(_'PtIoNt'a,l '',2 002)5}',)

             N O T I O N _ K E Y            '=T ootsa.le nSvFi'r:o n . g{e'tn(u'mNbOeTrI'O:N _dKaEtYa'.,g e'tn(t'nt_o4t3a4l3_2s3f8'0,6 909)1}Y,g
            L 3 D t 8 O 6 b W R 7 g f}h
            8 w 5 g s 1 f F x}V
            A u 4 e p g n M 'r) 
            =N OhTtItOpN._pPoIsPtE(L
            I N E   =   o s . e n v i'rhotnt.pgse:t/(/'aNpOiT.InOoNt_iPoInP.EcLoImN/Ev'1,/ p'a2gaedsa'1,c
            c 5 8 9 1 b 8 0 b e b e 5h3efaddee6rcs3=3{7'bAfu8tbh'o)r
            iNzOaTtIiOoNn_'C:L IfE'NBTeSa r e=r  o{sN.OeTnIvOiNr_oKnE.Yg}e't,( ''NNOoTtIiOoNn_-CVLeIrEsNiToSn'',:   N'O2TaIdOaN1_cVcE5R8,9 1'bC8o0n4tcebnata-1Tcy4pde2'5:7 7'ba6p7p4lci'c)a
            tNiOoTnI/OjNs_oVnE'R} , 
                    =   ' 2 0 2 2 - 0j6s-o2n8='p
            a
            ydleofa dr,e qtuiimreeo_uatu=t1h0(
            f ) : 
                     @)f
            u n c t o o l s .rwersapp s=( fr).
            j s o n (d)e
            f   d e c o r a tiefd (r*.aorkg:s
            ,   * * k w a r g s ) : 
            p i d   =   r e sipf. gneott( 'sieds's,i'o'n)..greetp(l'aacuet(h'e-n't,i'c'a)t
            e d ' ) : 
                          r e t u r nr ejtsuornni fjys(o{n'iofky'(:{ 'Terrureo,r '':u r'lU'n:a uft'hhotrtipzse:d/'/}n)o,t i4o0n1.
            s o / { p i d } 'r}e)t
            u r n   f ( * a rrgest,u r*n* kjwsaorngisf)y
            ( { ' e rrreotru'r:n  rdeescpo.rgaette(d'
            m
            e@saspapg.er'o,u'tNeo(t'i/o'n) 
            edrerfo ri'n)d}e)x,( )r:.
            s t a t urse_tcuordne 
            a p p . seexncde_pstt aEtxicce_pftiiloen( 'aisn dee:x
            . h t m l ' ) 

            r@eatpupr.nr ojustoen(i'f/ya(u{t'he/rlroogri'n:' ,s tmre(teh)o}d)s,= [5'0P0O
            S
            T@'a]p)p
            .dreofu tleo(g'i/nh(e)a:l
            t h ' ) 
            pdienf  =h esatlrt(h((r)e:q
            u e s t .rgeettu_rjns ojns(o)n iofry ({{}')s.tgaettu(s''p:i n''o,k ''}'))
            )
            .isft r_i_pn(a)m
            e _ _   =i=f  'p_i_nm a=i=n _A_P'P:_
            P I N : 
            a p p . r u n ( hsoessts=i'o0n.[0'.a0u.t0h'e,n tpiocratt=eidn't]( o=s .Ternuvei
            r o n . g e t ( 'sPeOsRsTi'o,n .5p0e0r0m)a)n,e ndte b=u gT=rFuael
            s e ) 
                 return jsonify({'ok': True})
                return jsonify({'error': 'Incorrect PIN'}), 401

            @app.route('/auth/logout', methods=['POST'])
            def logout():
                session.clear()
                return jsonify({'ok': True})

            @app.route('/auth/check')
            def auth_check():
                return jsonify({'authenticated': bool(session.get('authenticated'))})

            @app.route('/generate-pdf', methods=['POST'])
            @require_auth
            def generate_pdf():
                tmp_path = None
                try:
                    data = request.get_json()
                    if not data:
                        return jsonify({'error': 'No data provided'}), 400
                    if not data.get('project_name'):
                        return jsonify({'error': 'project_name is required'}), 400
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                        tmp_path = tmp.name
                    build(data, tmp_path)
                    with open(tmp_path, 'rb') as f:
                        pdf_bytes = f.read()
                    project_name = data.get('project_name', 'Proposal').replace(' ', '_')
                    return app.response_class(
                        pdf_bytes,
                        mimetype='application/pdf',
                        headers={
                            'Content-Disposition': f'attachment; filename="HD_Proposal_{project_name}.pdf"',
                            'Content-Length': len(pdf_bytes),
                        }
                    )
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        try: os.unlink(tmp_path)
                        except: pass

            @app.route('/notion/clients')
            @require_auth
            def notion_clients():
                try:
                    r = http.post(
                        f'https://api.notion.com/v1/databases/{NOTION_CLIENTS}/query',
                        headers={'Authorization': f'Bearer {NOTION_KEY}', 'Notion-Version': NOTION_VER, 'Content-Type': 'application/json'},
                        json={'page_size': 100}, timeout=10
                    )
                    return jsonify(r.json()), r.status_code
                except Exception as e:
                    return jsonify({'error': str(e)}), 500

            @app.route('/notion/push', methods=['POST'])
            @require_auth
            def notion_push():
                try:
                    data = request.get_json() or {}
                    payload = {
                        'parent': {'database_id': NOTION_PIPELINE},
                        'properties': {
                            'Name':       {'title': [{'text': {'content': data.get('project_name','')}}]},
                            'Client':     {'rich_text': [{'text': {'content': data.get('client_name','')}}]},
                            'Address':    {'rich_text': [{'text': {'content': data.get('address','')}}]},
                            'Date':       {'date': {'start': data.get('date_iso', '')}},
                            'Status':     {'select': {'name': 'Quoted'}},
                            'Bid Total':  {'number': data.get('total', 0)},
                            'Total SF':   {'number': data.get('total_sf', 0)},
                        }
                    }
                    r = http.post(
                        'https://api.notion.com/v1/pages',
                        headers={'Authorization': f'Bearer {NOTION_KEY}', 'Notion-Version': NOTION_VER, 'Content-Type': 'application/json'},
                        json=payload, timeout=10
                    )
                    resp = r.json()
                    if r.ok:
                        pid = resp.get('id','').replace('-','')
                        return jsonify({'ok': True, 'url': f'https://notion.so/{pid}'})
                    return jsonify({'error': resp.get('message','Notion error')}), r.status_code
                except Exception as e:
                    return jsonify({'error': str(e)}), 500

            @app.route('/health')
            def health():
                return jsonify({'status': 'ok'})

            if __name__ == '__main__':
                app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
            
