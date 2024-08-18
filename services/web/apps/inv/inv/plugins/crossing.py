# ---------------------------------------------------------------------
# inv.inv crossing plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, Any, Set
from collections import defaultdict

# NOC modules
from .base import InvPlugin
from noc.inv.models.object import Object
from noc.core.text import alnum_key


class CrossingPlugin(InvPlugin):
    name = "crossing"
    js = "NOC.inv.inv.plugins.crossing.CrossingPanel"

    def get_data(self, request, o: Object) -> Dict[str, Any]:
        crossings = list(o.iter_effective_crossing())
        data = [
            {
                "id": f"c_{n}",
                "input": c.input,
                "input_discriminator": c.input_discriminator,
                "output": c.output,
                "output_discriminator": c.output_discriminator,
                "gain_db": c.gain_db,
            }
            for n, c in enumerate(crossings)
        ]
        #
        n_input_discriminators = defaultdict(int)
        for c in crossings:
            if c.input_discriminator:
                n_input_discriminators[c.input] += 1
        # Build list
        inputs: Set[str] = set()
        outputs: Set[str] = set()
        mixed: Set[str] = set()
        for c in crossings:
            # Process inputs
            if c.input not in mixed:
                inputs.add(c.input)
                if c.input in outputs:
                    inputs.remove(c.input)
                    outputs.remove(c.input)
                    mixed.add(c.input)
            # Process outputs
            if c.output not in mixed:
                outputs.add(c.output)
                if c.output in inputs:
                    inputs.remove(c.output)
                    outputs.remove(c.output)
                    mixed.add(c.output)
        # Build graph
        viz = {
            "graphAttributes": {
                "label": "",
                "bgcolor": "",
                "rankdir": "LR",
            },
            "directed": True,
            "nodes": [],
            "edges": [],
            "subgraphs": [],
        }
        viz["nodes"].append(self._render_node("i", inputs))
        viz["nodes"].append(self._render_node("o", outputs))
        if mixed:
            viz["nodes"].append(self._render_node("m", mixed))
        # Add edges
        for n, c in enumerate(crossings):
            edge = {
                "head": "o" if c.output in outputs else "m",
                "tail": "i" if c.input in inputs else "m",
                "attributes": {
                    "headport": c.output,
                    "tailport": c.input,
                    "class": "selectable",
                    "id": f"c_{n}",
                },
            }
            label_parts = []
            if c.input_discriminator and n_input_discriminators[c.input] == 1:
                # Single discriminator, generate virtual edge
                viz["nodes"].append({"name": f"vi_{c.input}", "attributes": {"shape": "point"}})
                viz["edges"].append(
                    {
                        "head": "i" if c.input in inputs else "m",
                        "tail": f"vi_{c.input}",
                        "attributes": {"headport": c.input, "label": c.input_discriminator},
                    }
                )
            elif c.input_discriminator:
                # Multiple discriminators
                label_parts.append(c.input_discriminator)
            if c.output_discriminator:
                label_parts.append(c.output_discriminator)
            if label_parts:
                edge["attributes"]["label"] = " ".join(label_parts)
            viz["edges"].append(edge)
        return {"id": str(o.id), "data": data, "viz": viz}

    def _render_node(self, name: str, items: Set[str]) -> Dict[str, Any]:
        """
        Render Viz node
        """
        label = "|".join(f"<{n}>{n}" for n in sorted(items, key=alnum_key))
        return {"name": name, "attributes": {"shape": "record", "label": label}}
