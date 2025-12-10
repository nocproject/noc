# ----------------------------------------------------------------------
# Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, List

# Third-party modules
import jinja2

rx_empty_string = re.compile(r"\n{2,}")


@dataclass
class ScopeConfig:
    """
    Action Configuration Scope
    Attributes:
        name: Scope name
        value:
    """

    name: str
    value: str
    command: Optional[str] = None
    exit_command: Optional[str] = None
    enter: bool = True

    def update_config(self, config: "ScopeConfig"):
        if config.command is not None:
            self.command = config.command
        # if config.exit_command is not None:
        self.exit_command = config.exit_command
        self.enter = config.enter


@dataclass
class ActionCommandConfig:
    """
    Config Action for render command
    Attributes:
        name: Action name
        commands: Configuration command template
        scopes:
    """

    name: str
    commands: str
    config_mode: bool = False
    scopes: Optional[List[ScopeConfig]] = None
    cancel_prefix: Optional[str] = None

    def render_command(
        self,
        commands: str,
        add_cancel: bool = False,
        **ctx: Dict[str, Any],
    ):
        """"""
        loader = jinja2.DictLoader({"tpl": commands})
        env = jinja2.Environment(loader=loader)
        template = env.get_template("tpl")
        if add_cancel:
            return f"{self.cancel_prefix} {template.render(**ctx)}"
        return template.render(**ctx)

    def render(
        self,
        ctx: Dict[str, Any],
        scope_prepend: str = " ",
        enable_commands: Optional[List[str]] = None,
        disable_commands: Optional[List[str]] = None,
        clean_empty_string: bool = True,
        ignore_scope: bool = False,
        cancel: bool = False,
        cancel_prefix: Optional[str] = None,
    ):
        """
        Args:
            ctx: Context for Render commands
            scope_prepend: Add for commands string within scope
            clean_empty_string: Clean empty strings in commands output (for template)
            enable_commands: Execute when enter scope
            disable_commands: Execute when exist scope
            ignore_scope: Render commands only, without enter scope context
            cancel:
            cancel_prefix: Prefix for cancel commands. Example - 'no'
        """
        r, exits = [], []
        cancel_prefix = cancel_prefix or self.cancel_prefix
        inputs = {"scope_prefix": [], "scope_prepend": scope_prepend}
        inputs |= ctx
        if enable_commands:
            inputs["enable_command"] = "\n".join(enable_commands)
        if disable_commands:
            inputs["disable_command"] = "\n".join(disable_commands)
        elif enable_commands and self.cancel_prefix:
            inputs["disable_command"] = f"{cancel_prefix} {inputs['enable_command']}"
        # If render cancel - cancel scope only
        for s in self.scopes or []:
            if ignore_scope:
                continue
            if not s.command:
                # Append space ?
                continue
            s_command = self.render_command(s.command, add_cancel=cancel, **inputs)
            if s.enter:
                r.append(s_command)
            inputs["scope_prefix"] += [s_command]
            if cancel:
                return r
            if s.exit_command:
                exits.append(s.exit_command)
        inputs["scope_prefix"] = " ".join(inputs["scope_prefix"])
        command = self.render_command(self.commands, add_cancel=cancel, **inputs)
        if clean_empty_string:
            command = rx_empty_string.sub("\n", command)
        if command:
            r.append(command)
        r += exits
        return r
