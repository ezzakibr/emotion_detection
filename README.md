# Real-time Emotion Detection System

This project demonstrates a real-time emotion detection pipeline using modern data engineering tools. Let's break down how it works and why each component is important.

## System Architecture & Data Flow

### 1. Data Capture & Emotion Detection (emotion_detector.py)
This is where everything starts. Using your webcam, the system:
- Captures video frames in real-time
- Uses OpenCV to detect faces in these frames
- Analyzes each face to determine the emotion (Happy, Sad, or Neutral)
- Records important data for each detection:
 * Face position (x, y coordinates) 
 * Face size (width, height)
 * Detected emotion
 * Timestamp of detection

Think of this as the data collection point - it's constantly gathering information about emotions detected in the video feed.

### 2. Data Streaming Layer (Kafka & Zookeeper)
Once data is collected, it needs to be transmitted reliably. This is where Kafka comes in:

**Kafka** is a distributed streaming platform that:
- Acts like a highly reliable message broker
- Ensures no data is lost during transmission
- Can handle massive amounts of real-time data
- Makes data available to multiple consumers simultaneously

**Zookeeper** works alongside Kafka to:
- Keep track of which parts of Kafka are working
- Maintain configuration settings
- Ensure the whole system stays synchronized

Together, they ensure that every piece of emotion data captured makes it to the next stage reliably.

### 3. Data Processing (Apache Spark)
Spark acts as our data processing engine. It:
- Reads the continuous stream of emotion data from Kafka
- Processes this data in small batches
- Prepares it for storage in Cassandra
- Could perform additional analytics if needed

This step is crucial for handling real-time data effectively and preparing it for storage and analysis.

### 4. Data Storage (Cassandra)
Cassandra is our database choice because it's excellent at:
- Handling high-speed writes from real-time data
- Storing time-series data efficiently
- Retrieving recent data quickly for the dashboard

The database keeps track of all detections with their associated data, making it available for analysis and visualization.

### 5. Data Visualization (Dashboard)
The dashboard brings all this data to life by showing:
- A pie chart of emotion distribution
- A scatter plot showing where faces are detected in the frame
- Real-time statistics about detections

This helps us understand the patterns and trends in the emotion detection data.



## Technical Benefits
- **Scalability**: Can handle increasing amounts of data
- **Reliability**: No data loss even if components fail
- **Real-time Processing**: Immediate data availability
- **Flexibility**: Easy to modify or extend


## Installation & Setup
- Step 1 : Start Zookeeper
Terminal 1 :
```bash
/opt/kafka/bin/zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties
```
- Step 2 : Start Kafka
Terminal 2 :
```bash
/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
```
- Step 3 : Create Kafka Topic 
Terminal 3 :
```bash
/opt/kafka/bin/kafka-topics.sh --create --topic face-emotions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```
- Step 4: Start Cassandra
Terminal 4 :
```bash
sudo service cassandra start
```
- Step 5 : Create Cassandra Table 
```bash
cqlsh -f cassandra_schema.cql
```
- Step 5 : Create Cassandra Table
```bash
cqlsh -f cassandra_schema.cql
```
- Step 6 : Launch Components
**Emotion detector and Kafka Producer**
Terminal 5 :
```bash
python3 emotion_detector.py
```
**Start Spark Consumer**
Terminal 5 :
```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0 spark_consumer.py
```
**Start Dashboard**
Terminal 6 :
```bash
streamlit run dashboard.py
```



  


