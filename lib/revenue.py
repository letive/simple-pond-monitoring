from lib.partial_harvest import PartialHarvest
from lib.helpers import price_function, realize_counter
import numpy as np

def aggregation(t0, T, area, wn, w0, alpha, n0, sr, partial, doc, final_doc=120):

    revenue = []
    potential_revenue = []
    population = []
    biomassa = []
    wt = [] 

    m = -np.log(sr)/T

    f = price_function("data/fixed_price.csv")

    for t in range(0, T+1):
        obj = PartialHarvest(t0, t, wn, w0, alpha, n0, sr, m, partial, doc, final_doc=final_doc)

        population.append(obj.population()*area)
        biomassa.append(obj.biomassa()*area/1000)
        potential_revenue.append(obj.potential_revenue(f)*area)
        revenue.append(obj.realized_revenue(f)*area)
        wt.append(obj.wt())

    result = {
        "body_weight": wt,
        "population": population,
        "biomassa": biomassa,
        "potential_revenue": potential_revenue,
        "realized_revenue": revenue,
        "cumulative_revenue": np.cumsum(np.array(revenue)).tolist()
    }

    return result

