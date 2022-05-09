from lib.partial_harvest import PartialHarvest
from lib.helpers import price_function
import numpy as np

def aggregation(t0, T, area, wn, w0, alpha, n0, sr, partial1, partial2, partial3, 
            docpartial1, docpartial2, docpartial3, docfinal):

    m = -np.log(sr)/T
    revenue = []
    potential_revenue = []
    population = []
    biomassa = []
    wt = [] 

    f = price_function("data/fixed_price.csv")
    for t in range(0, T+1):
        obj = PartialHarvest(t0, t, wn, w0, alpha, n0, sr, [partial1, partial2, partial3], 
            [docpartial1, docpartial2, docpartial3], docfinal)

        population.append(obj.population()[-1]*area)
        biomassa.append(obj.biomassa()/1000 * area)
        potential_revenue.append(obj.potential_revenue(f))
        revenue.append(obj.realized_revenue(f))
        wt.append(obj.wt())
    
    revenue = np.cumsum(np.array(revenue)).tolist()
    result = {
        "body_weight": wt,
        "population": population,
        "biomassa": biomassa,
        "potential_revenue": potential_revenue,
        "realized_revenue": revenue
    }

    return result

