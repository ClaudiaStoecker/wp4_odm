"""Orthophoto tool ODM"""

from typing import (Dict)

import argparse
import os
import multiprocessing
from Its4landAPI import Its4landAPI

# from stages.odm_app import ODMApp

def ODMApp(args):
    print(args)
    pass


WORK_VOLUME = '/data'
WORK_VOLUME = '.'
PLATFORM_URL = 'http://i4ldev1dmz.hansaluftbild.de/sub/'
PLATFORM_API_KEY = '1'
BD_HARDCODED_BASEMAP_UID = 'ece25171-6137-4514-94e4-b36006baf97a'


def download(url: str, dest: str) -> str:
    """Download file on specified URL to specified location."""
    api = Its4landAPI(url=PLATFORM_URL, api_key=PLATFORM_API_KEY)

    api.session_token = 'NEW'
    api.download_content_item(url, filename=dest)
    # api.download_file(None, url=url, filename=dest)

    return dest


def unzip(file: str, dest: str) -> None:
    """Unzip specified file to a destination."""
    pass


def get_image_properties(file: str) -> Dict:
    """Get image properties like size etc."""
    return {
        'width': 1000,
        'height': 1000,
    }


def to_odm_args(args: Dict, image_max_side_size: int) -> Dict:
    """Input params translated to ODM params."""
    defaults = {
        'project_path': '/',
        'name': 'code',
        'resize_to': 2048,
        'end_with': 'odm_orthophoto',
        'rerun_all': False,
        'min_num_features': 8000,
        'matcher_neighbors': 8,
        'matcher_distance': 0,
        'use_fixed_camera_params': False,
        'cameras': '',
        'camera_lens': 'auto',
        'max_concurrency': multiprocessing.cpu_count(),
        'depthmap_resolution': 640,
        'opensfm_depthmap_min_consistent_views': 3,
        'opensfm_depthmap_method': 'PATCH_MATCH',
        'opensfm_depthmap_min_patch_sd': 1,
        'use_hybrid_bundle_adjustment': False,
        'mve_confidence': 0.60,
        'use_3dmesh': False,
        'skip_3dmodel': False,
        'use_opensfm_dense': False,
        'ignore_gsd': False,
        'mesh_size': 100000,
        'mesh_octree_depth': 9,
        'mesh_samples': 1.0,
        'mesh_point_weight': 4,
        'fast_orthophoto': False,
        'crop': 3,
        'pc_classify': False,
        'pc_csv': False,
        'pc_las': False,
        'pc_ept': False,
        'pc_filter': 2.5,
        'smrf_scalar': 1.25,
        'smrf_slope': 0.15,
        'smrf_threshold': 0.5,
        'smrf_window': 18.0,
        'texturing_data_term': 'gmi',
        'texturing_nadir_weight': 16,
        'texturing_outlier_removal_type': 'gauss_clamping',
        'texturing_skip_visibility_test': False,
        'texturing_skip_global_seam_leveling': False,
        'texturing_skip_local_seam_leveling': False,
        'texturing_skip_hole_filling': False,
        'texturing_keep_unseen_faces': False,
        'texturing_tone_mapping': 'none',
        'gcp': None,
        'use_exif': False,
        'dtm': False,
        'dsm': False,
        'dem_gapfill_steps': 3,
        'dem_resolution': 5,
        'dem_decimation': 1,
        'dem_euclidean_map': False,
        'orthophoto_resolution': 5,
        'orthophoto_no_tiled': False,
        'orthophoto_compression': 'DEFLATE',
        'orthophoto_bigtiff': 'IF_SAFER',
        'orthophoto_cutline': False,
        'build_overviews': False,
        'verbose_v': False,
        'time': False,
        'debug': False,
        'split': 999999,
        'split_overlap': 150,
        'sm_cluster': None,
        'merge': 'all',
        'force_gps': False,
    }
    texturing_nadir_weight = {
        'rural': 16,
        'urban': 24,
    }
    resize_to = {
        'full': -1,
        'half': image_max_side_size / 2,
        'quarter': image_max_side_size / 4,
        'eighth': image_max_side_size / 8,
    }

    defaults['resize_to'] = resize_to[args['resize_to']]
    defaults['texturing_nadir_weight'] = texturing_nadir_weight[args['texturing_nadir_weight']]

    defaults['opensfm_depthmap_method'] = args['opensfm_depthmap_method']
    defaults['opensfm_depthmap_min_consistent_views'] = args['opensfm_depthmap_min_consistent_views']
    defaults['pc_las'] = args['pc_las']
    defaults['dsm'] = args['dsm']
    defaults['dem_resolution'] = args['dem_resolution']
    defaults['orthophoto_resolution'] = args['orthophoto_resolution']
    defaults['min_num_features'] = args['min_num_features']

    if args['georeferencing'] == 'EXIF':
        defaults['use_exif'] = True
    elif args['georeferencing'] == 'GCP':
        defaults['use_exif'] = False

    return defaults

