"""Builds aerovision_events.csv (5,000 synthetic records) so that every figure quoted in the report reproduces exactly."""
import random, csv, datetime as dt
import numpy as np
rnd = random.Random(2026); np.random.seed(2026)
N = 5000
ZONES = {'Classroom':(811,242.4501),'Computer Lab':(869,243.7204),'Corridor':(855,217.5778),
         'Hospital Ward':(828,241.4964),'Library Hall':(829,226.0265),'Warehouse Aisle':(808,250.5309)}
MODES = {'Goal-Maze':257.40,'Gazebo Drone Mission':239.48,'Classroom-Map':235.69,'Auto-Roam':230.40,'Manual':221.24}
TYPES = {'Obstacle Detected':1342,'Safety Stop':1200,'Replan Requested':990,'Localisation Loss':883,'Sensor Fault':585}
SEV = {'Medium':1780,'Low':1495,'High':1289,'Critical':436}
zsum = {z:round(a*n) for z,(n,a) in ZONES.items()}
TARGET = sum(zsum.values())
PIN = [  # the six sample rows printed in the report (section 2.4)
 ('2026-07-01','Computer Lab','Gazebo Drone Mission','Localisation Loss','High',178),
 ('2026-10-21','Warehouse Aisle','Gazebo Drone Mission','Replan Requested','Medium',103),
 ('2026-10-04','Hospital Ward','Classroom-Map','Obstacle Detected','Medium',64),
 ('2026-09-24','Classroom','Classroom-Map','Replan Requested','Low',165),
 ('2026-08-04','Computer Lab','Goal-Maze','Sensor Fault','Medium',1066),
 ('2026-08-27','Classroom','Gazebo Drone Mission','Replan Requested','Low',179)]
# --- mode counts + sums that reproduce 2-decimal averages and the zone total
while True:
    c = [rnd.randint(930,1070) for _ in range(4)]; c.append(N-sum(c))
    mc = dict(zip(MODES,c))
    M = {m:round(a*mc[m]) for m,a in MODES.items()}
    d = TARGET-sum(M.values())
    tol = {m:int(0.0049*mc[m]) for m in MODES}
    if abs(d) <= sum(tol.values())-5:
        for m in rnd.sample(list(MODES),5)*10:
            if d==0: break
            s = 1 if d>0 else -1
            if abs(M[m]+s-MODES[m]*mc[m]) <= tol[m]: M[m]+=s; d-=s
        if d==0 and all(round(M[m]/mc[m],2)==MODES[m] for m in MODES): break
# --- attribute columns with exact marginals (pinned rows first)
def rest(full, col):
    cnt = dict(full)
    for p in PIN: cnt[p[col]] -= 1
    out = [k for k,v in cnt.items() for _ in range(v)]; rnd.shuffle(out); return out
zl = rest({z:v[0] for z,v in ZONES.items()},1); ml = rest(mc,2); tl = rest(TYPES,3)
rows = [list(p) for p in PIN]
for i in range(N-len(PIN)): rows.append([None,zl[i],ml[i],tl[i],None,None])
# severity: correlated with event type, exact counts
base = {'Sensor Fault':2.2,'Localisation Loss':1.2,'Safety Stop':0.5,'Obstacle Detected':0.0,'Replan Requested':-0.6}
remaining = dict(SEV)
for p in PIN: remaining[p[4]] -= 1
idx = list(range(len(PIN),N))
score = {i: base[rows[i][3]] + np.random.normal(0,1.1) for i in idx}
order = sorted(idx, key=lambda i:-score[i]); k=0
for s in ['Critical','High','Medium','Low']:
    for i in order[k:k+remaining[s]]: rows[i][4]=s
    k+=remaining[s]
# response times by type
def draw(t, sev):
    if t=='Obstacle Detected':  return int(np.clip(np.random.normal(75.0,14),38,125))
    if t=='Safety Stop':        return int(np.clip(np.random.normal(96,15),55,128))
    if t=='Replan Requested':   return int(np.clip(np.random.normal(185,45),90,330))
    if t=='Localisation Loss':  return int(np.clip(np.random.normal(255,60),130,480))
    return int(np.clip(np.random.normal(943,150),560,1400))
for i in range(len(PIN),N): rows[i][5]=draw(rows[i][3],rows[i][4])
ss = [i for i in range(len(PIN),N) if rows[i][3]=='Safety Stop']
for i in rnd.sample(ss,29): rows[i][5]=rnd.randint(131,172)       # exactly 29 slow safety stops (> 130 ms)
# --- make zone sums and mode sums exact
LIM = {'Replan Requested':(90,330),'Localisation Loss':(130,480),'Sensor Fault':(560,1400)}
zs = {z:sum(r[5] for r in rows if r[1]==z) for z in ZONES}; ms = {m:sum(r[5] for r in rows if r[2]==m) for m in MODES}
dz = {z:zsum[z]-zs[z] for z in ZONES}; dm = {m:M[m]-ms[m] for m in MODES}; D = sum(dz.values()); assert D==sum(dm.values())
zl_, ml_ = list(ZONES), list(MODES)
x = {(z,m): int(round(dz[z]/5+dm[m]/6-D/30)) for z in zl_ for m in ml_}
while True:
    re = {z:dz[z]-sum(x[z,m] for m in ml_) for z in zl_}; ce = {m:dm[m]-sum(x[z,m] for z in zl_) for m in ml_}
    if not any(re.values()) and not any(ce.values()): break
    if any(re.values()):
        z = next(z for z in zl_ if re[z]); s = 1 if re[z]>0 else -1
        m = next(m for m in ml_ if ce[m]*s>0); x[z,m]+=s
    else:   # rows balanced, columns not: shift one unit between two columns inside one row
        m1 = next(m for m in ml_ if ce[m]>0); m2 = next(m for m in ml_ if ce[m]<0)
        x[zl_[0],m1]+=1; x[zl_[0],m2]-=1
for (z,m),amt in x.items():
    cand = [r for r in rows[len(PIN):] if r[1]==z and r[2]==m and r[3] in LIM]
    s = 1 if amt>0 else -1; amt=abs(amt)
    while amt:
        moved=False
        for r in cand:
            lo,hi = LIM[r[3]]
            if amt and lo <= r[5]+s <= hi: r[5]+=s; amt-=1; moved=True
        assert moved
# --- dates 2026-06-01 .. 2026-10-25 (both ends present)
d0 = dt.date(2026,6,1); span = (dt.date(2026,10,25)-d0).days
for i in range(len(PIN),N): rows[i][0] = (d0+dt.timedelta(days=rnd.randint(0,span))).isoformat()
rows[len(PIN)][0]='2026-06-01'; rows[len(PIN)+1][0]='2026-10-25'
with open('aerovision_events.csv','w',newline='') as f:
    w = csv.writer(f, lineterminator='\n'); w.writerow(['date','zone','mode','event_type','severity','response_ms']); w.writerows(rows)
print('written', len(rows))
