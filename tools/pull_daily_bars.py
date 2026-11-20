#!/usr/bin/env python3
"""Pulls Yahoo Finance daily bars (the same symbols as free_data2.py) from 2026-09-25 and writes merged_yahoo.csv
(sym,date,o,h,l,c,v). Run by .github/workflows/fwd-data.yml; the forward test reads it from the fwd-data branch."""
import json, time, datetime as dt, urllib.request, urllib.parse, csv, sys
SYMS = ['ES=F', 'NQ=F', 'YM=F', 'RTY=F', 'CL=F', 'NG=F', 'GC=F', 'SI=F', 'HG=F', 'PL=F', 'PA=F', 'ZB=F', 'ZN=F', 'ZF=F', 'ZT=F', 'ZC=F', 'ZS=F', 'ZW=F', 'ZM=F', 'ZL=F', 'LE=F', 'HE=F', 'GF=F', 'CC=F', 'KC=F', 'SB=F', 'CT=F', '6E=F', '6J=F', '6B=F', '6A=F', '6C=F', '6S=F', '6M=F', '6N=F', '6Z=F', '6L=F', 'HO=F', 'RB=F', 'KE=F', 'ZO=F', 'ZR=F', 'DC=F', 'LBR=F', 'UB=F', 'DX-Y.NYB', '^GSPC', '^NDX', '^VIX', '^TNX', 'BTC-USD', 'ETH-USD']
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
p1 = int(dt.datetime(2026, 9, 25).timestamp()); p2 = int(time.time()) + 86400
rows = []; bad = []
for s in SYMS:
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + urllib.parse.quote(s) + f'?period1={p1}&period2={p2}&interval=1d'
    ok = False
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
                d = json.loads(r.read().decode())
            res = d['chart']['result'][0]; q = res['indicators']['quote'][0]; ts = res.get('timestamp') or []
            tz = res['meta'].get('gmtoffset', 0)
            nm = s.replace('^', '').replace('=', '_')
            for i, t in enumerate(ts):
                c = q['close'][i]
                if c is None: continue
                day = dt.datetime.fromtimestamp(t + tz, dt.timezone.utc).strftime('%Y-%m-%d')
                rows.append((nm, day, q['open'][i], q['high'][i], q['low'][i], c, q['volume'][i] or 0))
            ok = True; break
        except Exception as e:
            time.sleep(1 + a)
    if not ok: bad.append(s)
    time.sleep(0.2)
with open('merged_yahoo.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['sym', 'date', 'o', 'h', 'l', 'c', 'v']); w.writerows(rows)
print(len(rows), 'rows;', len(SYMS) - len(bad), 'of', len(SYMS), 'symbols ok; failed:', bad)
sys.exit(0 if len(bad) < len(SYMS) / 3 else 1)
