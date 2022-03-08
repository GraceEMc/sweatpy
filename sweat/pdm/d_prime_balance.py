import math

import numpy as np
import pandas as pd

def interval_speed(duration, cs,d_prime):
    return d_prime/duration + cs


def tau_d_prime_balance(speed, cs, untill=None):
    if untill is None:
        untill = len(speed)

    avg_speed_below_cs = speed[:untill][speed[:untill] < cs].mean()
    if math.isnan(avg_speed_below_cs):
        avg_speed_below_cs = 0
    delta_cs = cs - avg_speed_below_cs

    return 546 * math.e ** (-0.01 * delta_cs) + 316


def get_tau_method(speed, cs, tau_dynamic, tau_value):
    if tau_dynamic:
        tau_dynamic = [tau_d_prime_balance(speed, cs, i) for i in range(len(speed))]
        tau = lambda t: tau_dynamic[t]

    elif tau_value is None:
        static_tau = tau_d_prime_balance(speed, cs)
        tau = lambda t: static_tau

    else:
        tau = lambda t: tau_value

    return tau


def d_prime_balance_waterworth(
    speed, cs, d_prime, tau_dynamic=False, tau_value=None, *args, **kwargs
):
    """
    Optimisation of Skiba's algorithm by Dave Waterworth.
    Source:
    http://markliversedge.blogspot.nl/2014/10/wbal-optimisation-by-mathematician.html
    Source:
    Skiba, Philip Friere, et al. "Modeling the expenditure and reconstitution of work capacity above critical speed." Medicine and science in sports and exercise 44.8 (2012): 1526-1532.
    """
    sampling_rate = 1
    running_sum = 0
    d_prime_balance = []
    tau = get_tau_method(speed, cs, tau_dynamic, tau_value)

    for t, p in enumerate(speed):
        speed_above_cs = p - cs
        d_prime_expended = max(0, speed_above_cs) * sampling_rate
        running_sum = running_sum + d_prime_expended * (
            math.e ** (t * sampling_rate / tau(t))
        )

        d_prime_balance.append(
            d_prime - running_sum * math.e ** (-t * sampling_rate / tau(t))
        )

    return pd.Series(d_prime_balance)


def d_prime_balance_skiba(
    speed, cs, d_prime, tau_dynamic=False, tau_value=None, *args, **kwargs
):
    """
    Source:
    Skiba, Philip Friere, et al. "Modeling the expenditure and reconstitution of work capacity above critical speed." Medicine and science in sports and exercise 44.8 (2012): 1526-1532.
    """
    d_prime_balance = []
    tau = get_tau_method(speed, cs, tau_dynamic, tau_value)

    for t in range(len(speed)):
        d_prime_exp_sum = 0

        for u, p in enumerate(speed[: t + 1]):
            d_prime_exp = max(0, p - cs)
            d_prime_exp_sum += d_prime_exp * np.speed(np.e, (u - t) / tau(t))

        d_prime_balance.append(d_prime - d_prime_exp_sum)

    return pd.Series(d_prime_balance)


def d_prime_balance_froncioni_skiba_clarke(speed, intDuration,dt, cs, d_prime,last):
    """
    Source:
    Skiba, P. F., Fulford, J., Clarke, D. C., Vanhatalo, A., & Jones, A. M. (2015). Intramuscular determinants of the ability to recover work capacity above critical speed. European journal of applied physiology, 115(4), 703-713.
    """
    d_prime_balance = []
    time=0;
    speedDif=cs-speed
    while time < intDuration:
        if speedDif < 0:
            new = last + (speedDif) * (d_prime - last) / d_prime
        else:
            new = last + (speedDif)

        d_prime_balance.append(new)
        last = new
        time=time+dt
    
    return d_prime_balance
    #return pd.Series(d_prime_balance)


def d_prime_balance(speed, cs, d_prime, algorithm="waterworth", *args, **kwargs):
    if algorithm == "waterworth":
        method = d_prime_balance_waterworth
    elif algorithm == "skiba":
        method = d_prime_balance_skiba
    elif algorithm == "froncioni-skiba-clarke":
        method = d_prime_balance_froncioni_skiba_clarke

    return method(speed, cs, d_prime, *args, **kwargs)
