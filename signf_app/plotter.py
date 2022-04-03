from typing import Tuple, Union

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from signf_app.loader import Loader


class PlotlyBackend:
    """
    This class contains method to produce the required plot for analysis using Plotly as 
    backend.
    """
    
    @staticmethod
    def make_hist(control: pd.Series, variant: pd.Series, figsize: Tuple[int,int] = (800,600) ):
        """
        Produce an histogram for both control and variant.

        Args
            control (pd.Series) -> Array containing the values of the chosen variable in the control group
            variant (pd.Series) -> Array containing the values of the chosen variable in the variant group
            figsize (int, int) : A (width, height)  tuple in pixels that specifies the size of the returned figure

        Returns
            f: A Figure that contains the histograms of both control and variant  
        """
        w,h = figsize
        f = go.Figure()
        f.add_trace(go.Histogram(x=control, name="Control"))
        f.add_trace(go.Histogram(x=variant, name="Variant"))
        f.update_layout(
            barmode="overlay",
            title='Histogram of both variant and control',
            width = w, 
            height = h)
        f.update_traces(opacity=0.75)
        return f

    @staticmethod
    def make_quantile(data: pd.DataFrame, varname: str, figsize: Tuple[int,int] = (800,600) ):
        """
        Produce an quantile treatment plot. It already asume the scheme of the input dataframe to plot the figure which 
        comes from bootstrapper.Bootstrapper.summarize_quantile_effect. 

        Args
            data (pd.DataFrame): Dataframe with the expected scheme
            varname (str) : Chosen variable. This variable is just to use it in the title.
            figsize (int, int) : A (width, height)  tuple in pixels that specifies the size of the returned figure

        Returns
            f: Figure object. 

        """
        w,h = figsize
        f = go.Figure()
        f.add_trace(go.Scatter(y=data["diff_lower"], x=data["plot_axis"], name="Lower Bound 95CI"))
        f.add_trace(go.Scatter(y=data["diff_upper"], x=data["plot_axis"], fill="tonexty", name="Upper Bound 95CI"))
        f.add_trace(go.Scatter(y=data["diff_mean"], x=data["plot_axis"], mode="lines", name="Mean"))
        f.add_hline(y=0)
        f.update_layout(
            title="Quantile Treatment Effect",
            xaxis=dict(title=f"Percentile | Variation {varname}"),
            width = w, 
            height = h
        )
        return f

    
    @staticmethod
    def make_h0_hist(
        modeled_h0: np.array, 
        exp_test: float,
        varname: str, 
        figsize: Tuple[int,int] = (800,600)
        ):

        """
        Plot the distribution of modeled_h0  and the experimental test statistics using Plotly

        Args
            modeled_h0: Array with the differences of means between control and variant under the h0 hypothesis
            exp_test: Observed difference.
            varname: chosen variable for the analysis. Used just for the title. 
            figsize (int, int) : A (width, height)  tuple in pixels that specifies the size of the returned figure
        
        Returns
            f: Figure Object

        """

        # TODO -> Add figsize parameter to plotly -> DONE
        w,h = figsize
        f = go.Figure()
        f.add_trace(go.Histogram(x=modeled_h0, name="H0"))
        f.add_vline(x=exp_test, line_color='red')
        f.update_traces(opacity=0.75)
        f.update_layout(
            title=f'Distribution of {varname} under H0',
            width = w, 
            height = h
        )
        return f    





class Plotter:
    """
    This class is the one used to call the method that generates the plot for analysis.
    It's also wrapper to have both the Plotly and Pyplot backend availables. 
    """
     
    @staticmethod
    def plot_hist(
        data: pd.DataFrame, 
        varname: str, 
        figsize: Tuple[int, int] = (800,600), 
        cap: Union[float, int] = None, 
        backend:str = 'plotly'):

        """
        Plot the histogram of the chosen variable.

        Args
            data (pd.DataFrame): Dataframe with the test data. 
            varname (str): Chosen variable for analysis
            figsize (int, int) : A (width, height) tuple that specifies the size of the returned figure.
            cap (float, int): Used to filter outliers
            backend (str): Define the library used for plots. Default is plotly as is interactive. Other choice is 'pyplot'
            which is seaborn/matplotlib based and is static.
        
        """
        # TODO -> Add Docstring -> DONE
        # TODO -> Add Typing -> DONE
        if cap:
            mask = data[varname] < cap
            data = data[mask]

        control, variant = Loader.extract_series_from_data(data, varname)

        if backend == "plotly":
            f = PlotlyBackend.make_hist(control, variant, figsize=figsize)

        return f



    @classmethod
    def plot_quantile_effect(
        cls, 
        quantiles_summary: pd.DataFrame, 
        varname: str, 
        figsize: Tuple[int, int] = (800,600),
        backend: str = "plotly"
        ):

        
        """
        Plot the quantile of the chosen variable.

        Args
            quantiles_summary (pd.DataFrame): Dataframe with the test data. 
            varname (str): Chosen variable for analysis, used just in the title.
            figsize (int, int) : A (width, height) tuple that specifies the size of the returned figure.
            backend (str): Define the library used for plots. Default is plotly as is interactive. Other choice is 'pyplot'
            which is seaborn/matplotlib based and is static.

        Returns
            f: Figure Object
        
        """

        # TODO -> Add Typing -> DONE
        # TODO -> Add Docstring -> DONE
        # TODO -> Add Plotly Backend -> DONE


        # Generate graph
        # TODO -> Abstract in a function that unpacks the desired columns -> NOT NEEDED/DONE
        if backend == "plotly":
            f = PlotlyBackend.make_quantile(quantiles_summary, varname, figsize)

        return f

    @staticmethod
    def plot_h0_results(
        modeled_h0: np.array, 
        exp_test: float,
        varname: str, 
        figsize: Tuple[int, int] = (800,600), 
        backend: str ='plotly'
        ):
        # TODO: Add Typing -> DONE

        """
        Plot the distribution of modeled_h0  and the experimental test statistics

        Args
            modeled_h0: Array with the differences of means between control and variant under the h0 hypothesis
            exp_test: Observed difference.
            varname: chosen variable for the analysis. Used just for the title. 
            figsize (int, int) : A (width, height) tuple that specifies the size of the returned figure.
            backend (str): Define the library used for plots. Default is plotly as is interactive. Other choice is 'pyplot'
            which is seaborn/matplotlib based and is static.
        
        Returns
            f: Figure Object

        """
        if backend == 'plotly':
            f = PlotlyBackend.make_h0_hist(modeled_h0, exp_test, varname, figsize)
            
        return f
