import numpy as np

def score(m, suitable_min, suitable_max, optimal_min, optimal_max, upper_limit):
    """
    m: value in t
    """
    if np.isnan(m):
        ret = 0.25
    elif m < suitable_min:
        ret = (m - suitable_min)/suitable_min # pasti akan return negatif
    elif m > suitable_max:
        ret = (m-suitable_max)/(suitable_max-upper_limit) # pasti akan return negatif
    else:
        ret = min(((m-suitable_min)/(optimal_min-suitable_min), 1, (suitable_max-m)/(suitable_max-optimal_max)))
        
    return ret

def score2(m, suitable_min, optimal_min):
    """
    m: value in t
    """
    if np.isnan(m):
        ret = 0.25
    elif m < suitable_min:
        ret = (m - suitable_min)/suitable_min # pasti akan return negatif
    else:
        ret = min(((m-suitable_min)/(optimal_min-suitable_min), 1))
        
    return ret


def score3(m, suitable_min, suitable_max, optimal_min, optimal_max, upper_limit):
    """
    m: value in t
    """
    if np.isnan(m):
        ret = 0.25
    elif m < suitable_min:
        ret = (m - suitable_min)/suitable_min # pasti akan return negatif
    elif m > suitable_max:
        ret = (m-suitable_max)/(suitable_max-upper_limit) # pasti akan return negatif
    else:
        # beda di (m-suitable_min)/(optimal_min-suitable_max)
        ret = min(((m-suitable_min)/(optimal_min-suitable_max), 1, (suitable_max-m)/(suitable_max-optimal_max)))
        
    return ret

def score4(m, suitable_min, suitable_max, optimal_min, optimal_max, upper_limit):
    """
    m: value in t
    """
    if np.isnan(m):
        ret = 0.25
    elif m < suitable_min:
        ret = (m - suitable_min)/suitable_min # pasti akan return negatif
    elif m > suitable_max:
        ret = (m-suitable_max)/(suitable_max-upper_limit) # pasti akan return negatif
    else:
        # berbeda di (m-suitable_min)/(suitable_min - optimal_min)
        ret = min(((m-suitable_min)/(suitable_min - optimal_min), 1, (suitable_max-m)/(suitable_max-optimal_max)))
        
    return ret

def data_scoring(morning, afternoon, suitable_min, suitable_max, optimal_min, optimal_max, limit, weight=1, score_type=1):
    """
    morning: salinities, ph, temperature data in the morning
    afternoon: salinities, ph, temperature data in the noon
    suittable_min: minimum suitable value of the trapezoidal function score
    suittable_max: maximum suitable value of the trapezoidal function score
    optimal_min: minimum optimal value of the trapezoidal function score
    optimal_max: maximum optimal value of the trapezoidal function score
    limit: upper limit of the trapezoidal function score
    """

    morning = np.array(morning)
    afternoon = np.array(afternoon)

    morning = morning.astype(float)
    afternoon = afternoon.astype(float)

    m_score = []
    a_score = []
    for x in enumerate(morning):
        if score_type == 1:
            m_score.append(score(x[1], suitable_min, suitable_max, optimal_min, optimal_max, limit))
            a_score.append(score(afternoon[x[0]], suitable_min, suitable_max, optimal_min, optimal_max, limit))
        elif score_type == 2:
            m_score.append(score2(x[1], suitable_min, optimal_min))
            a_score.append(score2(afternoon[x[0]], suitable_min, optimal_min))
        elif score_type == 3:
            m_score.append(score3(x[1], suitable_min, suitable_max, optimal_min, optimal_max, limit))
            a_score.append(score3(afternoon[x[0]], suitable_min, suitable_max, optimal_min, optimal_max, limit))
        else:
            m_score.append(score4(x[1], suitable_min, suitable_max, optimal_min, optimal_max, limit))
            a_score.append(score4(afternoon[x[0]], suitable_min, suitable_max, optimal_min, optimal_max, limit))

    return m_score, a_score, (weight*np.array(m_score)).tolist(), (weight*np.array(a_score)).tolist()


def single_data_scoring(data, suitable_min, suitable_max, optimal_min, optimal_max, limit, weight=1, score_type=1):
    """
    data: single data to be scored
    suittable_min: minimum suitable value of the trapezoidal function score
    suittable_max: maximum suitable value of the trapezoidal function score
    optimal_min: minimum optimal value of the trapezoidal function score
    optimal_max: maximum optimal value of the trapezoidal function score
    limit: upper limit of the trapezoidal function score
    """

    data = np.array(data)
    data = data.astype(float)

    data_score = []
    for x in data:
        if score_type == 1:
            data_score.append(score(x, suitable_min, suitable_max, optimal_min, optimal_max, limit))
        elif score_type == 2:
            data_score.append(score2(x, suitable_min, optimal_min))
        elif score_type == 3:
            data_score.append(score3(x, suitable_min, suitable_max, optimal_min, optimal_max, limit))
        else:
            data_score.append(score4(x, suitable_min, suitable_max, optimal_min, optimal_max, limit))

    return data_score, (weight*np.array(data_score)).tolist()




