# ----------------------------------------------------------------------
# Rule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
from dataclasses import dataclass
from typing import Any, Optional, Dict, List, Iterable, Set
import logging
import re

# Third-party modules
import pydantic

# NOC modules
from noc.core.cdag.node.base import BaseCDAGNode
from noc.core.cdag.node.loader import loader
from noc.pm.models.metrictype import MetricType
from noc.pm.models.metricaction import MetricAction
from noc.pm.models.metricrule import MetricRule

logger = logging.getLogger(__name__)
rx_exp = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")


@dataclass
class RuleItem(object):
    # CDAG Nodes and Config
    metric_type: MetricType
    compose_node: Optional[BaseCDAGNode] = None
    compose_inputs: Optional[Dict[str, str]] = None
    activation_node_window: Optional[BaseCDAGNode] = None
    activation_node_activation: Optional[BaseCDAGNode] = None
    deactivation_node_window: Optional[BaseCDAGNode] = None
    deactivation_node_activation: Optional[BaseCDAGNode] = None
    key_node: Optional[BaseCDAGNode] = None
    alarm_node: Optional[BaseCDAGNode] = None


@dataclass
class Rule(object):
    match_labels: Set[str]
    items: List[RuleItem]

    def is_matched(self, labels: Set[str]) -> bool:
        return labels.issuperset(self.match_labels)


_rules: Optional[List[Rule]] = None


def iter_rules(scope_name: str, labels: List[str]) -> Iterable[RuleItem]:
    """
    Iterate all applicable rule items
    """
    s_labels = set(labels)
    for rule in _get_rules():
        if not rule.is_matched(s_labels):
            continue
        for item in rule.items:
            if item.metric_type.scope.table_name == scope_name:
                yield item


def _get_rules() -> List[Rule]:
    """
    Get list of rules
    """
    global _rules
    if _rules is not None:
        return _rules
    r: List[Rule] = []
    for mr in MetricRule.objects.filter(is_active=True):
        r.append(
            Rule(
                match_labels=set(sys.intern(label) for label in mr.match_labels),
                items=list(_iter_items(mr)),
            )
        )
    _rules = r
    return r


def _iter_items(mr: "MetricRule") -> Iterable[RuleItem]:
    """
    Prepare metric rule items
    """
    for r_item in mr.items:
        if not r_item.is_active:
            continue
        action: "MetricAction" = r_item.metric_action
        metric_type = None
        # Prepare params
        # missed_params = set()
        # mr_config: Dict[str, Any] = r_item.config or {}
        # params: Dict[str, Any] = {}
        # for param in action.params:
        #     pv = mr_config.get(param.name)
        #     if pv is None:
        #         missed_params.add(param.name)
        #     else:
        #         params[param.name] = pv
        # if missed_params:
        #     logger.error(
        #         "Broken rule `%s`. Missed params for action %s: %s. Skipping",
        #         mr.name,
        #         action.name,
        #         ", ".join(missed_params),
        #     )
        #     continue
        params: Dict[str, Any] = {}
        # compose
        compose_inputs = {}
        for num, ci in enumerate(action.compose_inputs):
            if not num:
                metric_type = ci.metric_type
                continue
            compose_inputs[sys.intern(ci.metric_type.field_name)] = sys.intern(f"in{num}")
        compose_node = None
        if action.compose_function:
            compose_node = _get_node(
                action.compose_node,
                f"{mr.name}-{action.name}-c",  # a_item.compose_config, params
            )
            if not compose_node:
                logger.error(
                    "Broken rule `%s`. Cannot create compose node for action `%s`. Skipping",
                    mr.name,
                    action.name,
                )
        # activation
        activation_node_window, activation_node_activation = None, None
        if action.activation_config:
            if action.activation_config.window_function:
                config = {
                    "min_window": action.activation_config.min_window,
                    "max_window": action.activation_config.max_window,
                }
                config.update(action.activation_config.window_config)
                activation_node_window = _get_node(
                    action.activation_config.window_function,
                    f"{mr.name}-{action.name}-ac-wf",
                    config,
                    params,
                )
                if not activation_node_window:
                    logger.error(
                        "Broken rule `%s`. Cannot create activation node for action `%s`. Skipping",
                        mr.name,
                        action.name,
                    )
            if action.activation_config.activation_function:
                activation_node_activation = _get_node(
                    action.activation_config.activation_node_activation,
                    f"{mr.name}-{action.name}-ac-af",
                    action.activation_config.activation_config,
                    params,
                )
                if not activation_node_activation:
                    logger.error(
                        "Broken rule `%s`. Cannot create activation node for action `%s`. Skipping",
                        mr.name,
                        action.name,
                    )
        # Deactivation
        deactivation_node_window, deactivation_node_activation = None, None
        if action.deactivation_config:
            if action.deactivation_config.window_function:
                config = {
                    "min_window": action.deactivation_config.min_window,
                    "max_window": action.deactivation_config.max_window,
                }
                config.update(action.deactivation_config.window_config)
                deactivation_node_window = _get_node(
                    action.deactivation_config.window_function,
                    f"{mr.name}-{action.name}-ac-wf",
                    config,
                    params,
                )
                if not deactivation_node_window:
                    logger.error(
                        "Broken rule `%s`. Cannot create activation node for action `%s`. Skipping",
                        mr.name,
                        action.name,
                    )
            if action.deactivation_config.activation_function:
                deactivation_node_activation = _get_node(
                    action.deactivation_config.activation_node_activation,
                    f"{mr.name}-{action.name}-ac-af",
                    action.deactivation_config.activation_config,
                    params,
                )
                if not deactivation_node_activation:
                    logger.error(
                        "Broken rule `%s`. Cannot create activation node for action `%s`. Skipping",
                        mr.name,
                        action.name,
                    )
        # alarm
        alarm_node = None
        if action.alarm_config:
            alarm_node = _get_node(
                "alarm", f"{mr.name}-{action.name}-al", {
                    "alarm_class": action.alarm_config.alarm_class.name,
                    "reference": action.alarm_config.reference
                }, params
            )
        if not metric_type:
            # Metric Type is not set
            logger.error("[%s|%s] Nothing inputs. Skipping", mr.name, action.name)
            continue
        yield RuleItem(
            metric_type=metric_type,
            compose_node=compose_node,
            compose_inputs=compose_inputs,
            activation_node_window=activation_node_window,
            activation_node_activation=activation_node_activation,
            deactivation_node_window=deactivation_node_window,
            deactivation_node_activation=deactivation_node_activation,
            alarm_node=alarm_node,
        )


def _expand_config(
    config_template: Optional[Dict[str, Any]], params: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Apply params to template config
    """
    if not config_template:
        return None
    if not params:
        return config_template
    r: Dict[str, Any] = {}
    for tn, tv in config_template.items():
        if isinstance(tv, str):
            try:
                tv = rx_exp.sub(lambda match: params[match.group(1)], tv)
            except KeyError:
                logger.error("Invalid parameter: %s", tv)
                return None
    return r


def _get_node(
    node: str,
    node_id: str,
    config_template: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Optional[BaseCDAGNode]:
    """
    Create node from config template and params
    """
    cfg = _expand_config(config_template=config_template, params=params)
    node_cls = loader.get_class(node)
    if not node_cls:
        logger.error("Invalid node class `%s`", node)
        return None
    try:
        return node_cls.construct(node_id, config=cfg)
    except pydantic.ValidationError as e:
        logger.error("Cannot create node `%s`: %s", node, e)
        return None