def upload_results():
    pass

def start(args: Dict) -> None:
    """Run orthophoto creation."""
    try:
        download_file = os.path.join(WORK_VOLUME, 'download', 'image.tif')
        extracted_dir = os.path.join(WORK_VOLUME, 'extracted')

        download(BD_HARDCODED_BASEMAP_UID, download_file)
        unzip(download_file, extracted_dir)

        image_props = get_image_properties(download_file)
        image_max_side_size = max(image_props['width'], image_props['height'])

        odm_args = to_odm_args(args, image_max_side_size=image_max_side_size)

        app = ODMApp(odm_args)
        app.execute()

        upload_results()

    except Exception as err:
        # TODO better error handling
        print('Oopsie!')
        print(err)
        exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create an orthophotos using OpenDroneMap',
        epilog='This tool is part of the Publish and Share platform'
    )

    '''Initialize arguments'''
    parser.add_argument('--resize-to', type=str, default='full',
                        choices=('full', 'half', 'quarter', 'eighth'),
                        help='resizes images by the largest side for opensfm.'
                             'Set to `full` to disable. Default: full')
    parser.add_argument('--opensfm-depthmap-method', type=str,
                        choices=(
                            'BRUTE_FORCE',
                            'PATCH_MATCH',
                            'PATCH_MATCH_SAMPLE'
                            ),
                        help='Raw depthmap computation algorithm. PATCH_MATCH '
                             'and PATCH_MATCH_SAMPLE are faster, but might '
                             'miss some valid points. BRUTE_FORCE takes '
                             'longer but produces denser reconstructions. '
                             'Default: PATCH_MATCH')
    parser.add_argument('--opensfm-depthmap-min-consistent-views', type=int,
                        default=3, choices=(3, 6),
                        help='Minimum number of views that should reconstruct '
                             'a point for it to be valid. Use lower values if '
                             'your images have less overlap. Lower values '
                             'result in denser point clouds but with more '
                             'noise. Default: 3')
    parser.add_argument('--texturing-nadir-weight',  type=str, required=True,
                        choices=('urban', 'rural'),
                        help='Affects orthophotos only.')
    parser.add_argument('--georeferencing', type=str, default='EXIF',
                        choices=('GCP', 'EXIF'),
                        help='Mode of georeferencing: either GCP, or EXIF.')
    parser.add_argument('--pc-las', action='store_true',
                        help='Export the georeferenced point cloud in LAS '
                             'format. Default: False')
    parser.add_argument('--dsm', action='store_true',
                        help='Use this tag to build a DSM (Digital Surface '
                             'Model, ground + objects) using a progressive '
                             'morphological filter. Default: False')
    parser.add_argument('--dem-resolution', type=float,
                        metavar='<float > 0.0>', default=5,
                        help='DSM/DTM resolution in cm / pixel. Default: 5')
    parser.add_argument('--orthophoto-resolution', type=float,
                        metavar='<float > 0.0>', default=5,
                        help='Orthophoto resolution in cm / pixel. Default: 5')
    parser.add_argument('--min-num-features', type=int, default=10000,
                        help='Minimum number of features to extract per '
                             'image. More features leads to better results '
                             'but slower execution. Default: 10000')

    args = parser.parse_args()

    start(vars(args))
