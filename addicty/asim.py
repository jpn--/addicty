from .configurator import IsPath, IsA, IsSubconfig, Configuration
from collections.abc import Sequence, Mapping

class InputTable(Configuration):

    """
      - tablename: households
    filename: households.csv
    index_col: household_id
    rename_columns:
      HHID: household_id  # household_id is the required index column
      PERSONS: hhsize
      workers: num_workers
      VEHICL: auto_ownership
      TAZ: home_zone_id
    keep_columns:
      - home_zone_id
      - income
      - hhsize
      - HHT
      - auto_ownership
      - num_workers

    """
    tablename = IsA(str)
    filename = IsA(str)
    index_col = IsA(str)
    rename_columns = IsA(Mapping)
    keep_columns = IsA(Sequence)


class Setting(Configuration):

    input_table_list = IsA(list[InputTable])