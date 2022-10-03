from scipy.interpolate import interp1d
import pandas as pd

def get_feed_point(excess_percent: float):
    """feed point per tray"""
    if excess_percent == 0:
        point = 3
    elif excess_percent <= 10:
        point = 1
    else:
        point = 0
    
    return point

def adjusted_leftover_fr(fr: float, excess_feed_trays: list):
    """ 
    This function is about adjustment amount of feeding regarded on excess in each trays for every feeding.
    This function is better to use in each feeding time. 

    fr: feed ratio for each section of a day
    exess_feed_trays: excess of feeding
    """

    feed_points = sum([get_feed_point(i) for i in excess_feed_trays])

    ## see get_feed_point function to know more the algorithm

    if feed_points >= 15:
        adjusted_point = 10
    elif (feed_points < 15) and (feed_points >= 11):
        adjusted_point = 5
    elif (feed_points < 11) and (feed_points >= 8):
        adjusted_point = 0
    elif (feed_points < 8) and (feed_points >= 4):
        adjusted_point = -5
    else:
        adjusted_point = -10
    
    return fr + adjusted_point


def get_rating_function(df: pd.DataFrame):
    """
    This function related to the data which has format like in data/feed_table_temp.csv.
    Output of this function is several extrapolate functions.
    """
    f_15_19 = interp1d(df["ABW"], df["15-19"], fill_value="extrapolate")
    f_19_21 = interp1d(df["ABW"], df["19-21"], fill_value="extrapolate")
    f_21_24 = interp1d(df["ABW"], df["21-24"], fill_value="extrapolate")
    f_24_28 = interp1d(df["ABW"], df["24-28"], fill_value="extrapolate")
    f_28_32 = interp1d(df["ABW"], df["28-32"], fill_value="extrapolate")
    f_33 = interp1d(df["ABW"], df["33"], fill_value="extrapolate")
    f_34 = interp1d(df["ABW"], df["34"], fill_value="extrapolate")
    return f_15_19, f_19_21, f_21_24, f_24_28, f_28_32, f_33, f_34

    
def adjusted_abw_temp_fr(abw: float, temp: float, funcs: list):
    """ 
    This function is about adjustment amount of feeding regarded on abw and temperature in a cultivation.

    abw: average body weight or maybe we used to call this only weight
    fr: feeding ratio
    temp: temperature this time
    funcs: list of interpolation function that represented to abw and the temperature. see the get_ration_function function to know more to this function. the order of this function follows the output of that function.
    """


    if (temp < 15) or (temp > 34):
        new_fr = 0
    elif (temp >= 15) and (temp < 19):
        new_fr = funcs[0](abw)
    elif (temp >= 19) and (temp < 21):
        new_fr = funcs[1](abw)
    elif (temp >= 21) and (temp < 24):
        new_fr = funcs[2](abw)
    elif (temp >= 24) and (temp < 28):
        new_fr = funcs[3](abw)
    elif (temp >= 28) and (temp < 32):
        new_fr = funcs[4](abw)
    elif (temp >= 32) and (temp < 33):
        new_fr = funcs[5](abw)
    elif (temp >= 33) and (temp < 34):
        new_fr = funcs[6](abw)
    else:
        new_fr = funcs[7](abw)

    return new_fr


##############################
# Combined Functions
##############################

def init_time_adjustment(no_feeding: int, abw: float, temp: float, funcs: list, t=1):
    if t == 1:
        next_feed_fr = adjusted_abw_temp_fr(abw, temp, funcs)
        feedtime_fr_adjusted = [next_feed_fr/no_feeding] * no_feeding
        return next_feed_fr, feedtime_fr_adjusted

def actual_time_adjustment(t: int, no_feeding: int, feedtime_fr_before_adjusted: list, excess: list):
    if t > 1:
        fr = feedtime_fr_before_adjusted[t-2] # t-1 is current
        next_feed_fr = adjusted_leftover_fr(fr, excess)
        feedtime_fr_adjusted = feedtime_fr_before_adjusted[:t] + [[next_feed_fr] * (no_feeding - t)]

        return next_feed_fr, feedtime_fr_adjusted
        
def update_fr(df: pd.DataFrame, trays: pd.DataFrame, f, number_of_feed_time=4, col_doc="DOC", col_fr="formula_1"):
    """ 
    df: Dataframe of the origin data FR which contains minimumn DOC, Temp, and FR
    trays: Dataframe of the trays number
    number_of_feed_time: number of feeding
    col_doc: DOC columns that contains in df and trays. In this case, we use doc column is similar.
    col_fr: columns fr in dataframe df
    """
    df = df.copy()
    trays = trays.copy()
    
    DOCs = trays[col_doc].unique()
    df.index = df[col_doc]

    for i in DOCs:
        selected = trays.query("{} == {}".format(col_doc, i))

        abw = float(df.query("{} == {}".format(col_doc, i))["ABW"])
        temp = float(df.query("{} == {}".format(col_doc, i))["Temp"])

        total_times = selected.shape[0]
        if total_times <= number_of_feed_time:
            for j in range(total_times):
                if j+1:
                    next_feed_fr, feedtime_fr_adjusted = init_time_adjustment(number_of_feed_time, abw, temp, funcs=f)
                else:
                    selected = selected.filter(regex="tray_*")
                    excess = selected.loc[j].tolist()
                    next_feed_fr, feedtime_fr_adjusted = actual_time_adjustment(j + 1, number_of_feed_time, feedtime_fr_adjusted, excess)

            df.loc[i, col_fr] = sum(feedtime_fr_adjusted)

        else:
            no_trays = len(trays.filter(regex="tray_*").columns)
            next_feed_fr = float(df.query("{} == {}".format(col_doc, i))[col_fr])/number_of_feed_time/no_trays
            break

    return df, next_feed_fr
    
