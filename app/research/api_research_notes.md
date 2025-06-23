**Research Date:** June 10, 2025  
**Researcher:** bdela

---

## RentSpree API Research Results

### Pricing & Limits
- Free tier: NOT PUBLICLY AVAILABLE requests/month
- Paid tiers: $39.99+ for screening reports, PRO plans starting at $30/month
- Rate limits: Not publicly documented - enterprise partnerships only

### Available Data Fields
- Property details: rental applications, tenant data only
- Market data: NOT AVAILABLE - tenant screening focus only
- Location data: basic property addresses only
- Additional data: tenant screening reports, background checks, e-sign documents

### Geographic Coverage
- Supported countries: United States only
- Supported cities/states: All 50 states + DC
- Coverage limitations: No property market data, wrong use case for PropInsight

### Authentication Method
- API Key type: ENTERPRISE ONLY
- Required headers: Not publicly documented
- Authentication example: Contact sales team for API access

### Data Quality Notes
- Update frequency: Real-time for tenant applications
- Data accuracy: N/A for PropInsight use case
- Known limitations: No property pricing, market data, or analytics

---

## RealtyMole API Research Results

### Pricing & Limits
- Free tier: 50 requests/month
- Paid tiers: $99/month for 1,000 requests, $249/month for 5,000 requests, $499/month for 15,000 requests
- Rate limits: Reasonable usage expected, no hard limits documented

### Available Data Fields
- Property details: address, bedrooms, bathrooms, sqft, property_type, year_built, lot_size, features
- Market data: current_price, rent_estimate, price_history, market_value, comparables, AVM estimates
- Location data: latitude, longitude, city, state, zip_code, neighborhood, FIPS codes
- Additional data: owner_info, tax_assessment, property_photos, listing_status, days_on_market

### Geographic Coverage
- Supported countries: United States only
- Supported cities/states: All 50 states + DC with 140+ million properties
- Coverage limitations: Rural areas may have limited data, best coverage in major metropolitan areas

### Authentication Method
- API Key type: HEADER
- Required headers: X-API-Key, Content-Type: application/json
- Authentication example: headers = {"X-API-Key": "your_key_here", "Content-Type": "application/json"}

### Data Quality Notes
- Update frequency: DAILY updates with 500,000+ record updates processed daily
- Data accuracy: High accuracy from multiple data sources (public records, tax assessors, online directories)
- Known limitations: Some historical data limitations in rural areas, 2-year limit on historical data

---

## Rentals.com API Research Results

### Pricing & Limits
- Free tier: NOT AVAILABLE requests/month
- Paid tiers: NOT AVAILABLE - no public API
- Rate limits: N/A - no API access

### Available Data Fields
- Property details: NOT ACCESSIBLE - website only, no API
- Market data: NOT ACCESSIBLE - no API available
- Location data: NOT ACCESSIBLE - no API available
- Additional data: NOT ACCESSIBLE - no API available

### Geographic Coverage
- Supported countries: N/A - no API available
- Supported cities/states: N/A - no API available
- Coverage limitations: MAJOR - no API exists

### Authentication Method
- API Key type: N/A - no API available
- Required headers: N/A - no API available
- Authentication example: N/A - no API available

### Data Quality Notes
- Update frequency: N/A - no API access
- Data accuracy: N/A - no API access
- Known limitations: MAJOR - Rentals.com does not provide a public API

---

## Census API Research Results

### Pricing & Limits
- Free tier: UNLIMITED requests/month
- Paid tiers: NOT APPLICABLE - government service, completely free
- Rate limits: 500 requests per IP per day without key, unlimited with free API key

### Available Data Fields
- Property details: NOT AVAILABLE - demographics focus, not individual properties
- Market data: LIMITED - housing statistics and median values, no individual property pricing
- Location data: geographic boundaries, FIPS codes, lat/long coordinates for census areas, ZIP codes
- Additional data: demographics (age, race, income), population density, education levels, employment data, housing characteristics by geographic area

### Geographic Coverage
- Supported countries: United States only (including Puerto Rico and territories)
- Supported cities/states: Complete coverage - nation, states, counties, cities, census tracts, block groups
- Coverage limitations: No property-level data, only aggregated demographic data by geographic boundaries

### Authentication Method
- API Key type: QUERY_PARAM
- Required headers: None required
- Authentication example: GET https://api.census.gov/data/2021/acs/acs5?get=B01003_001E,NAME&for=county:*&in=state:06&key=your_census_api_key

### Data Quality Notes
- Update frequency: ANNUAL for American Community Survey, every 10 years for Decennial Census, quarterly for some economic data
- Data accuracy: Extremely high - official U.S. government statistics with rigorous quality control
- Known limitations: No individual property data, 1-5 year lag on some datasets, aggregated data only

---

## API Comparison & Recommendation

### Best APIs for PropInsight:
1. **Primary Choice:** RentCast/RealtyMole API - Comprehensive property data with pricing, estimates, and market analytics perfect for PropInsight's core functionality
2. **Secondary Choice:** US Census API - Free demographic data to enhance property insights with neighborhood analytics and market context

### Decision Factors:
- [x] Data coverage quality
- [x] Free tier limits sufficient
- [x] Geographic coverage matches target markets
- [x] Authentication complexity
- [x] Documentation quality
- [x] Response time/reliability

### Next Steps:
- [x] Sign up for chosen APIs (Day 6)
- [x] Get API credentials
- [x] Test connections