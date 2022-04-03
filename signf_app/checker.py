
from scipy.stats import chisquare
from statsmodels.stats.power import TTestPower, NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
import numpy as np


class Checker:
    # TODO -> Add Logger
    """
    The Checker class aims to provide all the functions required to run sanity checks
    before run an analysis on a test. By default, the alpha is set to 0.05 and the power to 0.8. 
    Currently, the class checks for Sample Ratio Mismatch and Power Value. 
    """
    def __init__(self, alpha: float = 0.05, power: float = 0.8) -> None:
        self.alpha = alpha
        self.power = power 


    def _do_chi(self, obs, exp):
        # TODO add docstring
        chi = chisquare(f_obs = obs, f_exp= exp)
        return  chi[1]

    def check_for_smr(self, control, variant):
        # TODO add docstring
        # TODO -> Check SMR at daily level?
        # TODO -> Plot sample ratio per day?
        n_control, n_variant = len(control), len(variant)
        total = n_control + n_variant 
        p_val = self._do_chi( obs = [n_control, n_variant], exp =[total/2, total/2])
        return p_val

    def calculate_power_for_mean(self, control, variant):
        # TODO add docstring
        # print(control.mean(), variant.mean())
        treatment_effect = np.abs(control.mean() - variant.mean())
        control_std = control.std()
        return TTestPower().power(effect_size=treatment_effect/control_std, nobs=len(control), alpha=self.alpha)


    def calculate_power_for_proportion(self, control, variant, nobs):
        effect_size = proportion_effectsize(control, variant)
        return NormalIndPower().power(effect_size, nobs1=nobs, alpha=self.alpha)
