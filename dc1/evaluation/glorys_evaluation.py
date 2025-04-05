#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Evaluator class using Glorys forecasts as reference."""

from argparse import Namespace
import os
from pathlib import Path
from typing import Dict, List

from dask.distributed import Client

from dctools.data.dataloader import DatasetLoader
from dctools.data.dataset import CmemsGlorysDataset, GlonetDataset
#from dctools.dcio.loader import FileLoader
#from dctools.dcio.saver import DataSaver
from dctools.metrics.evaluator import Evaluator
from dctools.metrics.metrics import MetricComputer
from dctools.data.transforms import CustomTransforms
from dctools.utilities.init_dask import setup_dask
from dctools.utilities.xarray_utils import DICT_RENAME_CMEMS,\
    LIST_VARS_GLONET, RANGES_GLONET, GLONET_DEPTH_VALS



class GlorysEvaluation:
    """Class to evaluate models on Glorys forecasts."""

    def __init__(self, arguments: Namespace) -> None:
        """Init class.

        Args:
            aruguments (str): Namespace with config.
        """
        self.args = arguments

    def run_eval(self) -> None:
        """Proceed to evaluation."""
        #list_start_dates = self.args['list_glonet_start_dates'].split(',')
        '''path_glonet = "public/glonet_reforecast_2024/"
        list_start_dates = ["2024-01-03", "2024-01-10", "2024-01-17", "2024-01-24", "2024-01-31",
                           "2024-02-07", "2024-02-14", "2024-02-21", "2024-02-28", "2024-03-06",
                           "2024-03-13", "2024-03-20", "2024-03-27", "2024-04-03", "2024-04-10",
                           "2024-04-17", "2024-04-24", "2024-05-01", "2024-05-08", "2024-05-15",
                           "2024-05-22", "2024-05-29", "2024-06-05", "2024-06-12", "2024-06-19",
                           "2024-06-26", "2024-07-03", "2024-07-10", "2024-07-17" ]'''

        #for start_date in list_start_dates:
        #    self.args.dclogger.info(f"process Initial Date: {start_date}")

        #    list_dates = get_dates_from_startdate(
        #        start_date, self.dc_config['glonet_n_days_forecast']
        #    )

        dask_cluster = setup_dask(self.args)
        glonet_data_dir = self.args.glonet_data_dir
        glorys_data_dir = self.args.glorys_data_dir

        transf_glorys = CustomTransforms(
            transform_name="glorys_to_glonet",
            dict_rename=DICT_RENAME_CMEMS,
            list_vars=LIST_VARS_GLONET,
            depth_coord_vals=GLONET_DEPTH_VALS,
            interp_ranges = RANGES_GLONET,
            weights_path=self.args.weights_path,
        )
        self.args.dclogger.info("Creating datasets.")
        dataset_glonet = GlonetDataset(
            conf_args=self.args,
            root_data_dir= glonet_data_dir,
            list_dates=self.args.list_glonet_start_dates,
            transform_fct=None,
        )

        dataset_glorys = CmemsGlorysDataset(
            conf_args=self.args,
            root_data_dir= glorys_data_dir,
            cmems_product_name=self.args.glorys_cmems_product_name,
            cmems_file_prefix="mercatorglorys",
            list_dates=self.args.list_glonet_start_dates,
            transform_fct=transf_glorys,
            save_after_preprocess=False,
            file_format="zarr",
        )
        # 1. Chargement des données de référence et des prédictions avec DatasetLoader
        glonet_vs_glorys_loader = DatasetLoader(
            pred_dataset=dataset_glonet,
            ref_dataset=dataset_glorys
        )

        # 3. Exécution de l’évaluation sur plusieurs modèles
        evaluator = Evaluator(
            self.args, 
            dask_cluster=dask_cluster, metrics=None,
            data_container={'glonet': glonet_vs_glorys_loader},
        )

        metrics = [
            MetricComputer(
                dc_logger=self.args.dclogger,
                exc_handler=self.args.exception_handler,
                metric_name='rmse', plot_result=False,
            ),

            MetricComputer(
                dc_logger=self.args.dclogger,
                exc_handler=self.args.exception_handler,
                metric_name='energy_cascad',
                plot_result=False,
                var="uo", depth=2,
            ),
        ]
        ''' TODO : check error on oceanbench : why depth = 0 ? -> crash
            MetricComputer(
                dc_logger=test_vars.dclogger,
                exc_handler=test_vars.exception_handler,
                metric_name='euclid_dist',
                plot_result=True,
                minimum_latitude=0,
                maximum_latitude=10,
                minimum_longitude=0,
                maximum_longitude=10,
            ),'''
        
        evaluator.set_metrics(metrics)
        self.args.dclogger.info("Run computation of metrics.")
        results = evaluator.evaluate()

        self.args.dclogger.info(f"Computed metrics : {results}")

