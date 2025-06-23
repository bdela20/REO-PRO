-- PropInsight Database Schema
-- Based on RentCast and Census API analysis

-- Drop existing tables if they exist (for development)
DROP TABLE IF EXISTS property_photos CASCADE;
DROP TABLE IF EXISTS search_history CASCADE;
DROP TABLE IF EXISTS market_trends CASCADE;
DROP TABLE IF EXISTS demographics CASCADE;
DROP TABLE IF EXISTS properties CASCADE;

-- PROPERTIES TABLE (Main property data from RentCast)
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    
    -- Address Information
    address TEXT NOT NULL,
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    county VARCHAR(100),
    
    -- Property Details
    property_type VARCHAR(50),
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    square_footage INTEGER,
    lot_size DECIMAL(10,2),
    year_built INTEGER,
    
    -- Financial Data
    estimated_value DECIMAL(12,2),
    rent_estimate DECIMAL(8,2),
    price_per_sqft DECIMAL(8,2),
    
    -- Location Coordinates
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    
    -- Data Management
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(50) DEFAULT 'RentCast',
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    CONSTRAINT unique_property UNIQUE(address, city, state)
);

-- DEMOGRAPHICS TABLE (Census data)
CREATE TABLE demographics (
    id SERIAL PRIMARY KEY,
    
    -- Geographic Identifiers
    state_code VARCHAR(2) NOT NULL,
    county_code VARCHAR(3),
    tract_code VARCHAR(6),
    area_name TEXT,
    
    -- Population Data
    total_population INTEGER,
    housing_units INTEGER,
    
    -- Economic Data
    median_household_income DECIMAL(10,2),
    poverty_rate DECIMAL(5,2),
    
    -- Education Data
    bachelors_degree_percent DECIMAL(5,2),
    high_school_percent DECIMAL(5,2),
    
    -- Demographics
    median_age DECIMAL(4,1),
    families_with_children_percent DECIMAL(5,2),
    
    -- Data Management
    survey_year INTEGER DEFAULT 2022,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_census_area UNIQUE(state_code, county_code, tract_code)
);

-- SEARCH_HISTORY TABLE (Track searches)
CREATE TABLE search_history (
    id SERIAL PRIMARY KEY,
    search_query TEXT NOT NULL,
    search_type VARCHAR(50),
    results_count INTEGER,
    user_ip VARCHAR(45),
    search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX idx_properties_city_state ON properties(city, state);
CREATE INDEX idx_properties_zip ON properties(zip_code);
CREATE INDEX idx_properties_location ON properties(latitude, longitude);
CREATE INDEX idx_demographics_location ON demographics(state_code, county_code);

-- Insert sample data for testing
INSERT INTO properties (
    address, city, state, zip_code, property_type,
    bedrooms, bathrooms, square_footage, year_built,
    estimated_value, rent_estimate, latitude, longitude
) VALUES (
    '123 Sample Street', 'Austin', 'TX', '78701', 'Single Family',
    3, 2.0, 1800, 1995,
    450000.00, 2800.00, 30.2672, -97.7431
);

SELECT 'PropInsight database schema created successfully! 🎉' AS status;