# ----------------------------------------------------------------------
# Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, List, Tuple

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
    after_enter: Optional[str] = None
    before_exit: Optional[str] = None
    enter: bool = True

    def update_config(self, config: "ScopeConfig"):
        if config.command is not None:
            self.command = config.command
        # if config.exit_command is not None:
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
    exit_command: Optional[str] = None

    @classmethod
    def render_command(cls, commands: str, **ctx: Dict[str, Any]):
        """"""
        loader = jinja2.DictLoader({"tpl": commands})
        env = jinja2.Environment(loader=loader)
        template = env.get_template("tpl")
        return template.render(**ctx)

    def render_scope(self, **inputs) -> Tuple[List[str], Dict[str, str]]:
        """Render Scope"""
        r, r_ctx = [], {}
        for s in self.scopes or []:
            if not s.command:
                # Append space ?
                continue
            ctx = {s.name: s.value}
            ctx |= inputs
            r_ctx |= ctx
            s_command = self.render_command(s.command, **ctx)
            if s.enter:
                r.append(s_command)
        return r, r_ctx

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
        r, scopes_c = [], []
        cancel_prefix = cancel_prefix or self.cancel_prefix
        inputs = {"scope_prefix": "", "scope_prepend": scope_prepend}
        inputs |= ctx
        if enable_commands:
            inputs["enable_command"] = "\n".join(enable_commands)
        if disable_commands:
            inputs["disable_command"] = "\n".join(disable_commands)
        elif enable_commands and self.cancel_prefix:
            inputs["disable_command"] = f"{cancel_prefix} {inputs['enable_command']}"
        # If render cancel - cancel scope only
        scopes_c, s_ctx = self.render_scope(**ctx)
        inputs["scope_prefix"] = " ".join(scopes_c)
        inputs |= s_ctx
        if not ignore_scope:
            r += scopes_c
        command = self.render_command(self.commands, **inputs)
        if cancel and self.cancel_prefix:
            return [f"{self.cancel_prefix} {command}"]
        if clean_empty_string:
            command = rx_empty_string.sub("\n", command)
        if command.strip():
            r.append(command)
        if self.exit_command and not ignore_scope:
            # Len Scopes for
            r += [self.exit_command] * len(scopes_c)
        return r
