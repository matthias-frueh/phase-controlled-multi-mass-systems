import time, numpy as np, vk_model as m, vk_sa as sa
for (p2,p3) in [(120,240),(35,116)]:
    s = sa.SA(p2,p3)
    t=time.time()
    R = s.run(-m.MG/m.K, 0.0, 0.0, 100)
    st = sa.stats(R, 50, 100)
    print(p2,p3, f'{time.time()-t:.1f}s', {k: round(v,6) for k,v in st.items()}, sa.period(R), s.n_ev)
