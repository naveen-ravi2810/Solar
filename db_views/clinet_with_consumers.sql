CREATE OR REPLACE VIEW client_with_consumers AS
WITH consumer_sums AS (
    SELECT
        ccm_id,
        SUM(
            CASE WHEN exclude_for_calculation = FALSE OR exclude_for_calculation IS NULL
                 THEN appliance_watt * appliance_quantity * COALESCE(appliance_day_usage,0)
                 ELSE 0
            END
        ) AS total_day_wattage,
        SUM(
            CASE WHEN exclude_for_calculation = FALSE OR exclude_for_calculation IS NULL
                 THEN appliance_watt * appliance_quantity * COALESCE(appliance_night_usage,0)
                 ELSE 0
            END
        ) AS total_night_wattage,
        SUM(
            CASE WHEN need_battery_backup = TRUE AND (exclude_for_calculation = FALSE OR exclude_for_calculation IS NULL)
                 THEN appliance_watt * appliance_quantity * COALESCE(appliance_night_usage,0)
                 ELSE 0
            END
        ) AS total_battery_needed_for_night
    FROM consumerappliancesusage
        WHERE exclude_for_calculation = FALSE OR exclude_for_calculation IS NULL
    GROUP BY ccm_id
),
consumer_totals AS (
    SELECT
        cc.ccm_id,
        cc.client_id,
        cc.clinet_consumer_meter_type,
        cc.clinet_consumer_demand_load,
        cc.clinet_consumed_demand_phase,
        cc.client_consumer_max_consumed_units,
        cc.client_consumer_avg_consumed_unit,
        cc.client_consumer_peak_demand,
        cc.client_consumer_avg_demand,
        cc.clinet_consumer_number,
        cc.clinet_consumer_phone_number,
        cc.clinet_consumer_nick_name,
        cc.clinet_consumer_billing_type,
        cc.clinet_consumer_requirement,
        COALESCE(cs.total_day_wattage,0) AS total_day_wattage,
        COALESCE(cs.total_night_wattage,0) AS total_night_wattage,
        COALESCE(cs.total_battery_needed_for_night,0) AS total_battery_needed_for_night,
        
        -- Total days based on billing type
        CASE cc.clinet_consumer_billing_type
            WHEN 'MONTHLY' THEN 30
            WHEN 'BI_MONTHLY' THEN 60
            ELSE 1
        END AS total_days_multiplication,
        
        -- JS equivalent calculations
        (COALESCE(cs.total_day_wattage,0) + COALESCE(cs.total_night_wattage,0)) AS total_usage,
        ((COALESCE(cs.total_day_wattage,0) + COALESCE(cs.total_night_wattage,0))/1000.0) AS total_usage_units,
        (COALESCE(cs.total_day_wattage,0)/1000.0) AS day_usage_units,
        (COALESCE(cs.total_night_wattage,0)/1000.0) AS night_usage_units,
        ROUND(((COALESCE(cs.total_day_wattage,0) + COALESCE(cs.total_night_wattage,0)) * 
              CASE cc.clinet_consumer_billing_type
                  WHEN 'MONTHLY' THEN 30
                  WHEN 'BI_MONTHLY' THEN 60
                  ELSE 1
              END
             )/1000.0) AS per_bill_units,
        ROUND(((COALESCE(cs.total_day_wattage,0) + COALESCE(cs.total_night_wattage,0)) * 
              CASE cc.clinet_consumer_billing_type
                  WHEN 'MONTHLY' THEN 30
                  WHEN 'BI_MONTHLY' THEN 60
                  ELSE 1
              END
             )/1000.0 / 4.0 / 
             CASE cc.clinet_consumer_billing_type
                  WHEN 'MONTHLY' THEN 30
                  WHEN 'BI_MONTHLY' THEN 60
                  ELSE 1
             END
        ) AS kilo_watt_needed,
        ((COALESCE(cs.total_battery_needed_for_night,0)/1000.0)*15/100 + COALESCE(cs.total_battery_needed_for_night,0)/1000.0) AS battery_backup_needed,
        (((COALESCE(cs.total_battery_needed_for_night,0)/1000.0)*15/100 + COALESCE(cs.total_battery_needed_for_night,0)/1000.0) 
         + (COALESCE(cs.total_day_wattage,0)/1000.0))/4.0 AS kilo_watt_needed_for_day_and_battery
    FROM clientconsumer cc
    LEFT JOIN consumer_sums cs ON cc.ccm_id = cs.ccm_id
)
SELECT
    c.client_id,
    c.client_name,
    c.client_phone,
    c.client_email,
    c.created_on,
    COALESCE(
        (
            SELECT jsonb_agg(
                       jsonb_build_object(
                           'ccm_id', ct.ccm_id,
                           'clinet_consumer_meter_type', ct.clinet_consumer_meter_type,
                           'clinet_consumer_demand_load', ct.clinet_consumer_demand_load,
                           'clinet_consumed_demand_phase', ct.clinet_consumed_demand_phase,
                           'client_consumer_max_consumed_units', ct.client_consumer_max_consumed_units,
                           'client_consumer_avg_consumed_unit', ct.client_consumer_avg_consumed_unit,
                           'client_consumer_peak_demand', ct.client_consumer_peak_demand,
                           'client_consumer_avg_demand', ct.client_consumer_avg_demand,
                           'clinet_consumer_number', ct.clinet_consumer_number,
                           'clinet_consumer_phone_number', ct.clinet_consumer_phone_number,
                           'clinet_consumer_nick_name', ct.clinet_consumer_nick_name,
                           'clinet_consumer_billing_type', ct.clinet_consumer_billing_type,
                           'clinet_consumer_requirement', ct.clinet_consumer_requirement,
                           'total_day_wattage', ct.total_day_wattage,
                           'total_night_wattage', ct.total_night_wattage,
                           'total_battery_needed_for_night', ct.total_battery_needed_for_night,
                           'total_usage', ct.total_usage,
                           'total_usage_units', ct.total_usage_units,
                           'day_usage_units', ct.day_usage_units,
                           'night_usage_units', ct.night_usage_units,
                           'per_bill_units', ct.per_bill_units,
                           'kilo_watt_needed', ct.kilo_watt_needed,
                           'battery_backup_needed', ct.battery_backup_needed,
                           'kilo_watt_needed_for_day_and_battery', ct.kilo_watt_needed_for_day_and_battery,
                           'total_days_multiplication_value', ct.total_days_multiplication,
                           'consumer_requirements', (
                               SELECT COALESCE(
                                          jsonb_agg(
                                              jsonb_build_object(
                                                  'con_req_id', cr.con_req_id,
                                                  'ccm_id', cr.ccm_id,
                                                  'created_on', cr.created_on,
                                                  'creq_name', cr.creq_name
                                              )
                                          ), '[]'::jsonb
                                      )
                               FROM consumer_requirement cr
                               WHERE cr.ccm_id = ct.ccm_id
                           )
                           )
                   )
            FROM consumer_totals ct
            WHERE ct.client_id = c.client_id
        ), '[]'::jsonb
    ) AS client_consumers
FROM clients c;
