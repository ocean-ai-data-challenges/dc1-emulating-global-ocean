#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Evaluation of a model against a given reference."""

from argparse import ArgumentParser, Namespace
import os
import sys
from typing import Dict, List, Optional

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from dctools.dcio.dclogger import DCLogger
from dctools.metrics.oceanbench_metrics import OceanbenchMetrics
from dctools.utilities.errors import DCExceptionHandler
from dctools.utilities.net_utils import CMEMSManager
import yaml

from dc1.evaluation.glorys_evaluation import GlorysEvaluation


def parse_arguments(cli_args: Optional[List[str]] = None) -> Namespace:
    """Command-line argument parser.

    Args:
        cli_args (List[str], optional): List of arguments.

    Returns:
        Namespace: Namespace with parsed args.
    """
    parser = ArgumentParser()
    parser = ArgumentParser(description='Run DC1 Evaluation on Glorys data')
    parser.add_argument(
        '-d', '--data_directory', type=str,
        help="Folder where to store downloaded data",
        required=True,
    )
    parser.add_argument(
        '-c', '--config_name', type=str,
        default="glorys_eval",
        help="Folder where to store downloaded data",
    )
    parser.add_argument(
        '-l', '--logfile', type=str,
        help="File where to store log info.",
    )
    parser.add_argument(
        '-m', '--metric', type=str,
        help="Type of metric to compute."
        "Choose from list: [rmse, mld, geo, density, euclid_dist,"
        "energy_cascad, kinetic_energy, vorticity, mass_conservation]",
        default="rmse",
    )
    return parser.parse_args(args=cli_args)  # None defaults to sys.argv[1:]


def load_configs(args: Namespace, exception_handler: DCExceptionHandler) -> Dict:
    """Load configuration from yaml file.

    Args:
        args (Namespace): parsed arguments Namespace.
        exception_handler (DCExceptionHandler):

    Raises:
        err: error

    Returns:
        Dict: Dict of cofig elements.
    """
    try:
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'config',
            f"{args.config_name}.yaml",
        )

        with open(config_path, 'r') as file_pointer:
            config = yaml.safe_load(file_pointer)
    except Exception as err:
        exception_handler.handle_exception(
            err, f"Error while loading config from: {config_path}."
        )
    return config

def init_evaluation(args: Namespace, dc_config: Dict):
    """Initialize basic variables for evaluation.

    Args:
        args (Namespace): arguments.
        dc_config (Namespace): config._
    """
    '''glonet_base_url = "https://minio.dive.edito.eu"
    glorys_cmems_product_name = "cmems_mod_glo_phy_myint_0.083deg_P1D-m"
    glonet_s3_bucket = "project-glonet"
    s3_glonet_folder = "public/glonet_reforecast_2024"
    glonet_n_days_forecast = 10'''
    try:
        vars(args)['glonet_data_dir'] = os.path.join(args.data_directory, 'glonet')
        vars(args)['glorys_data_dir'] = os.path.join(args.data_directory, 'glorys')

        cmems_manager = CMEMSManager(
            args.dc1_logger, args.exception_handler
        )
        # cmems_manager.cmems_login()
        vars(args)['cmems_manager'] = cmems_manager

        s3_client = boto3.client(
            "s3",
            config=Config(signature_version=UNSIGNED),
            endpoint_url=dc_config['glonet_base_url'],
        )
        vars(args)['s3_client'] = s3_client

        os.makedirs(args.glonet_data_dir, exist_ok=True)
        os.makedirs(args.glorys_data_dir, exist_ok=True)

        # instance for metrics computation
        vars(args)['oceanbench_metrics'] = OceanbenchMetrics(
            args.dc1_logger, args.exception_handler
        )
    except Exception as exc:
        args.exception_handler.handle_exception(exc, "Error while initializing init variables.")

    return args

def main(args: Namespace = parse_arguments()) -> int:
    """Main function.

    Args:
        args (Namespace, optional): Namespace of parsed arguments.

    Returns:
        int: return code.
    """
    try:
        # init logger and exception handler
        dc1_logger = DCLogger(
            name="DC1 Logger", logfile=args.logfile
        ).get_logger()
        # initialize exception handler
        exception_handler = DCExceptionHandler(dc1_logger)
        vars(args)['dc1_logger'] = dc1_logger
        vars(args)['exception_handler'] = exception_handler

        config = load_configs(args, exception_handler)

        args = init_evaluation(args, config)
        evaluator = GlorysEvaluation(args, config)
        evaluator.run_eval()

    except KeyboardInterrupt:
        dc1_logger.error("Manual abort.")
        return 1

    except Exception as err:
        exception_handler.handle_exception(err, "An unhandled exception occured.")
        # Error = non-zero return code
        return 1

    dc1_logger.info("Evaluation has finished successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main(parse_arguments()))
