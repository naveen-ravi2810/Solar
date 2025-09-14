CREATE OR REPLACE VIEW client_with_consumers AS
WITH consumer_sums AS (
    SELECT
        ccm_id,
        COALESCE(
            SUM(
                CASE 
                    WHEN exclude_for_calculation = FALSE OR exclude_for_calculation IS NULL
                    THEN COALESCE(appliance_watt,0) * COALESCE(appliance_quantity,0) * COALESCE(appliance_day_usage,0)
                    ELSE 0
                END
            ),0
        ) AS total_day_wattage,
        COALESCE(
            SUM(
                CASE 
                    WHEN exclude_for_calculation = FALSE OR exclude_for_calculation IS NULL
                    THEN COALESCE(appliance_watt,0) * COALESCE(appliance_quantity,0) * COALESCE(appliance_night_usage,0)
                    ELSE 0
                END
            ),0
        ) AS total_night_wattage
    FROM consumerappliancesusage
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
        COALESCE(cs.total_day_wattage,0) AS total_day_wattage,
        COALESCE(cs.total_night_wattage,0) AS total_night_wattage
    FROM clientconsumer cc
    LEFT JOIN consumer_sums cs
      ON cc.ccm_id = cs.ccm_id
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
                           'total_day_wattage', ct.total_day_wattage,
                           'total_night_wattage', ct.total_night_wattage
                       )
                   )
            FROM consumer_totals ct
            WHERE ct.client_id = c.client_id
        ), '[]'::jsonb
    ) AS client_consumers
FROM clients c;