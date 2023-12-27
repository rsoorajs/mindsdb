import hashlib

from mindsdb_sql.planner.steps import UnionStep

from mindsdb.api.executor.sql_query.result_set import ResultSet
from mindsdb.api.mysql.mysql_proxy.utilities import ErSqlWrongArguments

from .base import BaseStepCall


class UnionStepCall(BaseStepCall):

    bind = UnionStep

    def call(self, step):
        left_result = self.steps_data[step.left.step_num]
        right_result = self.steps_data[step.right.step_num]

        # count of columns have to match
        if len(left_result.columns) != len(right_result.columns):
            raise ErSqlWrongArguments(
                f'UNION columns count mismatch: {len(left_result.columns)} != {len(right_result.columns)} ')

        # types have to match
        # TODO: return checking type later
        # for i, left_col in enumerate(left_result.columns):
        #     right_col = right_result.columns[i]
        #     type1, type2 = left_col.type, right_col.type
        #     if type1 is not None and type2 is not None:
        #         if type1 != type2:
        #             raise ErSqlWrongArguments(f'UNION types mismatch: {type1} != {type2}')

        result = ResultSet()
        for col in left_result.columns:
            result.add_column(col)

        records_hashes = []
        for row in left_result.get_records_raw() + right_result.get_records_raw():
            if step.unique:
                checksum = hashlib.sha256(str(row).encode()).hexdigest()
                if checksum in records_hashes:
                    continue
                records_hashes.append(checksum)
            result.add_record_raw(row)

        return result
