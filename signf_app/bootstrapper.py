import numpy as np
import pandas as pd


class Bootstrapper:
    # TODO -> Add Docstring
    # TODO -> Add Logger
    """
    
    References:
        - https://eng.uber.com/analyzing-experiment-outcomes/
        - https://towardsdatascience.com/recreating-netflixs-quantile-bootstrapping-in-r-a4739a69adb6
    """

    def __init__(self, nrg) -> None:
        # TODO -> Add Typing
        self.nrg = nrg
        
    def _bootstrap_series(self, series):
        # TODO -> Add Docstring
        # TODO -> Add Typing
        return series.sample(len(series), replace=True, random_state = self.nrg)

    @staticmethod
    def _get_quantiles(series: pd.Series, q = np.arange(0, 1.1, 0.1)):
        # TODO -> Add Docstring
        # TODO -> Add Typing
        return np.quantile(series, q)

    def get_variant_control_percentiles(self, control: pd.Series, variant: pd.Series, q = np.arange(0, 1.1, 0.1)):
        # TODO -> Add Docstring
        # TODO -> Add Typing
        data = pd.DataFrame(index=q)\
                .assign(
                    control = self._get_quantiles(control, q),
                    variant = self._get_quantiles(variant, q)
                    )\
                .reset_index()
        return data

    @staticmethod
    def create_axis(row):
        return f'{row["percentiles"]:.2f} | {row["variant_mean"]:,.0f}'

    def generate_quantile_bootstrap_raw(self, control, variant, q = np.arange(0, 1.1, 0.1),  n_iter = 100):
        # TODO -> Add Docstring
        # TODO -> Add Typing
        result_list = []
        for i in range(n_iter):
            control_bootstrapped = self._bootstrap_series(control)
            variant_bootstrapped = self._bootstrap_series(variant)
            df = self.get_variant_control_percentiles(control_bootstrapped, variant_bootstrapped, q)
            result_list.append(df)
        return pd.concat(result_list, ignore_index = True)


    @staticmethod
    def _get_lower(series):
        # TODO -> Add Typing
        return series.quantile(0.025)

    @staticmethod
    def _get_upper(series):
        # TODO -> Add Typing
        return series.quantile(0.975)

    
    def summarize_quantile_effect(self, quantiles_bootstrapped):
        # TODO -> Add Docstring
        # TODO -> Add Typing
        quantiles_effect_summarize = quantiles_bootstrapped\
                                    .assign(
                                    variant_to_control = lambda row: row.variant - row.control
                                    )\
                                    .groupby("index", as_index=False)\
                                    .agg(
                                        variant_mean = ("variant", "mean"),
                                        control_mean = ("control", "mean"),
                                        diff_mean = ("variant_to_control", "mean"),
                                        diff_lower = ("variant_to_control", self._get_lower),
                                        diff_upper = ("variant_to_control", self._get_upper)
                                    )\
                                    .rename(columns={'index':'percentiles'})\
                                    .assign(
                                        plot_axis = lambda row: row.apply(self.create_axis, axis=1)
                                        )
        
        return quantiles_effect_summarize


    def generate_quantile_clean(self):
        # TODO -> Add Docstring
        # TODO -> Add Typing
        # TODO -> Complete. This function is a wrapper that combines generate_quantile_bootstrap_raw and summarize_quantile_effect
        pass

    def generate_ci_interval(self, ci=95):
        # TODO -> Add Docstring
        # TODO -> Add Typing
        # TODO -> Complete. This function takes a series and compute the CI intervals
        pass
