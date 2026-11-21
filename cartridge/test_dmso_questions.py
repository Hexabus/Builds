import sys
sys.path.insert(0,'/home/claude/cartridge')
from cartridge import store
db=store.open_db('/tmp/dmsopack/pack.db')
# (question, regex that must appear in the correct passage)
T=[("who discovered DMSO and when","Saytze.{0,3}f.*1866|1866"),
("what percent of cells survive freezing with DMSO","85\s+percent\s+of\s+cells"),
("what containers should DMSO be stored in glass or plastic","go with glass"),
("why does DMSO make my skin leathery","leathery"),
("what is pharmaceutical grade DMSO purity","99.995"),
("why does DMSO cause a garlic smell on the breath","garlic,\s+onions,\s+or\s+oysters"),
("what dilution percent is recommended for delicate skin","60% Topical percentage"),
("can I wear rubber gloves when applying DMSO","dissolve\s+these\s+materials"),
("how long to wait before getting dressed after applying DMSO","Wait 20 minutes"),
("what solution did the author use to treat skin mites","diatomaceous earth"),
]
import re
ok1=ok3=0
for q,pat in T:
    hits=store.search(db,q,k=4)
    rank=next((i+1 for i,h in enumerate(hits) if re.search(pat,h[3],re.S|re.I)),None)
    ok1+= rank==1; ok3+= bool(rank)
    print(rank, '|', q)
print(f"top1 {ok1}/{len(T)}  in-top4 {ok3}/{len(T)}")
