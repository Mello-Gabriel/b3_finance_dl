import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsgluedq.transforms import EvaluateDataQuality
from awsglue import DynamicFrame

def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Default ruleset used by all target nodes with data quality enabled
DEFAULT_DATA_QUALITY_RULESET = """
    Rules = [
        ColumnCount > 0
    ]
"""

# Script generated for node Amazon S3
AmazonS3_node1767307374518 = glueContext.create_dynamic_frame.from_options(format_options={}, connection_type="s3", format="parquet", connection_options={"paths": ["s3://techchallenge-02-gabriel/raw/"], "recurse": True}, transformation_ctx="AmazonS3_node1767307374518")

# Script generated for node SQL Query
SqlQuery1514 = '''
select
ticker as empresa,
avg(close) as media_fechamento,
month as mes
from acoes_b3
group by ticker, month
order by mes, empresa
'''
SQLQuery_node1767309088778 = sparkSqlQuery(glueContext, query = SqlQuery1514, mapping = {"acoes_b3":AmazonS3_node1767307374518}, transformation_ctx = "SQLQuery_node1767309088778")

# Script generated for node Amazon S3
EvaluateDataQuality().process_rows(frame=SQLQuery_node1767309088778, ruleset=DEFAULT_DATA_QUALITY_RULESET, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1767305597745", "enableDataQualityResultsPublishing": True}, additional_options={"dataQualityResultsPublishing.strategy": "BEST_EFFORT", "observations.scope": "ALL"})
AmazonS3_node1767309372301 = glueContext.getSink(path="s3://techchallenge-02-gabriel/refined/", connection_type="s3", updateBehavior="UPDATE_IN_DATABASE", partitionKeys=["empresa", "mes"], enableUpdateCatalog=True, transformation_ctx="AmazonS3_node1767309372301")
AmazonS3_node1767309372301.setCatalogInfo(catalogDatabase="default",catalogTableName="b3_analytics")
AmazonS3_node1767309372301.setFormat("glueparquet", compression="snappy")
AmazonS3_node1767309372301.writeFrame(SQLQuery_node1767309088778)
job.commit()