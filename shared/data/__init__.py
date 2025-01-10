"""Provides loaders for competition data and utilities to manipulate the data."""

from .manipulation import (
    create_flat_dataset,
    merge_unflat_datasets,
    merge_flat_datasets,
    attemped_mapping,
    ids_by_total_points
)

__all__ = [
    "create_flat_dataset", 
    "merge_unflat_datasets",
    "merge_flat_datasets", 
    "attemped_mapping", 
    "ids_by_total_points"
]
