import configparser
import logging

import joblib

from src.IO.get_data_from_yahoo import get_last_stock_price, get_stock_price_model
from src.IO.storage_tools import create_bucket, get_model_from_bucket, upload_file_to_bucket
from src.algo.dummy_model import Stock_model

def create_business_logic():
    data_fetcher = get_last_stock_price
    return BusinessLogic(Stock_model(data_fetcher))

class BusinessLogic:

    def __init__(self, model_creator):
        self._root_bucket = 'mnl008_model_bucket_ycng_228'
        self._config = configparser.ConfigParser()
        self._config.read('application.conf')
        self._model_creator = model_creator
        self._create_bucket()

    #def get_version(self):
    #    return self._config['DEFAULT']['version']

    def get_bucket_name(self):
        return f'{self._root_bucket}_{self.get_version().replace(".", "")}'

    def _get_or_create_model(self, ticker, date):
        log = logging.getLogger()
        model_filename = self.get_model_filename_from_date(date)
        model = get_model_from_bucket(model_filename, self.get_bucket_name())
        if model is None:
            log.warning(f'training model for {date}')
            model = self._model_creator.fit(date)
            with open(model_filename, 'wb') as f:
                joblib.dump(model, f)
            upload_file_to_bucket(model_filename, self.get_bucket_name())
        return model

    def get_model_filename_from_date(self, date):
        month = date.month
        year = date.year
        return f'baseline_{year}_{month}.pkl'