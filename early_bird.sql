SELECT u.username, pe.user_id, COUNT(*) AS entry_count
FROM pushup_entries pe
JOIN users u ON pe.user_id = u.id
WHERE pe.timestamp BETWEEN '04:00:00' AND '08:00:00'
GROUP BY u.username, pe.user_id
ORDER BY entry_count DESC
LIMIT 10;
