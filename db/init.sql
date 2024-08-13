-- Create the user_metrics table
CREATE TABLE IF NOT EXISTS user_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    user_id INT NOT NULL,
    session_id INT NOT NULL,
    metric_type VARCHAR(50) NOT NULL
);

-- Create the talked_time table
CREATE TABLE IF NOT EXISTS talked_time (
    id SERIAL PRIMARY KEY,
    user_metric_id INT REFERENCES user_metrics(id),
    duration INTERVAL NOT NULL
);

-- Create the microphone_used table
CREATE TABLE IF NOT EXISTS microphone_used (
    id SERIAL PRIMARY KEY,
    user_metric_id INT REFERENCES user_metrics(id),
    status BOOLEAN NOT NULL,
    volume_level INT
);

-- Create the speaker_used table
CREATE TABLE IF NOT EXISTS speaker_used (
    id SERIAL PRIMARY KEY,
    user_metric_id INT REFERENCES user_metrics(id),
    status BOOLEAN NOT NULL,
    volume_level INT
);

-- Create the voice_sentiment table
CREATE TABLE IF NOT EXISTS voice_sentiment (
    id SERIAL PRIMARY KEY,
    user_metric_id INT REFERENCES user_metrics(id),
    sentiment_score FLOAT NOT NULL,
    confidence_level FLOAT
);

-- Create indices for efficient querying
CREATE INDEX idx_user_metrics_timestamp ON user_metrics(timestamp);
CREATE INDEX idx_user_metrics_user_id ON user_metrics(user_id);
CREATE INDEX idx_user_metrics_session_id ON user_metrics(session_id);


/*
	This procedure inserts a new user metric and returns the inserted
	metric's ID for further use.
*/
CREATE OR REPLACE FUNCTION insert_user_metric(
    custom_timestamp TIMESTAMPTZ,
    custom_user_id INT,
    custom_session_id INT,
    custom_metric_type VARCHAR(50)
)
RETURNS INT AS $$
DECLARE
    user_metric_id INT;
BEGIN
    INSERT INTO user_metrics (timestamp, user_id, session_id, metric_type)
    VALUES (custom_timestamp, custom_user_id, custom_session_id, custom_metric_type)
    RETURNING id INTO user_metric_id;

    RETURN user_metric_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION insert_talked_time(
    custom_user_metric_id INT,
    custom_duration INTERVAL
)
RETURNS INT AS $$
DECLARE
    talked_time_id INT;
BEGIN
    INSERT INTO talked_time (user_metric_id, duration)
    VALUES (custom_user_metric_id, custom_duration)
    RETURNING id INTO talked_time_id;

    RETURN talked_time_id;
END;
$$ LANGUAGE plpgsql;

-- Function to insert into microphone_used
CREATE OR REPLACE FUNCTION insert_microphone_used(
    custom_user_metric_id INT,
    custom_status BOOLEAN,
    custom_volume_level INT
)
RETURNS INT AS $$
DECLARE
    microphone_used_id INT;
BEGIN
    INSERT INTO microphone_used (user_metric_id, status, volume_level)
    VALUES (custom_user_metric_id, custom_status, custom_volume_level)
    RETURNING id INTO microphone_used_id;

    RETURN microphone_used_id;
END;
$$ LANGUAGE plpgsql;

-- Function to insert into speaker_used
CREATE OR REPLACE FUNCTION insert_speaker_used(
    custom_user_metric_id INT,
    custom_status BOOLEAN,
    custom_volume_level INT
)
RETURNS INT AS $$
DECLARE
    speaker_used_id INT;
BEGIN
    INSERT INTO speaker_used (user_metric_id, status, volume_level)
    VALUES (custom_user_metric_id, custom_status, custom_volume_level)
    RETURNING id INTO speaker_used_id;

    RETURN speaker_used_id;
END;
$$ LANGUAGE plpgsql;

-- Function to insert into voice_sentiment
CREATE OR REPLACE FUNCTION insert_voice_sentiment(
    custom_user_metric_id INT,
    custom_sentiment_score FLOAT,
    custom_confidence_level FLOAT
)
RETURNS INT AS $$
DECLARE
    voice_sentiment_id INT;
BEGIN
    INSERT INTO voice_sentiment (user_metric_id, sentiment_score, confidence_level)
    VALUES (custom_user_metric_id, custom_sentiment_score, custom_confidence_level)
    RETURNING id INTO voice_sentiment_id;

    RETURN voice_sentiment_id;
END;
$$ LANGUAGE plpgsql;

/*
	This procedure calculates the total talked time for a specific
	user in a specific session.
*/
CREATE OR REPLACE FUNCTION total_talked_time(
    custom_user_id INT,
    custom_session_id INT
)
RETURNS INTERVAL AS $$
DECLARE
    total_duration INTERVAL;
