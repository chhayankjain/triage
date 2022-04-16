import datetime
import verboselogs
from triage.component.architect.entity_date_table_generators import EntityDateTableGenerator
from typing import List, Optional

logger = verboselogs.VerboseLogger(__name__)

import pydantic

class CohortInspectionResults(pydantic.BaseModel):
    ran_successfully: bool
    num_rows: int
    distinct_entity_ids: int
    examples: List[str]

def inspect_cohort_query_on_date(query: str, db_engine, as_of_date: datetime.date):
    cohort_table_name = 'temp_inspect_cohort'
    generator = EntityDateTableGenerator(
        query=query,
        db_engine=db_engine,
        entity_date_table_name=cohort_table_name,
        replace=True
    )
    results = {}
    logger.info('Inspecting cohort query at %s', query)
    generator.generate_entity_date_table([as_of_date])
    logger.info('Cohort query successfully ran')
    results['ran_successfully'] = True
    results['num_rows'] = list(db_engine.execute(
        f'select count(*) from {cohort_table_name} where as_of_date = %s',
        as_of_date))[0][0]
    results['distinct_entity_ids'] = list(db_engine.execute(
        f'select count(distinct(entity_id)) from {cohort_table_name} where as_of_date = %s',
        as_of_date))[0][0]

    results['examples'] = sorted([
        row[0]
        for row in db_engine.execute(f'select entity_id from {cohort_table_name} ORDER BY random() limit 5')
    ])
    return CohortInspectionResults(**results)
