#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Evaluator class using Glorys forecasts as reference."""

from argparse import Namespace
import os
from pathlib import Path
from typing import Dict, List

from dctools.dcio.loader import DataLoader
from dctools.dcio.saver import DataSaver
from dctools.processing.cmems_data import create_glorys_ndays_forecast
from dctools.utilities.file_utils import remove_listof_files, get_list_filter_files
from dctools.utilities.misc_utils import get_dates_from_startdate
from dctools.utilities.net_utils import download_s3_file


class GlorysEvaluation:
    """Class to evaluate models on Glorys forecasts."""

    def __init__(self, arguments: Namespace, dc_config: Dict) -> None:
        """Init class.

        Args:
            local_data_path (str): folder where to store downloaded data.
        """
        self.args = arguments
        self.dc_config = dc_config
        self.oceanbench_metrics = arguments.oceanbench_metrics
        self.logged = False

    def run_eval(self) -> None:
        """Proceed to evaluation."""
        list_start_dates = self.dc_config['list_glonet_start_dates'].split(',')
        '''path_glonet = "public/glonet_reforecast_2024/"
        list_start_dates = ["2024-01-03", "2024-01-10", "2024-01-17", "2024-01-24", "2024-01-31",
                           "2024-02-07", "2024-02-14", "2024-02-21", "2024-02-28", "2024-03-06",
                           "2024-03-13", "2024-03-20", "2024-03-27", "2024-04-03", "2024-04-10",
                           "2024-04-17", "2024-04-24", "2024-05-01", "2024-05-08", "2024-05-15",
                           "2024-05-22", "2024-05-29", "2024-06-05", "2024-06-12", "2024-06-19",
                           "2024-06-26", "2024-07-03", "2024-07-10", "2024-07-17" ]'''
        rmse_metrics = {}

        for start_date in list_start_dates:
            self.args.dc1_logger.info(f"process start_date: {start_date}")
            glonet_filename = start_date + '.nc'
            glonet_filepath = os.path.join(
                self.args.glonet_data_dir, glonet_filename
            )
            if not Path(glonet_filepath).is_file():
                self.download_glonet_forecast(glonet_filename)
            glonet_data = DataLoader.lazy_load_dataset(
                glonet_filepath, self.args.exception_handler
            )
            list_dates = get_dates_from_startdate(
                start_date, self.dc_config['glonet_n_days_forecast']
            )
            first_date = list_dates[0]

            glorys_filepath = os.path.join(self.args.glorys_data_dir, glonet_filename)
            if not (Path(glorys_filepath).is_file()):
                list_mercator_files = get_list_filter_files(
                    self.args.glorys_data_dir,
                    extension='.nc',
                    regex="mercatorglorys",
                    prefix=True,
                )
                if len(list_mercator_files) != self.dc_config['glonet_n_days_forecast']:
                    for date in list_dates:
                        filter = self.args.cmems_manager.get_cmems_filter_from_date(date)
                        if not self.logged:
                            self.args.cmems_manager.cmems_login()
                            self.logged = True
                        self.args.cmems_manager.cmems_download(
                            product_id=self.dc_config['glorys_cmems_product_name'],
                            output_dir=self.args.glorys_data_dir,
                            filter=filter,
                        )
                    list_mercator_files = get_list_filter_files(
                    self.args.glorys_data_dir,
                    extension='.nc',
                    regex="mercatorglorys",
                    prefix=True,
                )
                assert(len(list_mercator_files) == self.dc_config['glonet_n_days_forecast'])

                glorys_data = create_glorys_ndays_forecast(
                    nc_path=self.args.glorys_data_dir,
                    list_nc_files=list_mercator_files,
                    ref_data=glonet_data,
                    start_date=first_date,
                    dclogger=self.args.dc1_logger,
                    exception_handler=self.args.exception_handler
                )
                DataSaver.save_dataset(
                    glorys_data,
                    glorys_filepath,
                    self.args.exception_handler
                )
            else:
                glorys_data = DataLoader.lazy_load_dataset(
                    glorys_filepath, self.args.exception_handler
                )
            # call RMSE metric function
            self.args.dc1_logger.info(
                f"Compute {self.args.metric} metric for start date : {start_date}"
            )

            eval_array = self.oceanbench_metrics.compute_metric(
                self.args.metric, glonet_data, glorys_data, False
            )
            rmse_metrics[start_date] = eval_array
            # remove downloaded files
            list_mercator_files = get_list_filter_files(
                self.args.glorys_data_dir,
                extension='.nc',
                regex="mercatorglorys",
                prefix=True,
            )
            # print("List Mercator files : ", list_mercator_files)
            if len(list_mercator_files) > 0:
                self.args.dc1_logger.info("Remove temporary Mercator files.")
                remove_listof_files(
                    list_mercator_files, self.args.glorys_data_dir, self.args.exception_handler
                )

        self.args.dc1_logger.info(f"Aggregated RMSE metrics : {rmse_metrics}")

    def download_glonet_forecast(self, filename: str):
        """Download glonet forecast file from Edito.

        Args:
            filename (str): name of the file to download.
        """
        local_file_path = os.path.join(self.args.glonet_data_dir, filename)
        glonet_s3_filepath = os.path.join(
            self.dc_config['s3_glonet_folder'],
            filename
        )

        download_s3_file(
            s3_client=self.args.s3_client,
            bucket_name=self.dc_config['glonet_s3_bucket'],
            file_name=glonet_s3_filepath,
            local_file_path=local_file_path,
            dclogger=self.args.dc1_logger,
            exception_handler=self.args.exception_handler,
        )

    def download_glorys_files(self, list_glonet_files: List[str]):
        """Download Glorys files from CMEMS.

        Args:
            list_glonet_files (List[str]): list of the files to download.
        """
        for filename in list_glonet_files:
            local_file_path = os.path.join(self.args.glorys_data_dir, filename)
            download_s3_file(
                self.args.s3_client,
                self.dc_config['glonet_s3_bucket'],
                filename,
                local_file_path,
                self.args.dc1_logger,
                self.args.exception_handler,
            )
