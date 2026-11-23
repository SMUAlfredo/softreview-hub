-- Add the application criteria while preserving any existing criterion IDs.
INSERT INTO ScoreCriterion (criterion_name)
SELECT required.criterion_name
FROM (
    SELECT 'friendliness' AS criterion_name
    UNION ALL SELECT 'price'
    UNION ALL SELECT 'features'
    UNION ALL SELECT 'accuracy'
) AS required
WHERE NOT EXISTS (
    SELECT 1
    FROM ScoreCriterion AS existing
    WHERE LOWER(existing.criterion_name) = required.criterion_name
);
