# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import math
from pdm import w_prime_balance
import matplotlib.pyplot as plt
#from pdm import d_prime_balance
from athletic_pandas.models import Athlete, WorkoutDataFrame



def interval_speed(duration, cs,d_prime):
    return d_prime/duration + cs

def d_prime_balance_froncioni_skiba_clarke(speed, cs, d_prime):
    """
    Source:
    Skiba, P. F., Fulford, J., Clarke, D. C., Vanhatalo, A., & Jones, A. M. (2015). Intramuscular determinants of the ability to recover work capacity above critical speed. European journal of applied physiology, 115(4), 703-713.
    """
    last=d_prime
    d_prime_balance = []

    for s in speed:
        speedDif=cs-s
        if speedDif > 0:
            new = last + (speedDif) * (d_prime - last) / d_prime
        else:
            new = last + (speedDif)

        d_prime_balance.append(new)
        last = new

    
    return d_prime_balance

# First create an artificial workout
artificial_power = 60*[100] + 60*[400] + 30*[100] + 60*[400] + 60*[100]
datetime = pd.to_datetime(list(range(len(artificial_power))), unit="s")
data = pd.DataFrame(dict(power=artificial_power), index=datetime)

# Define the model coefficients
cp = 300
w_prime = 20000

cs= 6
d_prime=300




data["W'balance"] = w_prime_balance.w_prime_balance(data["power"], cp=cp, w_prime=w_prime).to_list()
data["W'balance"].plot();

intDuration=8*60
#speed that will completely deplete Dprime in 8 min

intSpeed=interval_speed(intDuration, cs,d_prime)
#round down to nearest .5m/s
base=0.5;
intSpeed=base*math.floor(intSpeed/base)
IntSpeedDif=intSpeed-cs
Ddep1=d_prime-IntSpeedDif*intDuration


recSpeed=base*math.floor(cs*0.8/base)
recSpeedDif=recSpeed-cs
recTime=180;
Drec1=d_prime+(Ddep1-d_prime)*math.exp(recSpeedDif*recTime/d_prime)
#time to deplete second interval
base=30;
tdep=(Drec1-0)/(intSpeed-cs)

intDuration2=base*math.floor(tdep/base)
Ddep2=Drec1-IntSpeedDif*intDuration2
Drec2=d_prime+(Ddep2-d_prime)*math.exp(recSpeedDif*recTime/d_prime)
#time to deplete third interval

tdep=(Drec2-0)/(intSpeed-cs)
intDuration3=base*math.floor(tdep/base)
Ddep3=Drec2-IntSpeedDif*intDuration3
Drec3=d_prime+(Ddep3-d_prime)*math.exp(recSpeedDif*recTime/d_prime)

# create an artificial workout
artificial_speed =( intDuration*[intSpeed] + recTime*[recSpeed] + intDuration2*[intSpeed] + recTime*[recSpeed] + intDuration3*[intSpeed]  + recTime*[recSpeed])
datetime = pd.to_datetime(list(range(len(artificial_speed))), unit="s")

data = pd.DataFrame(dict(speed=artificial_speed))

fig_power = data.speed.plot.line()
fig_power.set_ylabel('speed (m/s)')
fig_power.set_xlabel('time (seconds)');

DP=d_prime_balance_froncioni_skiba_clarke(artificial_speed, cs, d_prime)

data2 = pd.DataFrame(dict(Balance=DP))

fig_power2 = data2.Balance.plot(secondary_y=True,kind="line")
fig_power2.set_ylabel('Distance (m)')
fig_power2.set_xlabel('time (seconds)');


