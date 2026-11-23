-- Load only into a fresh, isolated development database.
START TRANSACTION;

INSERT INTO Brand (brand_id, brand_name) VALUES
    (1, 'Atlas'), (2, 'Cedar'), (3, 'Harbor'), (4, 'Indigo');

INSERT INTO ProductType (product_type_id, type_name) VALUES
    (1, 'Editor'), (2, 'Backup');

INSERT INTO SoftwareSystem (software_id, brand_id, product_type_id) VALUES
    (1, 1, 1), (2, 2, 1), (3, 3, 2), (4, 4, 2);

COMMIT;
