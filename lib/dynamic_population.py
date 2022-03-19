import numpy as np

def random_harvest(n, value):
    lower_bound = round(0.1*round(value))
    x = np.random.randint(lower_bound, round(value), size=(n,))
    while sum(x) != round(value):
        x = np.random.randint(lower_bound, round(value), size=(n,))
    
    return x

def random_t_harvest(n, max=120, lower_bound=55):
    x = np.sort(np.random.randint(lower_bound, max, size=(n,)))
    return x


def mortality_rate(sr, T):
    if T == 0:
        return 0
    else:
        return -1*np.log10(sr)/T
        

def mortality_rate(sr, T):
    if T == 0:
        return 0
    else:
        return -1*np.log10(sr)/T
        

def dynamic_poulation(n, n0, sr, T):
    partial_harvest = random_harvest(n, n0*sr)
    harvest_time = random_t_harvest(n)
    m = mortality_rate(sr, T)
    nt = []
    for t in range(harvest_time[-1]+1):
        if t == T+1:
            break
        else:
            partial = []
            for x in enumerate(harvest_time):
                if t >= x[1]:
                    partial.append(partial_harvest[x[0]]/n0)
            nt.append(n0*(np.exp(-1*m*t - sum(partial))))

    if harvest_time[-1] < T:
        index = list(range(harvest_time[-1]+1))
    else:
        index = list(range(T+1))
    return nt, index, partial_harvest, harvest_time
