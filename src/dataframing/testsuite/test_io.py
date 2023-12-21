import math

import dataframing as dfr
import numpy as np
import pandas as pd


def test_load_save(tmp_path):
    filename = str(tmp_path / "test.demo.xlsx")
    df = pd.DataFrame(
        [
            dict(last_name="Cleese", first_name="John"),
            dict(last_name="Gilliam", first_name="Terry"),
            dict(last_name=math.pi, first_name=np.nan),
        ]
    )
    dfr.save(df, filename)
    stored = dfr.load(filename, use_hash=False)
    assert df.equals(stored)
    assert dfr.io.hash_dataframe(df) == dfr.io.hash_dataframe(stored)
    try:
        stored = dfr.load(filename)
    except Exception:
        pass
