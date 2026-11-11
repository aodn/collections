from .cloud_optimised_physical_dataset import CloudOptimisedPhysicalDataset
from .object_physical_dataset import ObjectPhysicalDataset

PhysicalDataset = ObjectPhysicalDataset | CloudOptimisedPhysicalDataset

__all__ = [
    "CloudOptimisedPhysicalDataset",
    "ObjectPhysicalDataset",
    "PhysicalDataset",
]
