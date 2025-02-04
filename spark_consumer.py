from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Define schema for the incoming data
schema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("bbox_x", IntegerType(), True),
    StructField("bbox_y", IntegerType(), True),
    StructField("bbox_width", IntegerType(), True),
    StructField("bbox_height", IntegerType(), True),
    StructField("emotion", StringType(), True)
])

# Create Spark session
spark = SparkSession.builder \
    .appName("EmotionAnalysis") \
    .config("spark.cassandra.connection.host", "localhost") \
    .config("spark.cassandra.connection.port", "9042") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

def write_to_cassandra(batch_df, batch_id):
    try:
        # Add UUID and convert timestamp
        batch_df_with_id = batch_df \
            .withColumn("id", expr("uuid()")) \
            .withColumn("timestamp", to_timestamp(col("timestamp"))) \
            .select(
                "id",
                "bbox_height",
                "bbox_width",
                "bbox_x",
                "bbox_y",
                "emotion",
                "timestamp"
            )
        
        # Write to Cassandra
        batch_df_with_id.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .options(table="emotion_data", keyspace="emotion_tracking") \
            .save()
        
        print(f"Successfully wrote batch {batch_id} to Cassandra")
    except Exception as e:
        print(f"Error writing to Cassandra: {str(e)}")

try:
    # Read from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "face-emotions") \
        .option("startingOffsets", "earliest") \
        .load()

    # Process the data
    parsed_df = df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*")

    # Write to console for debugging
    console_query = parsed_df \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .start()

    # Write to Cassandra
    cassandra_query = parsed_df \
        .writeStream \
        .foreachBatch(write_to_cassandra) \
        .option("checkpointLocation", "/tmp/checkpoint") \
        .start()

    spark.streams.awaitAnyTermination()

except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    spark.stop()