INSERT INTO properties (address, purchase_price, sale_price, status)
VALUES
('10 Baker Street, London', 275000.00, NULL, 'purchased'),
('123 Main St, London', 250000.00, NULL, 'purchased'),
('456 Oak Ave, Manchester', 180000.00, NULL, 'renovating'),
('789 Elm St, Birmingham', 200000.00, 250000.00, 'for sale'),
('101 Pine Rd, Liverpool', 150000.00, 190000.00, 'sold'),
('202 Maple Ln, Leeds', 300000.00, NULL, 'purchased'),
('303 Cedar St, Bristol', 275000.00, NULL, 'renovating'),
('404 Birch Dr, Edinburgh', 220000.00, 275000.00, 'for sale'),
('505 Spruce Ct, Glasgow', 195000.00, 240000.00, 'sold')
RETURNING id;



INSERT INTO purchase_documents (property_id, document_type, document) VALUES
(1, 'contract', 'file_data_here'),
(1, 'notary_deed', 'file_data_here'),
(1, 'notary_registration', 'file_data_here'),
(1, 'deposit', 'file_data_here'),
(1, 'tax_ITP_IBA', 'file_data_here');


INSERT INTO renovation_documents (property_id, document_type, document) VALUES
(1, 'geotechnical_study', 'file_data_here'),
(1, 'land_plans', 'file_data_here'),
(1, 'architect_plans', 'file_data_here'),
(1, 'budget', 'file_data_here'),
(1, 'architect_contract', 'file_data_here'),
(1, 'surveyor_contract', 'file_data_here'),
(1, 'building_license', 'file_data_here'),
(1, 'contractor_contract', 'file_data_here'),
(1, 'trade_contract', 'file_data_here'),
(1, 'builder_payments', 'file_data_here');



INSERT INTO sales_documents (property_id, document_type, document) VALUES
(1, 'sale_contract', 'file_data_here'),
(1, 'payment_certification', 'file_data_here');

INSERT INTO payments (property_id, payment_stage, amount, recipient) VALUES
(1, 'during_construction', 50000.00, 'Main Contractor Ltd.'),
(1, 'at_start', 75000.00, 'Architect & Surveyor Co.'),
(1, 'at_end', 150000.00, 'RAMA Real Estate');
