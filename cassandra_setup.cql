-- cassandra_schema.cql
CREATE KEYSPACE IF NOT EXISTS emotion_tracking
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE emotion_tracking;

CREATE TABLE IF NOT EXISTS emotion_data (
    id UUID PRIMARY KEY,
    timestamp timestamp,
    bbox_x int,
    bbox_y int,
    bbox_width int,
    bbox_height int,
    emotion text
);

CREATE INDEX ON emotion_data(emotion);
CREATE INDEX ON emotion_data(timestamp);