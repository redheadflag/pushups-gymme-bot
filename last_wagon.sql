SELECT u.username, pe.user_id, COUNT(*) AS latest_entry_count
FROM (
    SELECT DISTINCT ON (date) *
    FROM pushup_entries
    ORDER BY date, timestamp DESC
) pe
JOIN users u ON pe.user_id = u.id
GROUP BY u.username, pe.user_id
ORDER BY latest_entry_count DESC
LIMIT 10;
