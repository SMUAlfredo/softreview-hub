-- Load only into a fresh, isolated development database.
START TRANSACTION;

INSERT INTO Brand (brand_id, brand_name) VALUES
    (1, 'Atlas'), (2, 'Cedar'), (3, 'Harbor'), (4, 'Indigo');

INSERT INTO ProductType (product_type_id, type_name) VALUES
    (1, 'Editor'), (2, 'Backup');

INSERT INTO SoftwareSystem (software_id, brand_id, product_type_id) VALUES
    (1, 1, 1), (2, 2, 1), (3, 3, 2), (4, 4, 2);

INSERT INTO Evaluator (evaluator_id) VALUES (1), (2), (3), (4);

INSERT INTO EvaluationReport (report_id, evaluator_id, software_id) VALUES
    (1, 1, 1), (2, 2, 1), (3, 3, 2), (4, 4, 3);

INSERT INTO EvaluationScore (report_id, criterion_id, score_value)
SELECT fixture.report_id, c.criterion_id,
       CASE LOWER(c.criterion_name)
           WHEN 'friendliness' THEN fixture.friendliness
           WHEN 'price' THEN fixture.price
           WHEN 'features' THEN fixture.features
           WHEN 'accuracy' THEN fixture.accuracy
       END
FROM (
    SELECT 1 AS report_id, 7 AS friendliness, 4 AS price, 6 AS features, 7 AS accuracy
    UNION ALL SELECT 2, 9, 6, 8, 9
    UNION ALL SELECT 3, 5, 9, 7, 6
    UNION ALL SELECT 4, 8, 3, 9, 8
) AS fixture
CROSS JOIN ScoreCriterion AS c
WHERE LOWER(c.criterion_name) IN ('friendliness', 'price', 'features', 'accuracy');

COMMIT;
