# Score the candidate phases on dimensions aligned to the stated research goal.
# Raw measurements only; the normalisation is linear against the best observed value.
P = {  # phase: raw measurements
 "Phase 3":  dict(pairs=2.5, ontopic=None, refs=8.5,  ft=0,  contra=0, calib=0, safe=0),
 "Phase 4":  dict(pairs=2.5, ontopic=22,   refs=22.6, ft=0,  contra=0, calib=0, safe=1),
 "Phase 9":  dict(pairs=2.5, ontopic=54,   refs=22.5, ft=6,  contra=0, calib=0, safe=0),
 "Phase 9L": dict(pairs=11.6,ontopic=52,   refs=23.4, ft=9,  contra=2, calib=3, safe=0),
 "Phase 11": dict(pairs=9.6, ontopic=65,   refs=13.0, ft=6,  contra=2, calib=4, safe=1),
 "Phase 12": dict(pairs=9.1, ontopic=63,   refs=13.7, ft=12, contra=1.5,calib=3, safe=1),
 "Phase 13": dict(pairs=14.5,ontopic=49,   refs=23.8, ft=17, contra=4, calib=3, safe=0),
}
# contra: 0 none, 2 untyped flags, 1.5 untyped+inflated by mechanistic, 4 typed+comparability-aware
# calib : 0 none, 3 rule-based but unvalidated on that config, 4 rule-based + benchmarked
DIMS = ["pairs","ontopic","refs","ft","contra","calib","safe"]
MAXV = {d: max(v[d] for v in P.values() if v[d] is not None) for d in DIMS}
def norm(name, d):
    v = P[name][d]
    if v is None: return 0.0
    return 5.0 * v / MAXV[d] if MAXV[d] else 0.0

W_GOAL = dict(contra=.30, pairs=.20, calib=.15, ft=.15, ontopic=.10, refs=.05, safe=.05)
W_CLIN = dict(safe=.30, ontopic=.25, calib=.20, contra=.15, refs=.05, pairs=.03, ft=.02)

print("%-10s %6s %7s %6s %6s %7s %6s %5s | %6s %6s" %
      ("phase","recall","precis","prov","depth","contra","calib","safe","GOAL","CLIN"))
print("-"*84)
rows=[]
for n in P:
    s={d:norm(n,d) for d in DIMS}
    g=sum(W_GOAL[d]*s[d] for d in DIMS); c=sum(W_CLIN[d]*s[d] for d in DIMS)
    rows.append((n,s,g,c))
for n,s,g,c in rows:
    print("%-10s %6.1f %7.1f %6.1f %6.1f %7.1f %6.1f %5.1f | %6.2f %6.2f" %
          (n,s["pairs"],s["ontopic"],s["refs"],s["ft"],s["contra"],s["calib"],s["safe"],g,c))
print()
print("ranked by RESEARCH GOAL  :", " > ".join(n for n,_,_,_ in sorted(rows,key=lambda r:-r[2])))
print("ranked by CLINICAL SAFETY:", " > ".join(n for n,_,_,_ in sorted(rows,key=lambda r:-r[3])))
