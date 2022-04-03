# simulate effect under H0
import numpy as np
import pandas as pd



class Resampler:
    # TODO -> Add Logger

    """
    The resampler class gather all functionality required to perform a hyphotesis testing by simulation of the 
    H0. 

    For more reference check: https://allendowney.github.io/ElementsOfDataScience/13_hypothesis.html
    """

    def __init__(self, nrg: np.random) -> None:
        self.nrg = nrg
        
    def _simulate_group_percent(self, n: int, p: float):
        """
        Return the simulated proportion of a success with probability p 
        in n trials. 
        """
        xs = self.nrg.random(size=n)
        k = np.sum(xs < p)
        return k / n * 100


    def simulate_proportion_under_h0(self, test_h0: float, n_control: int, n_variation: int, n_iter: int = 1000):
        """
        Under H0 -> effect is due to random and there's no difference between control and variation
        runs n_iter number of experiments for each control and variation
        """
        control, variation = [], []
        for i in range(n_iter):
            if i % 100 == 0:
                print(f"Iteration {i}")
            c = self._simulate_group_percent(n_control, test_h0)
            v = self._simulate_group_percent(n_variation, test_h0)
            control.append(c)
            variation.append(v)
        return np.array(control), np.array(variation)

        
    def _permutation_test_under_h0(self, control: pd.Series, variation: pd.Series):
        """
        Under H0 -> effect is due to random and there's no difference between control and variation
        combines control and variation data, shuffle it and slice again control and variation.
        """
        n, m = len(control), len(variation)
        data = np.append(control, variation)
        self.nrg.shuffle(data)
        control = data[:n]
        variation = data[n:]
        return  control, variation


    def simulate_cont_under_h0(self, control: pd.Series, variation: pd.Series, n_iter = 1000):
        """
        Performs a n_iter number of permutation tests for control and variation
        """
        control_perm, variation_perm = [], []
        for i in range(n_iter):
            if i % 100 == 0:
                print(f"Iteration {i}")
            c,v = self._permutation_test_under_h0(control, variation)
            control_perm.append(c)
            variation_perm.append(v)
        return control_perm, variation_perm
