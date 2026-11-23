-- 1. Brand: one row per distinct brand.
CREATE TABLE Brand (
    brand_id INT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(150) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- 2. ProductType: one row per software category.
CREATE TABLE ProductType (
    product_type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- 3. SoftwareSystem: connects a brand to a product category.
CREATE TABLE SoftwareSystem (
    software_id INT AUTO_INCREMENT PRIMARY KEY,
    brand_id INT NOT NULL,
    product_type_id INT NOT NULL,
    CONSTRAINT uq_brand_product UNIQUE (brand_id, product_type_id),
    CONSTRAINT fk_system_brand
        FOREIGN KEY (brand_id) REFERENCES Brand(brand_id),
    CONSTRAINT fk_system_type
        FOREIGN KEY (product_type_id) REFERENCES ProductType(product_type_id)
) ENGINE=InnoDB;

-- 4. Evaluator: stores anonymous evaluator identifiers only.
CREATE TABLE Evaluator (
    evaluator_id INT AUTO_INCREMENT PRIMARY KEY
) ENGINE=InnoDB;

-- 5. EvaluationReport: links an evaluator to a software system.
CREATE TABLE EvaluationReport (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    evaluator_id INT NOT NULL,
    software_id INT NOT NULL,
    CONSTRAINT fk_report_evaluator
        FOREIGN KEY (evaluator_id) REFERENCES Evaluator(evaluator_id),
    CONSTRAINT fk_report_software
        FOREIGN KEY (software_id) REFERENCES SoftwareSystem(software_id)
) ENGINE=InnoDB;

-- 6. ScoreCriterion: stores the four evaluation criteria.
CREATE TABLE ScoreCriterion (
    criterion_id INT AUTO_INCREMENT PRIMARY KEY,
    criterion_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- 7. EvaluationScore: one score per criterion in each report.
CREATE TABLE EvaluationScore (
    report_id INT NOT NULL,
    criterion_id INT NOT NULL,
    score_value INT NOT NULL,
    PRIMARY KEY (report_id, criterion_id),
    CONSTRAINT fk_score_report
        FOREIGN KEY (report_id) REFERENCES EvaluationReport(report_id),
    CONSTRAINT fk_score_criterion
        FOREIGN KEY (criterion_id) REFERENCES ScoreCriterion(criterion_id),
    CONSTRAINT chk_score_range CHECK (score_value BETWEEN 1 AND 10)
) ENGINE=InnoDB;
