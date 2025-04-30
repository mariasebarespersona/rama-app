CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    purchase_price NUMERIC(10,2),
    sale_price NUMERIC(10,2),
    status VARCHAR(50) CHECK (status IN ('purchased', 'renovating', 'for sale', 'sold')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE purchase_documents (
    id SERIAL PRIMARY KEY,
    property_id INT REFERENCES properties(id) ON DELETE CASCADE,
    document_type VARCHAR(50) CHECK (document_type IN ('contract', 'notary_deed', 'notary_registration', 'deposit', 'tax_ITP_IBA')),
    document BYTEA,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE renovation_documents (
    id SERIAL PRIMARY KEY,
    property_id INT REFERENCES properties(id) ON DELETE CASCADE,
    document_type VARCHAR(50) CHECK (document_type IN ('geotechnical_study', 'land_plans', 'architect_plans', 'budget', 'architect_contract', 'surveyor_contract', 'building_license', 'contractor_contract', 'trade_contract', 'builder_payments')),
    document BYTEA,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sales_documents (
    id SERIAL PRIMARY KEY,
    property_id INT REFERENCES properties(id) ON DELETE CASCADE,
    document_type VARCHAR(50) CHECK (document_type IN ('sale_contract', 'payment_certification')),
    document BYTEA,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    property_id INT REFERENCES properties(id) ON DELETE CASCADE,
    payment_stage VARCHAR(50) CHECK (payment_stage IN ('during_construction', 'at_start', 'at_end')),
    amount NUMERIC(10,2),
    recipient VARCHAR(100),
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);