BEGIN
    SELECT COALESCE(SUM(tt.duration), '0 seconds'::INTERVAL)
    INTO total_duration
    FROM talked_time tt
    JOIN user_metrics um ON tt.user_metric_id = um.id
    WHERE um.user_id = custom_user_id AND um.session_id = custom_session_id;

    RETURN total_duration;
END;
$$ LANGUAGE plpgsql;


/*
	This procedure returns the average sentiment score and average confidence
	level for a specific session.
*/
CREATE OR REPLACE FUNCTION calculate_voice_sentiment_summary(
    custom_session_id INT
)
RETURNS TABLE (
    avg_sentiment_score FLOAT,
    avg_confidence_level FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        AVG(vs.sentiment_score) AS avg_sentiment_score,
        AVG(vs.confidence_level) AS avg_confidence_level
    FROM voice_sentiment AS vs
    JOIN user_metrics um ON vs.user_metric_id = um.id
    WHERE um.session_id = custom_session_id;
END;
$$ LANGUAGE plpgsql;


/*
	This procedure generates a report showing each user's activity in
	a session, including total talked time and whether the microphone
	and speaker were used.
*/
CREATE OR REPLACE FUNCTION generate_user_activity_report(
    custom_session_id INT
)
RETURNS TABLE (
    user_id INT,
    total_talked_time INTERVAL,
    mic_used BOOLEAN,
    speaker_used BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        um.user_id,
        total_talked_time(um.user_id, um.session_id) AS total_talked_time,
        EXISTS (
            SELECT 1
            FROM user_metrics um2
            JOIN microphone_used mu ON mu.user_metric_id = um2.id
            WHERE um2.user_id = um.user_id
            AND um2.session_id = um.session_id
            AND mu.status = TRUE
        ) AS mic_used,
        EXISTS (
            SELECT 1
            FROM user_metrics um2
            JOIN speaker_used su ON su.user_metric_id = um2.id
            WHERE um2.user_id = um.user_id
            AND um2.session_id = um.session_id
            AND su.status = TRUE
        ) AS speaker_used
    FROM user_metrics um
    WHERE um.session_id = custom_session_id
    GROUP BY um.user_id, um.session_id;
END;
$$ LANGUAGE plpgsql;



/*
	Trigger to Automatically Insert a Record in talked_time when a New
	user_metrics Record is Inserted
*/
CREATE OR REPLACE FUNCTION trigger_insert_talked_time()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.metric_type = 'talked_time' THEN
        INSERT INTO talked_time (user_metric_id, duration)
        VALUES (NEW.id, '0 seconds');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_insert_user_metrics
AFTER INSERT ON user_metrics
FOR EACH ROW
EXECUTE FUNCTION trigger_insert_talked_time();



/*
	Trigger to Automatically Insert a Record in microphone_used when a 
	New user_metrics Record is Inserted
*/
CREATE OR REPLACE FUNCTION trigger_insert_microphone_used()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.metric_type = 'microphone_used' THEN
        INSERT INTO microphone_used (user_metric_id, status, volume_level)
        VALUES (NEW.id, FALSE, NULL);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_insert_microphone_used
AFTER INSERT ON user_metrics
FOR EACH ROW
EXECUTE FUNCTION trigger_insert_microphone_used();


/*
	Trigger to Automatically Insert a Record in speaker_used when a
	New user_metrics Record is Inserted
*/
CREATE OR REPLACE FUNCTION trigger_insert_speaker_used()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.metric_type = 'speaker_used' THEN
        INSERT INTO speaker_used (user_metric_id, status, volume_level)
        VALUES (NEW.id, FALSE, NULL);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_insert_speaker_used
AFTER INSERT ON user_metrics
FOR EACH ROW
EXECUTE FUNCTION trigger_insert_speaker_used();

/*
	Trigger to Automatically Insert a Record in voice_sentiment when
	a New user_metrics Record is Inserted
*/
CREATE OR REPLACE FUNCTION trigger_insert_voice_sentiment()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.metric_type = 'voice_sentiment' THEN
        INSERT INTO voice_sentiment (user_metric_id, sentiment_score, confidence_level)
        VALUES (NEW.id, 0.0, 0.0);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_insert_voice_sentiment
AFTER INSERT ON user_metrics
FOR EACH ROW
EXECUTE FUNCTION trigger_insert_voice_sentiment();

/*
	Trigger to Prevent Deletion of user_metrics Records if Linked to Other Tables
*/
CREATE OR REPLACE FUNCTION trigger_prevent_delete_user_metrics()
RETURNS TRIGGER AS $$
DECLARE
    v_exists BOOLEAN;
BEGIN
    -- Check if record exists in talked_time
    SELECT EXISTS (SELECT 1 FROM talked_time WHERE user_metric_id = OLD.id) INTO v_exists;
    IF v_exists THEN
        RAISE EXCEPTION 'Cannot delete user_metrics record because it is referenced in talked_time';
    END IF;

    -- Check if record exists in microphone_used
    SELECT EXISTS (SELECT 1 FROM microphone_used WHERE user_metric_id = OLD.id) INTO v_exists;
    IF v_exists THEN
        RAISE EXCEPTION 'Cannot delete user_metrics record because it is referenced in microphone_used';
    END IF;

    -- Check if record exists in speaker_used
    SELECT EXISTS (SELECT 1 FROM speaker_used WHERE user_metric_id = OLD.id) INTO v_exists;
    IF v_exists THEN
        RAISE EXCEPTION 'Cannot delete user_metrics record because it is referenced in speaker_used';
    END IF;

    -- Check if record exists in voice_sentiment
    SELECT EXISTS (SELECT 1 FROM voice_sentiment WHERE user_metric_id = OLD.id) INTO v_exists;
    IF v_exists THEN
        RAISE EXCEPTION 'Cannot delete user_metrics record because it is referenced in voice_sentiment';
    END IF;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_before_delete_user_metrics
BEFORE DELETE ON user_metrics
FOR EACH ROW
EXECUTE FUNCTION trigger_prevent_delete_user_metrics();


/*
    Updates a record in the talked_time table.
*/
CREATE OR REPLACE FUNCTION update_talked_time_record(
    record_id INT,
    new_duration INTERVAL
)
RETURNS VOID AS $$
BEGIN
    UPDATE talked_time
    SET duration = new_duration
    WHERE id = record_id;
END;
$$ LANGUAGE plpgsql;

/*
    Updates a record in the microphone_used table.
*/
CREATE OR REPLACE FUNCTION update_microphone_used_record(
    record_id INT,
    new_status BOOLEAN,
    new_volume_level INT
)
RETURNS VOID AS $$
BEGIN
    UPDATE microphone_used
    SET status = new_status, volume_level = new_volume_level
    WHERE id = record_id;
END;
$$ LANGUAGE plpgsql;

/*
    Updates a record in the speaker_used table.
*/
CREATE OR REPLACE FUNCTION update_speaker_used_record(
    record_id INT,
    new_status BOOLEAN,
    new_volume_level INT
)
RETURNS VOID AS $$
BEGIN
    UPDATE speaker_used
    SET status = new_status, volume_level = new_volume_level
    WHERE id = record_id;
END;
$$ LANGUAGE plpgsql;

/*
    Updates a record in the voice_sentiment table.
*/
CREATE OR REPLACE FUNCTION update_voice_sentiment_record(
    record_id INT,
    new_sentiment_score FLOAT,
    new_confidence_level FLOAT
)
RETURNS VOID AS $$
BEGIN
    UPDATE voice_sentiment
    SET sentiment_score = new_sentiment_score, confidence_level = new_confidence_level
    WHERE id = record_id;
END;
$$ LANGUAGE plpgsql;

/*
    Provides a summary of microphone usage, including the total number of records and percentage 
    of times the microphone was used.
*/
CREATE OR REPLACE FUNCTION microphone_usage_summary(
    custom_session_id INT
)
RETURNS TABLE (
    total_records INT,
    used_count INT,
    usage_percentage FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INT AS total_records,
        COUNT(CASE WHEN mu.status THEN 1 END)::INT AS used_count,
        (COUNT(CASE WHEN mu.status THEN 1 END) * 100.0 / COUNT(*))::FLOAT AS usage_percentage
    FROM user_metrics um
    JOIN microphone_used mu ON mu.user_metric_id = um.id
    WHERE um.session_id = custom_session_id;
END;
$$ LANGUAGE plpgsql;


/*
    Provides a summary of speaker usage similar to the microphone usage summary.
*/
CREATE OR REPLACE FUNCTION speaker_usage_summary(
    custom_session_id INT
)
RETURNS TABLE (
    total_records INT,
    used_count INT,
    usage_percentage FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INT AS total_records,
        COUNT(CASE WHEN su.status THEN 1 END)::INT AS used_count,
        (COUNT(CASE WHEN su.status THEN 1 END) * 100.0 / COUNT(*))::FLOAT AS usage_percentage
    FROM user_metrics um
    JOIN speaker_used su ON su.user_metric_id = um.id
    WHERE um.session_id = custom_session_id;
END;
$$ LANGUAGE plpgsql;
