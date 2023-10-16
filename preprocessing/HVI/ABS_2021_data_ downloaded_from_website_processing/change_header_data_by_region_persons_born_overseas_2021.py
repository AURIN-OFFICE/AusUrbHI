import pandas as pd

# change the header names of ABS data by region persons born overseas 2021 csv
new_columns = [
    "code", "label", "year", "males_born_overseas_no", "females_born_overseas_no",
    "persons_born_overseas_no", "0-4_years_no", "5-9_years_no", "10-14_years_no",
    "15-19_years_no", "20-24_years_no", "25-29_years_no", "30-34_years_no",
    "35-39_years_no", "40-44_years_no", "45-49_years_no", "50-54_years_no",
    "55-59_years_no", "60-64_years_no", "65-69_years_no", "70-74_years_no",
    "75-79_years_no", "80-84_years_no", "85_years_and_over_no",
    "arrived_within_5_years_percent", "arrived_5-10_years_ago_percent",
    "arrived_over_10_years_ago_percent", "arrival_not_stated_percent",
    "australian_citizen_percent", "not_an_australian_citizen_percent",
    "citizenship_not_stated_percent", "buddhism_percent", "christianity_percent",
    "hinduism_percent", "islam_percent", "judaism_percent", "other_religion_percent",
    "secular_beliefs_other_spiritual_beliefs_no_religion_percent",
    "religious_affiliation_inadequately_described_or_not_stated_percent",
    "proficient_in_english_percent", "not_proficient_in_english_percent",
    "english_proficiency_not_stated_percent", "postgraduate_degree_level_percent",
    "graduate_diploma_and_graduate_certificate_level_percent",
    "bachelor_degree_level_percent", "advanced_diploma_and_diploma_level_percent",
    "certificate_level_percent", "school_education_level_percent",
    "education_not_stated_percent", "managers_percent", "professionals_percent",
    "technicians_and_trades_workers_percent", "community_and_personal_service_workers_percent",
    "clerical_and_administrative_workers_percent", "sales_workers_percent",
    "machinery_operators_and_drivers_percent", "labourers_percent",
    "occupation_inadequately_described_or_not_stated_percent",
    "overseas_born_population_aged_15_years_and_over_no", "employed_no", "unemployed_no",
    "in_the_labour_force_no", "unemployment_rate_percent", "participation_rate_percent",
    "not_in_the_labour_force_percent", "labour_force_status_not_stated_percent",
    "overseas_born_population_aged_15_years_and_over_no", "persons_earning_$1-$499_per_week_percent",
    "persons_earning_$500-$999_per_week_percent", "persons_earning_$1000-$1999_per_week_percent",
    "persons_earning_$2000-$2999_per_week_percent", "persons_earning_$3000_or_more_per_week_percent",
    "persons_earning_nil_income_percent", "persons_with_a_negative_income_percent",
    "income_inadequately_described_or_not_stated_percent"
]

df = pd.read_csv(r'..\..\_data\boundary_data\data_by_region_persons_born_overseas_asgs.csv', header=None, skiprows=1)
df.columns = new_columns
df.to_csv(r'..\..\_data\boundary_data\data_by_region_persons_born_overseas_asgs_name_modified.csv', index=False)
