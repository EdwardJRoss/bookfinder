import json
import logging
from typing import BinaryIO

import numpy as np
import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Index, Series

from .transform import ParentSchema, clean_text, enrich_root, hash_bucket

logger = logging.getLogger(__name__)


class HNSchema(pa.SchemaModel):
    id: Index[int]
    parent: Series[int] = pa.Field(nullable=True)
    text: Series[str] = pa.Field(nullable=True)
    title: Series[str] = pa.Field(nullable=True)


def read_hn_data(path: BinaryIO) -> DataFrame[HNSchema]:
    df = (
        pd.read_parquet(path)
        .set_index("id")
        .assign(parent=lambda df: df["parent"].astype("Int64"))
        .query("dead.isna() & deleted.isna()")
        .pipe(DataFrame[HNSchema])
    )
    return df


def main(in_path: str, out_path: str) -> None:
    logger.info("Reading file")
    with open(in_path, "rb") as f:
        raw_df = read_hn_data(f)

    logger.info("Enriching root")
    df = enrich_root(raw_df.pipe(DataFrame[ParentSchema]))

    logger.info("Calculating hash bucket")
    df["bucket"] = df["root"].astype(float).apply(hash_bucket)

    logger.info("Cleaning text")
    df["clean_text"] = (
        np.where(df.title.isna(), "", df.title)
        + np.where(~df.title.isna() & ~df.text.isna(), "<p>", "")
        + df.text.fillna("")
    ).apply(clean_text)

    logger.info("Filtering to buckets < 50 and children")
    df_filtered = (
        df.query("bucket < 50")
        .query("~parent.isna()")
        .sample(frac=1, random_state=7191)
    )

    logger.info("Writing to jsonl")
    with open(out_path, "w") as f:
        for id, row in df_filtered.iterrows():
            data = {"text": row["clean_text"], "meta": {"id": id}}
            print(json.dumps(data), file=f)

    logger.info("Done")


if __name__ == "__main__":
    # Configure basic logging with timestamp
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    import sys

    main(sys.argv[1], sys.argv[2])
