from lib.helpers import heaviside_step
import numpy as np

def population(t: int, n0: float, sr: float, m: float, ph: list, doc: list, final_doc: int):
    doc = np.array(doc)
    ph = np.array(ph)
    
    partial_harvest_at_t = ph * heaviside_step(t - doc)

    if t >= final_doc:
        partial_harvest_at_t = np.append(
            partial_harvest_at_t, 
            (sr - ph.sum()) * heaviside_step(t - final_doc)
        )

    result = n0 * (np.exp(-m * t) - partial_harvest_at_t.sum())
    return result

def population_v2(t, n0: float, sr: float, m: float, ph: list, doc: list, final_doc: int, gamma: float, nh3_func, nh3_lim: float):
    doc = np.array(doc)
    ph = np.array(ph)
    
    partial_harvest_at_t = ph * heaviside_step(t - doc)

    if t >= final_doc:
        partial_harvest_at_t = np.append(
            partial_harvest_at_t, 
            (sr - ph.sum()) * heaviside_step(t - final_doc)
        )

    nh3_params = np.array([heaviside_step(nh3_func(i) - nh3_lim)  for i in range(t)])

    result = n0 * (np.exp(-m * t) - partial_harvest_at_t.sum() - gamma*nh3_params.sum())
    return result


def population_v3(t, n0: float, m: float, ph: list, doc: list, gamma: float, nh3_func, nh3_lim: float):
    """
    doc: the amount of partial harvest
    """
    doc = np.array(doc)
    ph = np.array(ph)
    
    partial_harvest_at_t = ph * heaviside_step(t - doc)

    nh3_params = np.array([heaviside_step(nh3_func(i) - nh3_lim)  for i in range(t)])

    result = (n0 * (np.exp(-m * t) - gamma*nh3_params.sum())) - partial_harvest_at_t.sum()
    
    return result

def harvested_population(t, n0: float, m: float, ph: list, doc: list, final_doc: int, gamma: float, nh3_func, nh3_lim: float):
    doc = np.array(doc)
    ph = np.array(ph)

    partial_harvest_at_t = ph * heaviside_step(t - doc)

    try:
        idx = int(np.where(doc == t)[0])
        partial_harvest_at_t = partial_harvest_at_t[idx]
    except:
        partial_harvest_at_t = 0

    if (t+1) == final_doc: # t+1 because we use t from index of list for the looping
        Nt = population_v3(t, n0, m, ph, doc, gamma, nh3_func, nh3_lim)
        return partial_harvest_at_t + Nt
    else:
        return partial_harvest_at_t

def harvested_biomass(t: float, wt: float, n0: float, m: float, ph: list, doc: list, final_doc: int, gamma: float, nh3_func, nh3_lim: float):
    """
    wt: list of weight at doc of partial harvest
    n0: initial
    """
    doc = np.array(doc)
    ph = np.array(ph)

    bio_harvest_at_t = ph * heaviside_step(t - doc) * wt

    try:
        idx = int(np.where(doc == t)[0])
        bio_harvest_at_t = bio_harvest_at_t[idx]
    except:
        bio_harvest_at_t = 0

    if (t+1) == final_doc:
        Nt = population_v3(t, n0, m, ph, doc, gamma, nh3_func, nh3_lim)
        return bio_harvest_at_t + Nt * wt
    else:
        return bio_harvest_at_t

def pond_remaining_biomass(t: int, wt: float, n0: float, m: float, ph: list, doc: list, gamma: float, nh3_func, nh3_lim: float):
    Nt = population_v3(t, n0, m, ph, doc, gamma, nh3_func, nh3_lim)
    return wt * Nt
