#!/usr/bin/env python3
"""Create season tables using publicly accessible football-data.co.uk EPL CSV feeds.
Check source terms and redistribution rights before public launch.
"""
import csv, io, json, urllib.request, datetime, pathlib, time
from collections import defaultdict
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'data'/'seasons.json'
YEAR=datetime.datetime.now(datetime.timezone.utc).year
# football-data.co.uk accepts season YY pairs, e.g. 0910, 2526.
SEASONS=list(range(2009, max(2026,YEAR)+1))
CITY='Man City'
# Team normalization for source formatting drift.
ALIASES={'Man City':'Manchester City','Man United':'Manchester United','Nottm Forest':'Nottingham Forest','Wolves':'Wolverhampton Wanderers','West Brom':'West Bromwich Albion','Sheffield United':'Sheffield United','Leicester':'Leicester City','Norwich':'Norwich City','Swansea':'Swansea City','Cardiff':'Cardiff City','Hull':'Hull City','Stoke':'Stoke City','QPR':'Queens Park Rangers','Newcastle':'Newcastle United','Brighton':'Brighton & Hove Albion','Tottenham':'Tottenham Hotspur','West Ham':'West Ham United','Bournemouth':'Bournemouth','Leeds':'Leeds United','Sunderland':'Sunderland','Blackpool':'Blackpool','Bolton':'Bolton Wanderers','Birmingham':'Birmingham City','Wigan':'Wigan Athletic','Aston Villa':'Aston Villa','Burnley':'Burnley','Fulham':'Fulham','Crystal Palace':'Crystal Palace','Ipswich':'Ipswich Town','Coventry':'Coventry City','Huddersfield':'Huddersfield Town'}
# Exceptional points deductions in the official standings, entered only when independently confirmed.
# This comparison is otherwise results-based; deductions only apply to official, not counterfactual, tables.
# Avoid inventing adjustments for new seasons. Historical fixtures alone cannot establish official deductions.
DEDUCTIONS={'2009/10':{'Portsmouth':9},'2023/24':{'Everton':8,'Nottingham Forest':4}}

def fetch(year):
    suffix=f'{year%100:02d}{(year+1)%100:02d}'
    url=f'https://www.football-data.co.uk/mmz4281/{suffix}/E0.csv'
    req=urllib.request.Request(url,headers={'User-Agent':'CitylessLeague/1.0 (community project)'})
    with urllib.request.urlopen(req,timeout=25) as r: raw=r.read()
    return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig',errors='replace')))),url

def make_table(matches,exclude_city=False,adjustments=None):
    table=defaultdict(lambda:dict(P=0,W=0,D=0,L=0,GF=0,GA=0,GD=0,Pts=0))
    for m in matches:
        h,a=m['home'],m['away']
        if exclude_city and ('Manchester City' in (h,a)): continue
        hg,ag=m['hg'],m['ag']
        for team,gf,ga in ((h,hg,ag),(a,ag,hg)):
            t=table[team];t['P']+=1;t['GF']+=gf;t['GA']+=ga
            if gf>ga:t['W']+=1;t['Pts']+=3
            elif gf==ga:t['D']+=1;t['Pts']+=1
            else:t['L']+=1
    rows=[]
    for name,st in table.items():
        st['GD']=st['GF']-st['GA']; st['Pts']-= (adjustments or {}).get(name,0)
        rows.append({'team':name,**st})
    # English league ranking: points, GD, GF; tied after that may require special tie-break rules.
    rows.sort(key=lambda x:(-x['Pts'],-x['GD'],-x['GF'],x['team']))
    for idx,t in enumerate(rows): t['pos']=idx+1
    return rows

def season(year):
    label=f'{year}/{str((year+1)%100).zfill(2)}';raw,url=fetch(year);games=[]
    for r in raw:
        if not all((r.get(k) or '').strip() for k in ('HomeTeam','AwayTeam','FTHG','FTAG','FTR')):continue
        try:hg,ag=int(r['FTHG']),int(r['FTAG'])
        except ValueError:continue
        h=ALIASES.get(r['HomeTeam'],r['HomeTeam']);a=ALIASES.get(r['AwayTeam'],r['AwayTeam'])
        games.append({'home':h,'away':a,'hg':hg,'ag':ag,'date':r.get('Date','')})
    # Include clubs with 0 games if fixtures have not begun? CSV commonly contains future schedule teams.
    official=make_table(games,adjustments=DEDUCTIONS.get(label,{}))
    alternative=make_table(games,exclude_city=True)
    by_off={r['team']:r for r in official};by_alt={r['team']:r for r in alternative}
    impact=[]
    for team,r in by_alt.items():
        old=by_off.get(team)
        if old:
            impact.append({'team':team,'officialPos':old['pos'],'altPos':r['pos'],'positionGain':old['pos']-r['pos'],'pointsRemoved':old['Pts']-r['Pts']})
    impact.sort(key=lambda x:(-x['positionGain'],-x['pointsRemoved'],x['team']))
    finished=len(games)>=380
    return {'season':label,'source':url,'matchCount':len(games),'complete':finished,'official':official,'alternative':alternative,'impact':impact,'matches':games,'adjustments':DEDUCTIONS.get(label,{})}

def main():
    old={}
    if OUT.exists():
        try:old={s['season']:s for s in json.loads(OUT.read_text())['seasons']}
        except (KeyError,ValueError): pass
    result=[]
    for y in SEASONS:
        label=f'{y}/{str((y+1)%100).zfill(2)}'
        try:
            data=season(y)
            if data['matchCount'] == 0:raise RuntimeError('No completed matches available')
            print(label,data['matchCount'],'completed fixtures')
            result.append(data)
        except Exception as exc:
            print('WARNING',label,str(exc))
            if label in old:result.append(old[label])
        time.sleep(.12)
    result.sort(key=lambda s:s['season'],reverse=True)
    if not result:raise SystemExit('No season data available; refusing to overwrite data file.')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'football-data.co.uk','seasons':result},separators=(',',':')))
    print('Wrote',OUT)
if __name__=='__main__':main()
