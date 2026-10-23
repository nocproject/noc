# ----------------------------------------------------------------------
# CLI Command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
import argparse
from typing import Never, TextIO, TypeVar
from collections.abc import Sequence, Iterable, Iterator
from pathlib import Path
import resource

# Third-party modules
from gufo.loader import Loader

# NOC modules
from noc.config import config

T = TypeVar("T")


class CommandError(Exception):
    pass


class BaseCommand:
    LOG_FORMAT = config.log_format
    help = ""  # Help text (shows ./noc help)

    def __init__(self, stdout: TextIO | None = None, stderr: TextIO | None = None) -> None:
        self.verbose_level = 0
        self.stdout: TextIO = sys.stdout if stdout is None else stdout
        self.stderr: TextIO = sys.stderr if stderr is None else stderr

    def print(
        self,
        *args: object,
        sep: str | None = " ",
        end: str | None = "\n",
        file: TextIO | None = None,
        flush: bool = False,
    ) -> None:
        """Print values to the configured output stream.

        This method behaves like the built-in ``print`` function, but uses
        the instance configured output stream when ``file`` is not specified.

        The output stream can be replaced for testing purposes by passing
        a custom ``TextIO`` object to the constructor, allowing tests to
        capture and verify printed output without redirecting process-wide
        stdout.

        Args:
            *args: Values to print.
            sep: String inserted between values.
            end: String appended after the last value.
            file: Output stream. Uses the configured output stream by default.
            flush: Whether to forcibly flush the output stream.
        """
        print(*args, sep=sep, end=end, file=self.stdout if file is None else file, flush=flush)

    def run(self) -> Never:
        """
        Execute the command using command-line arguments.

        This method is intended to be called from a command-line entry point
        or a script main block.

        Example:

        ```python
        if __name__ == "__main__":
            Command().run()
        ```

        The method terminates the process with the exit code returned by
        `run_from_argv`.
        """
        sys.exit(self.run_from_argv(sys.argv[1:]))

    def run_from_argv(self, argv: Sequence[str]) -> int:
        """
        Execute the command using the provided command-line arguments.

        This method parses and executes a command using the specified
        argument list and returns the process exit code.

        It can be used from a command-line entry point or a script main block.

        Example:

        ```python
        if __name__ == "__main__":
            import sys

            sys.exit(Command().run_from_argv(sys.argv[1:]))
        ```
        """
        parser = self.create_parser()
        self.add_default_arguments(parser)
        self.add_arguments(parser)
        options = parser.parse_args(argv)
        cmd_options = vars(options)
        args = cmd_options.pop("args", ())
        loglevel = cmd_options.pop("loglevel")
        if loglevel:
            config.loglevel = loglevel
        enable_profiling = cmd_options.pop("enable_profiling", False)
        show_metrics = cmd_options.pop("show_metrics", False)
        show_usage = cmd_options.pop("show_usage", False)
        self.no_progressbar = cmd_options.pop("no_progressbar", False)
        # Apply config settings
        config.setup()
        # Run
        if enable_profiling:
            # Start profiler
            import yappi

            yappi.start()
        try:
            if show_usage:
                import resource

                start_usage = resource.getrusage(resource.RUSAGE_SELF)
            return self.handle(*args, **cmd_options) or 0
        except CommandError as e:
            self.print(str(e))
            return 1
        except KeyboardInterrupt:
            self.print("Ctrl+C")
            return 3
        except AssertionError as e:
            if e.args and e.args[0]:
                self.print(f"ERROR: {e.args[0]}")
            else:
                self.print(f"Assertion error: {e}")
            return 4
        except Exception:
            from noc.core.debug import error_report

            error_report()
            return 2
        finally:
            if show_usage:
                stop_usage = resource.getrusage(resource.RUSAGE_SELF)
                self.show_usage(start_usage, stop_usage)
            if enable_profiling:
                i = yappi.get_func_stats()
                i.print_all(
                    out=self.stdout,
                    columns={
                        0: ("name", 80),
                        1: ("ncall", 10),
                        2: ("tsub", 8),
                        3: ("ttot", 8),
                        4: ("tavg", 8),
                    },
                )
            if show_metrics:
                from noc.core.perf import apply_metrics

                d = apply_metrics({})
                self.print("Internal metrics:")
                for k in d:
                    self.print(f"{k:>40} : {d[k]}")

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the command-line argument parser.

        The program name is derived from `sys.argv[0]`. For Python scripts,
        the `.py` suffix is removed and the command name is prefixed with
        `noc`.

        Returns:
            Configured argument parser instance.
        """
        cmd = Path(sys.argv[0]).name
        if cmd.endswith(".py"):
            cmd = f"noc {cmd[:-3]}"
        return argparse.ArgumentParser(prog=cmd)

    def handle(self, *args, **options):
        """
        Execute command
        """

    def add_default_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add common command-line arguments to the parser.

        Adds options shared by all commands, including logging configuration,
        profiling, metrics output, progress bar control, and resource usage
        reporting.

        Args:
            parser: Argument parser to extend with default command options.
        """
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--loglevel",
            action="store",
            dest="loglevel",
            help="Set loglevel",
            choices=["critical", "error", "warning", "info", "debug", "none"],
            default="info",
        )
        group.add_argument(
            "--quiet", action="store_const", dest="loglevel", const="none", help="Suppress logging"
        )
        group.add_argument(
            "--debug", action="store_const", dest="loglevel", const="debug", help="Debugging output"
        )
        group.add_argument(
            "--enable-profiling", action="store_true", help="Enable built-in profiler"
        )
        group.add_argument("--show-metrics", action="store_true", help="Dump internal metrics")
        group.add_argument("--no-progressbar", action="store_true", help="Disable progressbar")
        group.add_argument(
            "--show-usage", action="store_true", help="Dump resource usage statistics"
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Add command-specific arguments to the parser.

        This method can be overridden by subclasses to register additional
        command-line options specific to the command implementation.

        Args:
            parser: Argument parser to extend with command-specific options.
        """

    def die(self, msg: str) -> Never:
        """
        Terminate command execution by raising a command error.

        Args:
            msg: Error message describing the command failure.

        Raises:
            CommandError: Always raised with the provided error message.
        """
        raise CommandError(msg)

    def progress(self, iterable: Iterable[T], max_value: int | None = None) -> Iterator[T]:
        """Wrap an iterable with a progress bar.

        The progress bar can be disabled using the ``no_progressbar`` option.
        When disabled, items are yielded directly from the original iterable.

        Args:
            iterable: Iterable to process while displaying progress.
            max_value: Optional total number of items for the progress bar.

        Yields:
            Items from the input iterable.
        """
        if self.no_progressbar:
            yield from iterable
        else:
            import progressbar

            yield from progressbar.progressbar(iterable, max_value=max_value)

    def show_usage(self, start: resource.struct_rusage, stop: resource.struct_rusage) -> None:
        """Show resource usage statistics.

        Displays the difference between two resource usage snapshots.

        Args:
            start: Resource usage snapshot taken before the operation.
            stop: Resource usage snapshot taken after the operation.
        """
        r = [
            "Resource usage:",
            f"             User time   : {stop.ru_utime - start.ru_utime:.6f}",
            f"             System time : {stop.ru_stime - start.ru_stime:.6f}",
            f"             Max RSS     : {stop.ru_maxrss - start.ru_maxrss}k",
            f"        Shared mem. size : {stop.ru_ixrss - start.ru_ixrss}k",
            f"      Unshared mem. size : {stop.ru_idrss - start.ru_idrss}k",
            f"     Unshared stack size : {stop.ru_isrss - start.ru_isrss}k",
            f"    Page faults w/o. I/O : {stop.ru_minflt - start.ru_minflt}",
            f"      Page faults w. I/O : {stop.ru_majflt - start.ru_majflt}",
            f"               Swap outs : {stop.ru_nswap - start.ru_nswap}",
            f"               In blocks : {stop.ru_inblock - start.ru_inblock}",
            f"              Out blocks : {stop.ru_oublock - start.ru_oublock}",
            f"           Messages sent : {stop.ru_msgsnd - start.ru_msgsnd}",
            f"       Messages received : {stop.ru_msgrcv - start.ru_msgrcv}",
            f"                 Signals : {stop.ru_nsignals - start.ru_nsignals}",
            f"   Voluntary context sw. : {stop.ru_nvcsw - start.ru_nvcsw}",
            f" Involuntary context sw. : {stop.ru_nivcsw - start.ru_nivcsw}",
        ]
        self.print("\n".join(r))

    @property
    def is_debug(self) -> bool:
        return config.loglevel <= 10  # logging.DEBUG


command_loader = Loader[type[BaseCommand]](bases=config.iter_customized_bases("noc.commands"))
