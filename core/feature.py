# ----------------------------------------------------------------------
# Feature Gate implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from typing import List, Optional, Set
import logging

# NOC modules
from noc.config import config

logger = logging.getLogger(__name__)


class FeatureStatus(enum.Enum):
    """
    Feature status.

    Attributes:
       ALPHA: Alpha feature - in implementation.
       BETA: Beta feature - in testing.
       MATURE: Mature feature - stable and production ready.
    """

    ALPHA = enum.auto()
    BETA = enum.auto()
    MATURE = enum.auto()


class Feature(enum.Enum):
    """
    Feature gate.

    Contains list of all available features.

    Attributes:
        CHANNEL: Channel management.
        JOBS: Orchestrator jobs.
    """

    CHANNEL = "channel"
    JOBS = "jobs"

    def is_active(self) -> bool:
        """Check if feature is active."""
        return has_feature(self)


_FEATURE_STATUS = {Feature.CHANNEL: FeatureStatus.ALPHA, Feature.JOBS: FeatureStatus.ALPHA}
_FEATURE_DEFAULT = {Feature.CHANNEL: False, Feature.JOBS: False}
_current_features: Optional[Set[Feature]] = None


def active_features() -> List[Feature]:
    """
    Return list of currently active features.
    """
    return list(_get_features())


def has_feature(feature: Feature) -> bool:
    """
    Check if feature is enabled.
    Args:
        feature (Feature): Feature to check
    Returns:
        bool: True if feature is enabled, False otherwise
    """
    return feature in _get_features()


def _get_features() -> Set[Feature]:
    """Parse features and populate _CURRENT_FEATURES"""
    global _current_features

    if _current_features is not None:
        return _current_features
    # Features enabled by default
    print(config.features.gate)
    r = {f for f in _FEATURE_DEFAULT if _FEATURE_DEFAULT[f]}
    for fx in config.features.gate:
        fx = fx.strip()
        if not fx:
            continue
        if fx.startswith("-"):
            # Negate
            try:
                feature = Feature(fx[1:])
                r.discard(feature)
            except ValueError:
                logger.info("Unknown feature '%s', ignoring", fx[1:])
        else:
            try:
                feature = Feature(fx)
                r.add(feature)
            except ValueError:
                logger.info("Unknown feature '%s', ignoring", fx)
    _current_features = frozenset(r)
    if _current_features:
        logger.info("Activated features: %s", ", ".join(f.value for f in _current_features))
        for feature in _current_features:
            fs = _FEATURE_STATUS.get(feature, None)
            if not fs:
                continue
            if fs == FeatureStatus.ALPHA:
                logger.warning(
                    "Feature '%s' is ALPHA and may be unstable",
                    feature.value,
                )
            elif fs == FeatureStatus.BETA:
                logger.warning("Feature '%s' is BETA and may have bugs", feature.value)
    return _current_features
