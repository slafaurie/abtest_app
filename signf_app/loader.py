import pandas as pd
from typing import Tuple 

import pydata_google_auth
from google.cloud import bigquery



class Loader:
    # TODO -> Add Logger
    # TODO -> Should I create a Transformer class?
    """
    The objective of this class is have the functions required to succesfully load
    the test data into the app
    """

    def __init__(self) -> None:
        self.client = None 

    def auth(self):
        credentials = pydata_google_auth.get_user_credentials(
            ['https://www.googleapis.com/auth/bigquery'],
        )
        self.client = bigquery.Client(project='logistics-data-staging-flat', credentials=credentials)

    
    def load_test_data(self, path: str, format='sql') -> pd.DataFrame:
        # TODO -> Add Docstring

        if format == 'csv':
            return pd.read_csv(path)
        
        if format == 'sql':
            return self.client\
                    .query ('''
                    SELECT * FROM `{}`
                    '''.format(path)
                    ).to_dataframe()

    @staticmethod
    def _split_variant(data: pd.DataFrame, var: str):
        # TODO -> Add Docstring
        return data.query("variant==@var").reset_index(drop=True)

    @classmethod
    def split_control_variation_from_data(cls, data: pd.DataFrame):
        # TODO -> Add Docstring
        return cls._split_variant(data, "Control"), cls._split_variant(data, "Variation1")

    @classmethod
    def extract_series_from_data(cls, data: pd.DataFrame, varname:str) -> Tuple[pd.Series, pd.Series]:
        # TODO -> Add 
        control, variation = cls.split_control_variation_from_data(data)
        return control[varname], variation[varname]


    @staticmethod
    def aggregate_by_conversion(data: pd.DataFrame, conv_var: str) -> pd.DataFrame:
        # TODO -> Add Docstring
        """
        Aggregates a dataframe to suit a proportion testing. It takes as an input
        the column from which we should calculate a proportion, such column should have only 1 or zeros. 
        It returns a new dataframe which only three columns: The variant, the count and the conversion. 

        Args:
            Data (pd.DataFrame) : DataFrame with the raw data
            conv_var (str) : Column that represent the conversion. It should have only 1 or 0

        """
        return data.groupby('variant', as_index=False).agg(
                        cvr = ( conv_var, 'mean'),
                        count = ( conv_var, 'size')
                    )


    def aggregate_by_user():
        # TODO -> Add Docstring
        pass

    def normalize_by_column():
        # TODO -> Add Docstring
        pass