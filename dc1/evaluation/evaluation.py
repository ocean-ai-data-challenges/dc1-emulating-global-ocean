#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Evaluator class using Glorys forecasts as reference."""

from argparse import Namespace
from typing import Optional

import geopandas as gpd
from loguru import logger
import pandas as pd
from shapely import geometry

from dctools.data.datasets.dataset import get_dataset_from_config
from dctools.data.datasets.dataloader import EvaluationDataloader
from dctools.data.datasets.dataset_manager import MultiSourceDatasetManager

from dctools.data.transforms import CustomTransforms
from dctools.metrics.evaluator import Evaluator
from dctools.metrics.metrics import MetricComputer
from dctools.utilities.init_dask import setup_dask
from dctools.utilities.xarray_utils import (
    DICT_RENAME_CMEMS,
    LIST_VARS_GLONET,
    RANGES_GLONET,
    GLONET_DEPTH_VALS,
)


class GlorysEvaluation:
    """Class to evaluate models on Glorys forecasts."""

    def __init__(self, arguments: Namespace) -> None:
        """Init class.

        Args:
            aruguments (str): Namespace with config.
        """
        self.args = arguments

    def filter_data(
        self, manager: MultiSourceDatasetManager,
        filter_region: gpd.GeoSeries,
    ):
        # Appliquer les filtres temporels
        manager.filter_all_by_date(
            start=pd.to_datetime(self.args.start_times[0]),
            end=pd.to_datetime(self.args.end_times[0]),
        )
        # Appliquer les filtres spatiaux
        manager.filter_all_by_region(
            region=filter_region
        )
        # Appliquer les filtres sur les variables
        manager.filter_all_by_variable(variables=self.args.target_vars)
        return manager

    def setup_transforms(self):
        """Fixture pour configurer les transformations."""
        # Configurer les transformations
        glonet_transform = CustomTransforms(
            transform_name="glorys_to_glonet",
            weights_path=self.args.regridder_weights,
            depth_coord_vals=GLONET_DEPTH_VALS,
            interp_ranges=RANGES_GLONET,
        )
        # Configurer les transformations
        """pred_transform = CustomTransforms(
            transform_name="rename_subset_vars",
            dict_rename={"longitude": "lon", "latitude": "lat"},
            list_vars=["uo", "vo", "zos"],
        )

        ref_transform = CustomTransforms(
            transform_name="interpolate",
            interp_ranges={"lat": np.arange(-10, 10, 0.25), "lon": np.arange(-10, 10, 0.25)},
        )"""
        return {"glonet": glonet_transform}


    def check_dataloader(
        self,
        dataloader: EvaluationDataloader,
    ):
        for batch in dataloader:
            # Vérifier que le batch contient les clés attendues
            assert "pred_data" in batch[0]
            assert "ref_data" in batch[0]
            # Vérifier que les données sont de type str (paths)
            assert isinstance(batch[0]["pred_data"], str)
            if batch[0]["ref_data"]:
                assert isinstance(batch[0]["ref_data"], str)

    def setup_dataset_manager(self) -> None:

        '''glorys_dataset_name = "glorys"
        glonet_dataset_name = "glonet"
        glonet_wasabi_dataset_name = "glonet_wasabi"
        glorys_catalog_path = os.path.join(
            self.args.catalog_dir, glorys_dataset_name + ".json"
        )
        glonet_catalog_path = os.path.join(
            self.args.catalog_dir, glonet_dataset_name + ".json"
        )
        glonet_wasabi_catalog_path = os.path.join(
            self.args.catalog_dir, glonet_wasabi_dataset_name + ".json"
        )'''

        for source in self.args.sources:
            source_name = source['dataset']
            if source_name == "glorys":
                glorys_dataset = get_dataset_from_config(
                    source,
                    self.args.data_directory,
                    self.args.catalog_dir,
                    self.args.max_samples,
                )
            elif source_name == "glonet":
                glonet_dataset = get_dataset_from_config(
                    source,
                    self.args.data_directory,
                    self.args.catalog_dir,
                    self.args.max_samples,
                )
            elif source_name == "glonet_wasabi":
                glonet_wasabi_dataset = get_dataset_from_config(
                    source,
                    self.args.data_directory,
                    self.args.catalog_dir,
                    self.args.max_samples,
                )
        # Configurer les datasets
        # Glorys
        '''glorys_connection_config = CMEMSConnectionConfig(
            local_root=self.args.glorys_data_dir,
            dataset_id=self.args.glorys_cmems_product_name,
            max_samples=self.args.max_samples,
        )
        if os.path.exists(glorys_catalog_path):
            # Load dataset metadata from catalog
            glorys_config = DatasetConfig(
                alias=glorys_dataset_name,
                connection_config=glorys_connection_config,
                catalog_options={"catalog_path": glorys_catalog_path}
            )
        else:
            # create dataset
            glorys_config = DatasetConfig(
                alias=glorys_dataset_name,
                connection_config=glorys_connection_config,
            )
        # Création du dataset
        glorys_dataset = RemoteDataset(glorys_config)'''



        # Glonet (source Wasabi)
        '''glonet_wasabi_connection_config = WasabiS3ConnectionConfig(
            local_root=self.args.glonet_data_dir,
            bucket=self.args.wasabi_bucket,
            bucket_folder=self.args.wasabi_glonet_folder,
            key=self.args.wasabi_key,
            secret_key=self.args.wasabi_secret_key,
            endpoint_url=self.args.wasabi_endpoint_url,
            max_samples=self.args.max_samples,
        )
        if os.path.exists(glonet_wasabi_catalog_path):
            glonet_wasabi_config = DatasetConfig(
                alias=glonet_wasabi_dataset_name,
                connection_config=glonet_wasabi_connection_config,
                catalog_options={"catalog_path": glonet_wasabi_catalog_path},
            )
        else:
            glonet_wasabi_config = DatasetConfig(
                alias=glonet_wasabi_dataset_name,
                connection_config=glonet_wasabi_connection_config,        
            )
        glonet_wasabi_dataset = RemoteDataset(glonet_wasabi_config)


        # Glonet
        glonet_connection_config = GlonetConnectionConfig(
            local_root=self.args.glonet_data_dir,
            endpoint_url=self.args.glonet_base_url,
            max_samples=self.args.max_samples,
        )
        if os.path.exists(glonet_catalog_path):
            glonet_config = DatasetConfig(
                alias=glorys_dataset_name,
                connection_config=glonet_connection_config,
                catalog_options={"catalog_path": glonet_catalog_path}
            )
        else:
            # create dataset
            glonet_config = DatasetConfig(
                alias=glonet_dataset_name,
                connection_config=glonet_connection_config,
            )
        glonet_dataset = RemoteDataset(glonet_config)'''

        filter_region = gpd.GeoSeries(geometry.Polygon((
            (self.args.min_lon,self.args.min_lat),
            (self.args.min_lon,self.args.max_lat),
            (self.args.max_lon,self.args.min_lat),
            (self.args.max_lon,self.args.max_lat),
            (self.args.min_lon,self.args.min_lat),
            )), crs="EPSG:4326")

        manager = MultiSourceDatasetManager()

        logger.debug(f"Setup datasets manager")
        # Ajouter les datasets avec des alias
        manager.add_dataset("glonet", glonet_dataset)
        manager.add_dataset("glorys", glorys_dataset)
        manager.add_dataset("glonet_wasabi", glonet_wasabi_dataset)

        # Appliquer les filtres temporels
        manager.filter_all_by_date(
            start=pd.to_datetime(self.args.start_times[0]),
            end=pd.to_datetime(self.args.end_times[0]),
            #start=test_config.start_times[0],
            #end=test_config.end_times[0],
        )
        # Appliquer les filtres spatiaux
        manager.filter_all_by_region(
            region=filter_region    #=(test_config.min_lon, test_config.min_lat, test_config.max_lon, test_config.max_lat)
        )
        # Appliquer les filtres sur les variables
        manager.filter_all_by_variable(variables=self.args.target_vars)

        # Construire le catalogue
        logger.debug(f"Build catalog")
        manager.build_catalogs()

        manager.all_to_json(output_dir=self.args.catalog_dir)
        manager = self.filter_data(manager, filter_region)
        return manager


    def run_eval(self) -> None:
        """Proceed to evaluation."""
        dataset_manager = self.setup_dataset_manager()
        dask_cluster = setup_dask(self.args)

        transforms = self.setup_transforms()
        transform_glonet = transforms["glonet"]
        # Créer un dataloader
        """dataloader = manager.get_dataloader(
            pred_alias="glonet",
            ref_alias="glorys",
            batch_size=8,
            pred_transform=glonet_transform,
            ref_transform=glonet_transform,
        )"""
        dataloader = dataset_manager.get_dataloader(
            pred_alias="glonet",
            ref_alias=None,
            batch_size=self.args.batch_size,
            pred_transform=None,
            ref_transform=None,
        )

        # Vérifier le dataloader
        self.check_dataloader(dataloader)

        metrics = [
            MetricComputer(metric_name="rmse"),
            #MetricComputer(metric_name="euclid_dist"),
            #MetricComputer(metric_name="energy_cascad"),
        ]
        evaluator = Evaluator(
            dask_cluster=dask_cluster,
            metrics=metrics,
            dataloader=dataloader,
        )
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

        results = evaluator.evaluate()

        # Vérifier que les résultats existent
        assert len(results) > 0

        # Vérifier que chaque résultat contient les champs attendus
        for result in results:
            assert "date" in result
            assert "metric" in result
            assert "result" in result
        logger.info(f"Test Results: {results}")

