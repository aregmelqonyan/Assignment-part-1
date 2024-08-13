# Usage

## 1. Clone the Repository

```bash
git clone https://github.com/aregmelqonyan/Assignment-part-1
```

## 2. Change Directory
```bash
cd Assignment-part-1
```

## 3. Run the Application

This command will build and start the application and database containers in detached mode.
```bash
docker compose up -d
```

# Navigating the Swagger UI

## 1. Accessing Swagger UI

Open your browser and go to [http://localhost:8000/docs](http://localhost:8000/docs). You’ll see the Swagger UI, which provides an interactive interface for your API.
![Alt Text](/images/url.png)

## 2. Exploring Endpoints

The main page lists all available API endpoints. Each endpoint is organized by tags, which correspond to different areas of your API functionality.

- **Expand a Tag**: Click on a tag to expand it and see the available endpoints under that category.
- **View Endpoint Details**: Click on an endpoint to view its details, including request parameters, response format, and status codes.
![Alt Text](/images/endpoints.png)


## 3. Executing Requests

You can directly execute API requests from the Swagger UI:

- **Click "Try it out"**: When you click this button on an endpoint, you’ll be able to enter any required parameters.
- **Execute**: After entering the parameters, click the **Execute** button. The results, including the status code, response body, and headers, will be displayed.
![Alt Text](/images/try_it.png)

## 4. Request/Response Example

Each endpoint shows examples of the request body (if applicable) and the expected response. This helps in understanding the data structure and format required for the API interactions.
![Alt Text](/images/request_response.png)

## 5. Example Usage

- **Post user_metric**: After posting, a row is automatically created in the `talked_time` table with default values.
  ![Post user_metric](/images/post.png)
- **Retrieve metric_id**: Obtain the `metric_id` from the response.
  ![Retrieve metric_id](/images/return_id.png)
- **Find metric record_id**: Locate the `record_id` in the `talked_time` table using the `metric_id`.
  ![Find metric record_id](/images/finding_record_id.png)
- **Update Fields**: Modify the fields of the record in the `talked_time` table.
  ![Update Fields](/images/put.png)
- **Calculate Total Talked Time**: Calculate the total talked time for a user using `user_id` and `session_id`.
  ![Calculate Total Talked Time](/images/total.png)

# Database Schema and Pipeline Documentation

## Overview

This document explains the structure of the database schema used for recording user metrics and provides guidelines for maintaining and extending the data ingestion pipeline.

## Database Schema

### user_metrics Table

The `user_metrics` table is the central table that records each metric entry with a unique ID. It captures common fields applicable to all metric types.

**Columns:**
- **id**: Unique identifier for each metric entry.
- **timestamp**: Date and time when the metric was recorded.
- **user_id**: Identifier for the user associated with the metric.
- **session_id**: Identifier for the session in which the metric was recorded.
- **metric_type**: Type of metric (e.g., talked_time, microphone_used, etc.).

### talked_time Table

The `talked_time` table stores detailed information about the duration of talking sessions.

**Columns:**
- **id**: Unique identifier for each talked time record.
- **user_metric_id**: Foreign key referencing `user_metrics.id`, linking the talked time to a specific metric record.
- **duration**: Duration of the talking session.

### microphone_used Table

The `microphone_used` table records information about microphone usage, including its status and volume level.

**Columns:**
- **id**: Unique identifier for each microphone usage record.
- **user_metric_id**: Foreign key referencing `user_metrics.id`.
- **status**: Indicates whether the microphone was on or off.
- **volume_level**: Volume level when the microphone was in use.

### speaker_used Table

The `speaker_used` table tracks details about speaker usage similar to the microphone usage table.

**Columns:**
- **id**: Unique identifier for each speaker usage record.
- **user_metric_id**: Foreign key referencing `user_metrics.id`.
- **status**: Indicates whether the speaker was on or off.
- **volume_level**: Volume level when the speaker was in use.

### voice_sentiment Table

The `voice_sentiment` table captures sentiment analysis of the user's voice, providing insights into emotional tone.

**Columns:**
- **id**: Unique identifier for each sentiment record.
- **user_metric_id**: Foreign key referencing `user_metrics.id`.
- **sentiment_score**: Numerical score representing the sentiment of the voice.
- **confidence_level**: Confidence in the sentiment score provided.

![Alt Text](/images/schema.png)

## Guidelines for Maintaining and Extending the Pipeline

### Maintenance Guidelines

- Regularly verify that foreign key constraints are correctly enforced to maintain referential integrity between tables.
- Ensure appropriate security measures are in place.
- Plan for scaling the database if data volume increases significantly.

### Extending the Pipeline

- **Create New Tables**: Add new tables for each new type of metric.
- **Add New Fields**: Modify existing tables to include new fields as needed for additional metrics.
- **Update Relationships**: Adjust foreign key relationships if new tables are introduced.
- **Testing**: Thoroughly test the pipeline with new metrics to ensure correct data ingestion and processing.

### Potential Limitations

- Extremely high data volumes or very high query loads may require additional performance tuning or database scaling strategies.
- The use of multiple tables and foreign key relationships can introduce complexity in queries and data management.

## Suggestions for Future Improvements

- Regularly review and optimize indices based on query performance and usage patterns.
- Consider integrating real-time analytics tools if real-time processing and reporting are needed.
- Keep the documentation updated with any changes to the schema or pipeline to ensure clarity for future developers and maintainers.

## Assumptions

- The schema is designed for moderate to high data volumes. Very high data volumes may necessitate additional performance optimizations.
- Data entering the pipeline is assumed to be clean and conform to expected formats, including valid timestamps, user IDs, and metric values.
- Data consistency is assumed, following the expected format.

