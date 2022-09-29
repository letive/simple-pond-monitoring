import numpy as np
from scipy.interpolate import CubicSpline

def heaviside_step(x):
    return np.heaviside([x], 1)[0]


def normal_trapezoidal(m, suitable_min, suitable_max, optimal_min, optimal_max):
    """
    m: value in t
    """
    if np.isnan(m):
        ret = 0.25
    elif (m < suitable_min) or (m > suitable_max):
        ret = 0
    else:
        ret = min(
            ((m - suitable_min) / (optimal_min - suitable_min),
                1,
                (suitable_max - m) / (suitable_max - optimal_max),
            ))

    return ret


def left_trapezoidal(m, suitable_min, suitable_max, optimal_max):
    """
    m: value in t
    """
    if np.isnan(m):
        ret = 0.25
    elif (m < suitable_min) or (m > suitable_max):
        ret = 0
    else:
        ret = min((1, (suitable_max - m) / (suitable_max - optimal_max)))
    
    return ret

def right_trapezoidal(m, suitable_min, optimal_min):
    if np.isnan(m):
        ret = 0.25
    elif (m < suitable_min):
        ret = 0
    elif (m >= optimal_min):
        ret = 1
    else:
        ret = (m - suitable_min) / (optimal_min - suitable_min)
    
    return ret

def get_cycle_data(index, t, df):
    # index and t must be at the same row
    if t < index:
        start_index = index - t + 1
    else:
        start_index = index - index
    
    data = df.loc[start_index:index]
    if data.shape[0] == 1:
        data = df.loc[start_index:index+1]

    return data

def generate_interpolate_function(df, col_doc, col_function):
    f = CubicSpline(df[col_doc], df[col_function])
    return f

def generate_spline_function(df, col_doc, condition, col_function="Temp", biochem_type="temperature"):
    # col_function example is temperature
    # condition (suitable_min, optimal_min, optimal_max, suitable_max)
    if biochem_type == "temperature":
        data = [normal_trapezoidal(x, condition[0], condition[3], condition[1], condition[2]) for x in df[col_function].values]
    elif biochem_type == "nh4":
        data = [left_trapezoidal(x, condition[0], condition[3], condition[2]) for x in df[col_function].values]
    else:
        data = [normal_trapezoidal(x, condition[0], condition[3], condition[1], condition[2]) for x in df[col_function].values]

    f = CubicSpline(df[col_doc].values, data)
    return f

def integrate_function(t, function, condition, kind):
    """
    t: the time value
    function: interpolation function
    condition: list of condition
    type: type of function. ex: temperature
    """
    if (kind == "temperature"):
        return normal_trapezoidal(function(t), condition[0], condition[3], condition[1], condition[2])
    elif (kind == "do"):
        return right_trapezoidal(function(t), condition[0], condition[1])
    elif kind == "nh4":
        return left_trapezoidal(function(t), condition[0], condition[3], condition[2])

def get_cycle_range(df, col_doc="DOC"):
    list_index = df[df[col_doc] == 1].index
    cycles = []
    for index, value in enumerate(list_index):
        if value != list_index[-1]:
            cycles.append([value, list_index[index+1]])
        else:
            cycles.append([value])

    return cycles

def get_index_array(data):
    index = []
    for i, j in enumerate(data):
        if (i == 0) & (j[0] == 1):
            cycle = [i]
        elif (j[0] == 1):
            cycle.append(i)
            index.append(cycle)
            cycle = [i]
        else:
            pass
    index.append(cycle)
    return index

def generate_multicycle_interpolation(data):
    index = get_index_array(data)
    functions = []
    
    for i in index:
        if len(i) != 1:
            X = data[i[0]:i[1]]
            
        else:
            X = data[i[0]:]

        f_temp = CubicSpline(X[:, 0], X[:, 1])
        f_nh3 = CubicSpline(X[:, 0], X[:, 2])
        f_do = CubicSpline(X[:, 0], X[:, 3])

        functions.append([f_temp, f_nh3, f_do])
    
    return functions, index