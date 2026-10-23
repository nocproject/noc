# ----------------------------------------------------------------------
# Utils for DataFormatter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import polars as pl


def replace_nested_datatypes(df):
    """
    Replaces columns with nested datatypes by they string representation.
    Needed for transform data from Dataframe to CSV-format.
    Now implemented only List(String) dtype.
    """
    ls_cols = [name for name, dtype in df.schema.items() if dtype == pl.List(pl.String)]
    ls_cols = [("[" + pl.col(cname).list.join(", ") + "]").alias(cname) for cname in ls_cols]
    return df.with_columns(ls_cols)
