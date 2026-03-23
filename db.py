"""
db.py — Supabase REST API wrapper for hd-app
Tables: clients, proposals, pipeline_stages
"""
import os, json
import requests

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

def _h(prefer='return=representation'):
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': prefer,
    }

def _url(table):
    return f'{SUPABASE_URL}/rest/v1/{table}'

def init_db():
    pass  # Tables managed via Supabase SQL editor

# ── Proposals ────────────────────────────────────────────────────────────────

def save_quote(name, client, date, total, snap):
    payload = {
        'name':   name,
        'client': client,
        'date':   date,
        'total':  float(total),
        'snap':   snap if isinstance(snap, dict) else json.loads(snap),
    }
    r = requests.post(_url('proposals'), headers=_h(), json=payload, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data[0]['id'] if data else None

def list_quotes():
    r = requests.get(_url('proposals'), headers=_h(),
                     params={'order': 'created_at.desc', 'select': '*'},
                     timeout=10)
    r.raise_for_status()
    return r.json()

def get_quote(qid):
    r = requests.get(_url('proposals'), headers=_h(),
                     params={'id': f'eq.{qid}', 'select': '*'}, timeout=10)
    r.raise_for_status()
    d = r.json()
    return d[0] if d else None

def delete_quote(qid):
    r = requests.delete(_url('proposals'), headers=_h(''),
                        params={'id': f'eq.{qid}'}, timeout=10)
    r.raise_for_status()

def update_proposal(qid, fields):
    if 'updated_at' not in fields:
        fields['updated_at'] = 'now()'
    r = requests.patch(_url('proposals'), headers=_h(),
                       params={'id': f'eq.{qid}'},
                       json=fields, timeout=10)
    r.raise_for_status()

# ── Clients ───────────────────────────────────────────────────────────────────

def list_clients():
    r = requests.get(_url('clients'), headers=_h(),
                     params={'order': 'name.asc', 'select': '*'}, timeout=10)
    r.raise_for_status()
    return r.json()

def save_client(data):
    r = requests.post(_url('clients'), headers=_h(), json=data, timeout=10)
    r.raise_for_status()
    d = r.json()
    return d[0] if d else None

def update_client(cid, data):
    r = requests.patch(_url('clients'), headers=_h(),
                       params={'id': f'eq.{cid}'}, json=data, timeout=10)
    r.raise_for_status()

def delete_client(cid):
    r = requests.delete(_url('clients'), headers=_h(''),
                        params={'id': f'eq.{cid}'}, timeout=10)
    r.raise_for_status()

# ── Pipeline stages ───────────────────────────────────────────────────────────

def list_stages():
    r = requests.get(_url('pipeline_stages'), headers=_h(),
                     params={'order': 'position.asc', 'select': '*'}, timeout=10)
    r.raise_for_status()
    return r.json()

# ── Pipeline (proposals with stage info) ─────────────────────────────────────

def list_pipeline():
    r = requests.get(_url('proposals'), headers=_h(),
                     params={
                         'order': 'created_at.desc',
                         'select': '*,pipeline_stages(name,color,position,counts_in_ratio,is_closed)',
                     }, timeout=10)
    r.raise_for_status()
    return r.json()
