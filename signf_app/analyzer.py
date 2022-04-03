
from typing import Union, Tuple

import numpy as np
import pandas as pd

from signf_app.checker import Checker
from signf_app.resampler import Resampler
from signf_app.bootstrapper import Bootstrapper
from signf_app.plotter import Plotter
from signf_app.loader import Loader
from signf_app.common import VarTypes


class Analyzer:
    
    """
    This class performs a full analysis of an A/B test. It performs sanity checks such as
    Sample Ratio Mismatch and Power Analysis to guarantee that the following analysis are robust.
    To create an instance, it requires the just the data and the variable to analyze. It's expected
    that the data contain one column called "variant" which identifies both control and variant. 
    The class currently supports only A/B test not A/B/n.

    The analysis consist of three parts:
        - Hyphotesis testing: The implemented method is to simulate the H0 using resampling for the mean. 
        The p-val is calculated as the # of times the exp treatment effect is observed comparing it with respect to the
        H0 simulation. The test is represented through a Histogram of the simulated differences.
        Reference: https://allendowney.github.io/ElementsOfDataScience/13_hypothesis.html

        - Histogram of both variant and control distribution: We use this plot to go further of the mean and identify
        where and how much the distribution varies. 

        - Quantile Treatment Effect: It performs a hyphotesis testing but at quantiles level to verify if the differences
        in the distribution are significant or not. It uses bootstrap to generate the quantiles distribution. The result is a 
        plot of the mean difference at each quantile with the confidence intervals. 
        Reference for the plot: https://medium.com/towards-data-science/recreating-netflixs-quantile-bootstrapping-in-r-a4739a69adb6

    Attributes:
        data (pd.DataFrame): DataFrame with the data of the A/B test to analyze. 
        The Data must have a "variant" column that indicates which rows are from control and which ones are variation.

        var_to_analyze (str): Variable to analyze e.g "Revenue"

        alpha (float): Test alpha value to calculate statistical significance. Set to 0.05 by default

        power (float): Power parameter. Set to 0.8 by default.


    """
    # TODO -> Add Logger
    
    def __init__(
        self, 
        data: pd.DataFrame, 
        var_to_analyze: str, 
        var_type: VarTypes,
        alpha: float = 0.05,
        power: float = 0.8, 
        nrg: np.random = np.random.default_rng()
        ) -> None:

        # TODO -> Add check if data does not contain the variant column. Or should I include it as parameter?
        """
        Instantiate the class
        """

        if var_to_analyze not in data.columns:
            raise Exception('Variable is not in dataframe')

        if var_type not in [ x.value for x in VarTypes]:
            raise Exception('DataType is not supported. Choose one of "proportion" or "continuous"')

        self.data = data
        self.var_to_analyze = var_to_analyze
        self.var_type = var_type
        self.alpha = alpha
        self.power = power
        self.nrg = nrg

        # TODO -> Create func to abstract this
        self.control, self.variant = Loader.split_control_variation_from_data(self.data)
        self.control_series = self.control[self.var_to_analyze]
        self.variant_series = self.variant[self.var_to_analyze]

    
    def do_sanity_checks(self):
        """
        This method performs sanity checks for an A/B tests. It's a best practice before run a full analyzes
        to guarantee that our further conclusions are not biased by test design/set up. It perfoms two checks:
            - Sample Ratio Mismatch (SMR) which verifies that the sampling between control and variation are not statistically different
            - Power Analysis which verifies that we have enough sample to draw conclusions for the chosen variable at a adequate level of robutness 

        Returns:
            smr_check (str) : Message that contains the result of the SMR check. The message indicates if there are warnings or not.
            power_check(str) : Message that contains the result of the Power check. The message indicates if there are warnings or not.
        """
        # print('Sanity checks')
        # print('Function Init')
        checker = Checker(self.alpha, self.power)
        # print('Function Check1')
        smr_check = checker.check_for_smr(self.control, self.variant)
        # print('Function Check2')


        # TODO do the logic here for diff checks as the proportion requires a preaggregation.
        if self.var_type == VarTypes.CONTINUOUS.value:
            # print(self.var_type)
            power = checker.calculate_power_for_mean(self.control_series, self.variant_series)
            # print(power)
        
        if self.var_type == VarTypes.PROPORTION.value:
            # print(self.var_type)
            agg_data = Loader.aggregate_by_conversion(self.data, self.var_to_analyze)
            agg_control, agg_variant = Loader.split_control_variation_from_data(agg_data)
            power = checker.calculate_power_for_proportion(
                agg_control.cvr.iloc[0], 
                agg_variant.cvr.iloc[0], 
                agg_control['count'].iloc[0]
                )
            # print(power)

        # print('Function End')
        return smr_check, power


    def do_h0_testing(
        self, 
        figsize: Tuple[int, int] = (800,600),
        backend: str = "plotly"
        ):

        """
        This method performs a Hyphotesis testing under the simulation framework. It uses resampling under the hood.
        The idea is to simulate the null hyphotesis, H0, and compare the results with the observed treatment effect. 
        The p-val is calculated as the # of times the exp treatment effect is observed comparing it with respect to the
        H0 simulation. The test is represented through a Histogram of the simulated differences.
        Reference: https://allendowney.github.io/ElementsOfDataScience/13_hypothesis.html

        Args:
            figsize (int, int): A (width, height) tuple that specifies the size of the returned figure.

        Returns:
            p_val (float): The p_val from the test
            f (Figure): A Figure that represents the test. It's an histogram of the simulated differences.

        """
        
        resampler = Resampler(self.nrg)

       
        # Treatment effect
        test_statistic = self.variant_series.mean() - self.control_series.mean()

        if self.var_type == VarTypes.CONTINUOUS.value:
            # Shuffle data
            control_h0, variant_h0 = resampler.simulate_cont_under_h0(self.control_series, self.variant_series)

            # test statistics h0
            diff_of_means_h0 = np.mean(variant_h0, axis=1) - np.mean(control_h0, axis=1)


        if self.var_type == VarTypes.PROPORTION.value:
            # Shuffle data
            effect_h0 = self.control_series.sum() + self.variant_series.sum()
            n_control, n_variant = len(self.control_series), len(self.variant_series)
            prop_h0 = effect_h0 / (n_control + n_variant)
            control_h0, variant_h0 = resampler.simulate_proportion_under_h0(prop_h0, n_control, n_variant)
            diff_of_means_h0 = variant_h0 - control_h0
        
     
        #P value
        # TODO: take account which tail the effect is -> DONE
        p_sim = (diff_of_means_h0 <= test_statistic).mean()
        p_val = min([p_sim, 1 - p_sim])
    

        f = Plotter.plot_h0_results(
            diff_of_means_h0, 
            test_statistic, 
            self.var_to_analyze, 
            figsize=figsize, 
            backend=backend
            )
                
        return test_statistic, p_val, f


    def plot_histogram_treatment_effect(
        self, 
        max_cap: Union[int, float] = None, 
        figsize: Tuple[int, int]  = (800,600),
        backend: str = "plotly"
        ):
        
        """
        Histogram of both variant and control distribution: We use this plot to go further of the mean and identify
        where and how much the distribution varies. 

        Args:
            max_cap (int, float): A parameters that controls the maximum value to display in the return Figure
            figsize (int, int) : A (width, height) tuple that specifies the size of the returned figure.

        Returns:
            f: A Figure that contains the histograms of both control and variant  
        
        """
        f = Plotter.plot_hist(self.data, self.var_to_analyze, cap=max_cap, figsize=figsize, backend=backend)
        return f


    def do_quantile_treatment_effect(
        self, 
        q: np.array = np.linspace(0.01,1,100, endpoint=False), 
        figsize: Tuple[int, int] = (800,600),
        plot_backend: str = 'plotly'
        ):

        """
        It performs a hyphotesis testing but at quantiles level to verify if the differences
        in the distribution are significant or not. It uses bootstrap to generate the quantiles distribution. The result is a 
        plot of the mean difference at each quantile with the confidence intervals. 
        Reference for the plot: https://medium.com/towards-data-science/recreating-netflixs-quantile-bootstrapping-in-r-a4739a69adb6
        
        Args:
            q (np.array): the quantiles to be used. They should be between 0 and 1.
            figsize (int, int) : A (width, height) tuple that specifies the size of the returned figure.

        Returns:
            f: A Figure that contains the plot of the quantiles differences with the confidence intervals. 

        """

        bootstraper = Bootstrapper(self.nrg)

        quantiles_bootstrapped = bootstraper.generate_quantile_bootstrap_raw(
            control=self.control_series,
            variant=self.variant_series,
            q = q)
            

        summarize_quantile = bootstraper.summarize_quantile_effect(quantiles_bootstrapped)

        f = Plotter.plot_quantile_effect(summarize_quantile, varname=self.var_to_analyze, figsize = figsize, backend=plot_backend)
        return f



        
 
        




