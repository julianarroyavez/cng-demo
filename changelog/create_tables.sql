
create schema if not exists auth;
create schema if not exists master;
create schema if not exists payment;
create schema if not exists engagement;
create schema if not exists transactional;
create schema if not exists telemetry;
create schema if not exists support;





create sequence if not exists payment.invoices_id_seq;
create sequence if not exists auth.permissions_id_seq;
create sequence if not exists auth.roles_id_seq;
create sequence if not exists transactional.chargers_id_seq;
create sequence if not exists master.charging_connectors_id_seq;
create sequence if not exists auth.groups_id_seq;
create sequence if not exists transactional.equipments_id_seq;
create sequence if not exists master.equipment_type_masters_id_seq;
create sequence if not exists public.vehicle_connector_mapping_id_seq;
create sequence if not exists transactional.mobile_devices_id_seq;
create sequence if not exists transactional.nozzles_id_seq;
create sequence if not exists master.rated_powers_id_seq;
create sequence if not exists master.segments_of_day_id_seq;
create sequence if not exists auth.user_group_rel_id_seq;
create sequence if not exists master.app_configs_id_seq;
create sequence if not exists engagement.notifications_id_seq;
create sequence if not exists support.temporary_test_table_id_seq;
create sequence if not exists telemetry.energy_consumption_id_seq;
create sequence if not exists telemetry.station_mapping_id_seq;
create sequence if not exists support.faqs_id_seq;
create sequence if not exists master.service_masters_id_seq;
create sequence if not exists master.vehicle_masters_id_seq;
create sequence if not exists payment.order_items_id_seq;
create sequence if not exists master.service_rate_table_id_seq;
create sequence if not exists master.service_rates_id_seq;
create sequence if not exists master.token_conversion_rates_id_seq;
create sequence if not exists transactional.slots_id_seq;
create sequence if not exists transactional.station_assignment_id_seq;
create sequence if not exists master.station_operating_time_master_id_seq;
create sequence if not exists transactional.station_operation_break_details_id_seq;
create sequence if not exists transactional.station_operation_details_id_seq;
create sequence if not exists transactional.station_services_id_seq;
create sequence if not exists transactional.station_medias_id_seq;
create sequence if not exists transactional.verifications_id_seq;

CREATE FUNCTION public.fn_insert_account_for_new_user()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
BEGIN
    IF NOT Exists(
        SELECT * FROM accounts WHERE record_id = NEW.record_id
    ) THEN
        INSERT INTO accounts(id, record_id, active, created_on, created_by, modified_on, modified_by, validity_start, validity_end, alias_name)
        values (NEW.id, NEW.record_id, NEW.active, NEW.created_on, NEW.created_by, NEW.modified_on, NEW.modified_by, NEW.validity_start, NEW.validity_end, NEW.alias_name);
    END IF;
    Return NEW;
END
$BODY$;

CREATE FUNCTION public.fn_insert_equipment_for_new_mobile_device()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
--provide support to take temporal entries
BEGIN
    IF NOT Exists(
        SELECT * FROM equipments WHERE record_id = NEW.record_id
    ) THEN
        INSERT INTO equipments(id, record_id, active, created_on, created_by, modified_on, modified_by, validity_start, validity_end, type)
        values (NEW.id, NEW.record_id, NEW.active, NEW.created_on, NEW.created_by, NEW.modified_on, NEW.modified_by, NEW.validity_start, NEW.validity_end, NEW.type);
    END IF;
    Return NEW;
END
$BODY$;

CREATE FUNCTION public.fn_insert_wallet_for_new_account()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
BEGIN
    IF NOT Exists(
        SELECT * FROM wallets WHERE record_id = NEW.record_id
    ) THEN
        INSERT INTO wallets(id, record_id, account_id, active, created_on, created_by, modified_on, modified_by, validity_start, validity_end, name, balance, in_transit)
        values (NEW.id, NEW.record_id, NEW.record_id, NEW.active, NEW.created_on, NEW.created_by, NEW.modified_on, NEW.modified_by, NEW.validity_start, NEW.validity_end, NEW.alias_name, 0, null);
    END IF;
    Return NEW;
END
$BODY$;

CREATE EXTENSION hstore;

-- Table: master.app_configs

-- DROP TABLE master.app_configs;

CREATE TABLE IF NOT EXISTS master.app_configs
(
    id bigint NOT NULL DEFAULT nextval('master.app_configs_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    key character varying(100) COLLATE pg_catalog."default",
    value character varying(255) COLLATE pg_catalog."default",
    visibility character varying(50) COLLATE pg_catalog."default",
    CONSTRAINT app_configs_pkey PRIMARY KEY (id),
    CONSTRAINT app_configs_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES master.app_configs (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
TABLESPACE pg_default;


CREATE INDEX app_configs_created_by
    ON master.app_configs USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: app_configs_modified_by

-- DROP INDEX master.app_configs_modified_by;

CREATE INDEX app_configs_modified_by
    ON master.app_configs USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: app_configs_record_id

-- DROP INDEX master.app_configs_record_id;

CREATE INDEX app_configs_record_id
    ON master.app_configs USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-- Table: master.charging_connectors

-- DROP TABLE master.charging_connectors;

CREATE TABLE IF NOT EXISTS master.charging_connectors
(
    id bigint NOT NULL DEFAULT nextval('master.charging_connectors_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    standard_name character varying(50) COLLATE pg_catalog."default" NOT NULL,
    description character varying(100) COLLATE pg_catalog."default",
    icon_image bytea,
    CONSTRAINT charging_connectors_pkey PRIMARY KEY (id),
    CONSTRAINT charging_connectors_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES master.charging_connectors (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

-- Index: charging_connectors_created_by

-- DROP INDEX master.charging_connectors_created_by;

CREATE INDEX charging_connectors_created_by
    ON master.charging_connectors USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: charging_connectors_modified_by

-- DROP INDEX master.charging_connectors_modified_by;

CREATE INDEX charging_connectors_modified_by
    ON master.charging_connectors USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: charging_connectors_record_id

-- DROP INDEX master.charging_connectors_record_id;

CREATE INDEX charging_connectors_record_id
    ON master.charging_connectors USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;



-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------



-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: master.equipment_type_masters

-- DROP TABLE master.equipment_type_masters;

CREATE TABLE IF NOT EXISTS master.equipment_type_masters
(
    id bigint NOT NULL DEFAULT nextval('master.equipment_type_masters_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    type character varying(50) COLLATE pg_catalog."default" NOT NULL,
    icon_image bytea NOT NULL,
    rank integer NOT NULL,
    description character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT equipment_type_masters_pkey PRIMARY KEY (id),
    CONSTRAINT equipment_type_masters_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES master.equipment_type_masters (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

CREATE INDEX equipment_type_masters_created_by
    ON master.equipment_type_masters USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: equipment_type_masters_modified_by

-- DROP INDEX master.equipment_type_masters_modified_by;

CREATE INDEX equipment_type_masters_modified_by
    ON master.equipment_type_masters USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: equipment_type_masters_record_id

-- DROP INDEX master.equipment_type_masters_record_id;

CREATE INDEX equipment_type_masters_record_id
    ON master.equipment_type_masters USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;


-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: master.rated_powers

-- DROP TABLE master.rated_powers;

CREATE TABLE IF NOT EXISTS master.rated_powers
(
    id bigint NOT NULL DEFAULT nextval('master.rated_powers_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    power real NOT NULL,
    power_unit character varying(50) COLLATE pg_catalog."default" NOT NULL,
    charge_type character varying(50) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT rated_powers_pkey PRIMARY KEY (id),
    CONSTRAINT rated_powers_record_name_fkey FOREIGN KEY (record_id)
        REFERENCES master.rated_powers (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: rated_powers_created_by

-- DROP INDEX master.rated_powers_created_by;

CREATE INDEX rated_powers_created_by
    ON master.rated_powers USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: rated_powers_modified_by

-- DROP INDEX master.rated_powers_modified_by;

CREATE INDEX rated_powers_modified_by
    ON master.rated_powers USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: rated_powers_record_name

-- DROP INDEX master.rated_powers_record_name;

CREATE INDEX rated_powers_record_name
    ON master.rated_powers USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: master.segments_of_day

-- DROP TABLE master.segments_of_day;

CREATE TABLE IF NOT EXISTS master.segments_of_day
(
    id integer NOT NULL DEFAULT nextval('master.segments_of_day_id_seq'::regclass),
    name character varying(20) COLLATE pg_catalog."default" NOT NULL,
    key character varying(50) COLLATE pg_catalog."default" NOT NULL,
    segment_start_time time without time zone NOT NULL,
    segment_end_time time without time zone NOT NULL,
    icon_image bytea,
    CONSTRAINT segments_of_day_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;



-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: master.service_masters

-- DROP TABLE master.service_masters;

CREATE TABLE IF NOT EXISTS master.service_masters
(
    id bigint NOT NULL DEFAULT nextval('master.service_masters_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    "primary" boolean,
    name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    type character varying(50) COLLATE pg_catalog."default" NOT NULL,
    description character varying(150) COLLATE pg_catalog."default",
    service_rank integer,
    parameters hstore,
    icon_image bytea,
    CONSTRAINT service_masters_pkey PRIMARY KEY (id),
    CONSTRAINT service_masters_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES master.service_masters (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: service_masters_created_by

-- DROP INDEX master.service_masters_created_by;

CREATE INDEX service_masters_created_by
    ON master.service_masters USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: service_masters_modified_by

-- DROP INDEX master.service_masters_modified_by;

CREATE INDEX service_masters_modified_by
    ON master.service_masters USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: service_masters_parameters

-- DROP INDEX master.service_masters_parameters;

CREATE INDEX service_masters_parameters
    ON master.service_masters USING gin
    (parameters)
    TABLESPACE pg_default;
-- Index: service_masters_record_id

-- DROP INDEX master.service_masters_record_id;

CREATE INDEX service_masters_record_id
    ON master.service_masters USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: master.service_rate_table

-- DROP TABLE master.service_rate_table;

CREATE TABLE IF NOT EXISTS master.service_rate_table
(
    id bigint NOT NULL DEFAULT nextval('master.service_rate_table_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    description character varying(30) COLLATE pg_catalog."default",
    consumption_unit character varying(50) COLLATE pg_catalog."default" NOT NULL,
    consumption_from numeric(10,5) NOT NULL,
    consumption_to numeric(10,5) NOT NULL,
    rate numeric(10,5) NOT NULL,
    rate_unit character varying(50) COLLATE pg_catalog."default" NOT NULL,
    covered_rated_powers integer[],
    days_of_week bigint NOT NULL DEFAULT 127,
    segments_of_day integer[],
    service_rate_id bigint,
    CONSTRAINT service_rate_table_pkey PRIMARY KEY (id),
    CONSTRAINT service_rate_table_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES master.service_rate_table (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: service_rate_table_created_by

-- DROP INDEX master.service_rate_table_created_by;

CREATE INDEX service_rate_table_created_by
    ON master.service_rate_table USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: service_rate_table_modified_by

-- DROP INDEX master.service_rate_table_modified_by;

CREATE INDEX service_rate_table_modified_by
    ON master.service_rate_table USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: service_rate_table_record_id

-- DROP INDEX master.service_rate_table_record_id;

CREATE INDEX service_rate_table_record_id
    ON master.service_rate_table USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: master.service_rates

-- DROP TABLE master.service_rates;

CREATE TABLE IF NOT EXISTS master.service_rates
(
    id bigint NOT NULL DEFAULT nextval('master.service_rates_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    "primary" boolean,
    description character varying(100) COLLATE pg_catalog."default" NOT NULL,
    service_master_record_id bigint NOT NULL,
    CONSTRAINT service_rates_pkey PRIMARY KEY (id),
    CONSTRAINT service_rates_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES master.service_rates (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT service_rates_service_master_record_id_fkey FOREIGN KEY (service_master_record_id)
        REFERENCES master.service_masters (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: service_rates_created_by

-- DROP INDEX master.service_rates_created_by;

CREATE INDEX service_rates_created_by
    ON master.service_rates USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: service_rates_modified_by

-- DROP INDEX master.service_rates_modified_by;

CREATE INDEX service_rates_modified_by
    ON master.service_rates USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: service_rates_record_id

-- DROP INDEX master.service_rates_record_id;

CREATE INDEX service_rates_record_id
    ON master.service_rates USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: service_rates_service_master_record_id

-- DROP INDEX master.service_rates_service_master_record_id;

CREATE INDEX service_rates_service_master_record_id
    ON master.service_rates USING btree
    (service_master_record_id ASC NULLS LAST)
    TABLESPACE pg_default;


-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------


-- Table: master.station_operating_time_master

-- DROP TABLE master.station_operating_time_master;

CREATE TABLE IF NOT EXISTS master.station_operating_time_master
(
    id bigint NOT NULL DEFAULT nextval('master.station_operating_time_master_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    operation_type character varying(20) COLLATE pg_catalog."default" NOT NULL,
    window_start_time time without time zone NOT NULL,
    window_end_time time without time zone NOT NULL,
    duration interval NOT NULL,
    time_offset interval NOT NULL,
    CONSTRAINT station_operating_time_master_pkey PRIMARY KEY (id),
    CONSTRAINT station_operating_time_master_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES master.station_operating_time_master (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;
-- Index: station_operating_time_master_created_by

-- DROP INDEX master.station_operating_time_master_created_by;

CREATE INDEX station_operating_time_master_created_by
    ON master.station_operating_time_master USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_operating_time_master_modified_by

-- DROP INDEX master.station_operating_time_master_modified_by;

CREATE INDEX station_operating_time_master_modified_by
    ON master.station_operating_time_master USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_operating_time_master_record_id

-- DROP INDEX master.station_operating_time_master_record_id;

CREATE INDEX station_operating_time_master_record_id
    ON master.station_operating_time_master USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------


-- Table: master.token_conversion_rates

-- DROP TABLE master.token_conversion_rates;

CREATE TABLE IF NOT EXISTS master.token_conversion_rates
(
    id integer NOT NULL DEFAULT nextval('master.token_conversion_rates_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id integer NOT NULL,
    conversion_rate numeric(10,5) NOT NULL,
    conversion_from_unit character varying(255) COLLATE pg_catalog."default" NOT NULL,
    conversion_to_unit character varying(255) COLLATE pg_catalog."default" NOT NULL,
    description character varying(100) COLLATE pg_catalog."default",
    CONSTRAINT token_conversion_rates_pkey PRIMARY KEY (id),
    CONSTRAINT token_conversion_rates_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES master.token_conversion_rates (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: token_conversion_rates_created_by

-- DROP INDEX master.token_conversion_rates_created_by;

CREATE INDEX token_conversion_rates_created_by
    ON master.token_conversion_rates USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: token_conversion_rates_modified_by

-- DROP INDEX master.token_conversion_rates_modified_by;

CREATE INDEX token_conversion_rates_modified_by
    ON master.token_conversion_rates USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: token_conversion_rates_record_id

-- DROP INDEX master.token_conversion_rates_record_id;

CREATE INDEX token_conversion_rates_record_id
    ON master.token_conversion_rates USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: master.vehicle_masters

-- DROP TABLE master.vehicle_masters;

CREATE TABLE IF NOT EXISTS master.vehicle_masters
(
    id integer NOT NULL DEFAULT nextval('master.vehicle_masters_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id integer NOT NULL,
    brand character varying(100) COLLATE pg_catalog."default" NOT NULL,
    model character varying(120) COLLATE pg_catalog."default" NOT NULL,
    manufacturing_year integer NOT NULL,
    image bytea,
    wheels integer,
    swappable_battery boolean,
    swappable_battery_count integer,
    class_of_vehicle character varying(50) COLLATE pg_catalog."default",
    charging_connector_record_id bigint NOT NULL,
    connector_record_ids integer[],
    CONSTRAINT vehicle_masters_pkey PRIMARY KEY (id),
    CONSTRAINT vehicle_masters_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES master.vehicle_masters (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: vehicle_masters_charging_connector_record_id

-- DROP INDEX master.vehicle_masters_charging_connector_record_id;

CREATE INDEX vehicle_masters_charging_connector_record_id
    ON master.vehicle_masters USING btree
    (charging_connector_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: vehicle_masters_created_by

-- DROP INDEX master.vehicle_masters_created_by;

CREATE INDEX vehicle_masters_created_by
    ON master.vehicle_masters USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: vehicle_masters_modified_by

-- DROP INDEX master.vehicle_masters_modified_by;

CREATE INDEX vehicle_masters_modified_by
    ON master.vehicle_masters USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: vehicle_masters_record_id

-- DROP INDEX master.vehicle_masters_record_id;

CREATE INDEX vehicle_masters_record_id
    ON master.vehicle_masters USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: transactional.accounts

-- DROP TABLE transactional.accounts;

CREATE TABLE IF NOT EXISTS transactional.accounts
(
    id uuid NOT NULL,
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    record_id uuid NOT NULL,
    alias_name character varying(50) COLLATE pg_catalog."default",
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    type character varying(50) COLLATE pg_catalog."default",
    CONSTRAINT accounts_pkey PRIMARY KEY (id),
    CONSTRAINT accounts_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES transactional.accounts (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: accounts_created_by

-- DROP INDEX transactional.accounts_created_by;

CREATE INDEX accounts_created_by
    ON transactional.accounts USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: accounts_modified_by

-- DROP INDEX transactional.accounts_modified_by;

CREATE INDEX accounts_modified_by
    ON transactional.accounts USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: accounts_record_id

-- DROP INDEX transactional.accounts_record_id;

CREATE INDEX accounts_record_id
    ON transactional.accounts USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-- Trigger: tr_accounts_wallets_creation

-- DROP TRIGGER tr_accounts_wallets_creation ON transactional.accounts;

CREATE TRIGGER tr_accounts_wallets_creation
    AFTER INSERT
    ON transactional.accounts
    FOR EACH ROW
    EXECUTE FUNCTION public.fn_insert_wallet_for_new_account();

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: transactional.stations

-- DROP TABLE transactional.stations;

CREATE TABLE IF NOT EXISTS transactional.stations
(
    id uuid NOT NULL,
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    record_id uuid NOT NULL,
    alias_name character varying(50) COLLATE pg_catalog."default" NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    station_code character varying(120) COLLATE pg_catalog."default" NOT NULL,
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    location_latitude numeric(15,10) NOT NULL,
    location_longitude numeric(15,10) NOT NULL,
    address character varying(255) COLLATE pg_catalog."default",
    "pinCode" character varying(10) COLLATE pg_catalog."default",
    contact_number character varying(12) COLLATE pg_catalog."default",
    website character varying(100) COLLATE pg_catalog."default",
    has_hygge_box boolean,
    verified boolean NOT NULL,
    type character varying(50) COLLATE pg_catalog."default",
    CONSTRAINT stations_pkey PRIMARY KEY (id),
    CONSTRAINT stations_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES transactional.stations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: stations_created_by

-- DROP INDEX transactional.stations_created_by;

CREATE INDEX stations_created_by
    ON transactional.stations USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: stations_modified_by

-- DROP INDEX transactional.stations_modified_by;

CREATE INDEX stations_modified_by
    ON transactional.stations USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: stations_record_id

-- DROP INDEX transactional.stations_record_id;

CREATE INDEX stations_record_id
    ON transactional.stations USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: transactional.users

-- DROP TABLE transactional.users;

CREATE TABLE IF NOT EXISTS transactional.users
(
    id uuid NOT NULL,
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    record_id uuid NOT NULL,
    alias_name character varying(50) COLLATE pg_catalog."default",
    customer_id character varying(50) COLLATE pg_catalog."default",
    phone_number character varying(12) COLLATE pg_catalog."default",
    name character varying(50) COLLATE pg_catalog."default",
    email character varying(50) COLLATE pg_catalog."default",
    pin_code character varying(10) COLLATE pg_catalog."default",
    profile_image bytea,
    licence_number character varying(15) COLLATE pg_catalog."default",
    licence_image bytea,
    verified boolean NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    type character varying(50) COLLATE pg_catalog."default",
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES transactional.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: users_created_by

-- DROP INDEX transactional.users_created_by;

CREATE INDEX users_created_by
    ON transactional.users USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: users_modified_by

-- DROP INDEX transactional.users_modified_by;

CREATE INDEX users_modified_by
    ON transactional.users USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: users_record_id

-- DROP INDEX transactional.users_record_id;

CREATE INDEX users_record_id
    ON transactional.users USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-- Trigger: tr_users_accounts_creation

-- DROP TRIGGER tr_users_accounts_creation ON transactional.users;

CREATE TRIGGER tr_users_accounts_creation
    AFTER INSERT
    ON transactional.users
    FOR EACH ROW
    EXECUTE FUNCTION public.fn_insert_account_for_new_user();

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: transactional.vehicles

-- DROP TABLE transactional.vehicles;

CREATE TABLE IF NOT EXISTS transactional.vehicles
(
    id uuid NOT NULL,
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id uuid NOT NULL,
    registration_number character varying(50) COLLATE pg_catalog."default" NOT NULL,
    registration_certificate_image bytea,
    registration_plate_number character varying(20) COLLATE pg_catalog."default",
    verified boolean NOT NULL,
    vehicle_master_id integer NOT NULL,
    vehicle_master_json jsonb,
    user_record_id uuid NOT NULL,
    CONSTRAINT vehicles_pkey PRIMARY KEY (id),
    CONSTRAINT vehicles_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES transactional.vehicles (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT vehicles_user_record_id_fkey FOREIGN KEY (user_record_id)
        REFERENCES transactional.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT vehicles_vehicle_master_id_fkey FOREIGN KEY (vehicle_master_id)
        REFERENCES master.vehicle_masters (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: vehicles_created_by

-- DROP INDEX transactional.vehicles_created_by;

CREATE INDEX vehicles_created_by
    ON transactional.vehicles USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: vehicles_modified_by

-- DROP INDEX transactional.vehicles_modified_by;

CREATE INDEX vehicles_modified_by
    ON transactional.vehicles USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: vehicles_record_id

-- DROP INDEX transactional.vehicles_record_id;

CREATE INDEX vehicles_record_id
    ON transactional.vehicles USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: vehicles_user_record_id

-- DROP INDEX transactional.vehicles_user_record_id;

CREATE INDEX vehicles_user_record_id
    ON transactional.vehicles USING btree
    (user_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: vehicles_vehicle_master_id

-- DROP INDEX transactional.vehicles_vehicle_master_id;

CREATE INDEX vehicles_vehicle_master_id
    ON transactional.vehicles USING btree
    (vehicle_master_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: vehicles_vehicle_master_json

-- DROP INDEX transactional.vehicles_vehicle_master_json;

CREATE INDEX vehicles_vehicle_master_json
    ON transactional.vehicles USING gin
    (vehicle_master_json)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: transactional.verifications

-- DROP TABLE transactional.verifications;

CREATE TABLE IF NOT EXISTS transactional.verifications
(
    id bigint NOT NULL DEFAULT nextval('transactional.verifications_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    registered_by uuid NOT NULL,
    registered_user_record_id uuid,
    registered_vehicle_record_id uuid,
    registered_station_record_id uuid,
    verified_by uuid,
    verification_time timestamp without time zone,
    verification_status character varying(50) COLLATE pg_catalog."default" NOT NULL,
    verifier_remark character varying(255) COLLATE pg_catalog."default",
    verification_expiry timestamp without time zone,
    CONSTRAINT verifications_pkey PRIMARY KEY (id),
    CONSTRAINT verifications_registered_by_fkey FOREIGN KEY (registered_by)
        REFERENCES transactional.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT verifications_registered_station_record_id_fkey FOREIGN KEY (registered_station_record_id)
        REFERENCES transactional.stations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT verifications_registered_user_record_id_fkey FOREIGN KEY (registered_user_record_id)
        REFERENCES transactional.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT verifications_registered_vehicle_record_id_fkey FOREIGN KEY (registered_vehicle_record_id)
        REFERENCES transactional.vehicles (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT verifications_verified_by_fkey FOREIGN KEY (verified_by)
        REFERENCES transactional.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;
-- Index: verifications_created_by

-- DROP INDEX transactional.verifications_created_by;

CREATE INDEX verifications_created_by
    ON transactional.verifications USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: verifications_modified_by

-- DROP INDEX transactional.verifications_modified_by;

CREATE INDEX verifications_modified_by
    ON transactional.verifications USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: verifications_registered_by

-- DROP INDEX transactional.verifications_registered_by;

CREATE INDEX verifications_registered_by
    ON transactional.verifications USING btree
    (registered_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: verifications_registered_station_record_id

-- DROP INDEX transactional.verifications_registered_station_record_id;

CREATE INDEX verifications_registered_station_record_id
    ON transactional.verifications USING btree
    (registered_station_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: verifications_registered_user_record_id

-- DROP INDEX transactional.verifications_registered_user_record_id;

CREATE INDEX verifications_registered_user_record_id
    ON transactional.verifications USING btree
    (registered_user_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: verifications_registered_vehicle_record_id

-- DROP INDEX transactional.verifications_registered_vehicle_record_id;

CREATE INDEX verifications_registered_vehicle_record_id
    ON transactional.verifications USING btree
    (registered_vehicle_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: verifications_verified_by

-- DROP INDEX transactional.verifications_verified_by;

CREATE INDEX verifications_verified_by
    ON transactional.verifications USING btree
    (verified_by ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-- Table: transactional.station_assignment

-- DROP TABLE transactional.station_assignment;

CREATE TABLE IF NOT EXISTS transactional.station_assignment
(
    id bigint NOT NULL DEFAULT nextval('transactional.station_assignment_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    user_record_id uuid NOT NULL,
    station_record_id uuid NOT NULL,
    verified boolean,
    CONSTRAINT station_assignment_pkey PRIMARY KEY (id),
    CONSTRAINT station_assignment_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES transactional.station_assignment (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT station_assignment_station_record_id_fkey FOREIGN KEY (station_record_id)
        REFERENCES transactional.stations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT station_assignment_user_record_id_fkey FOREIGN KEY (user_record_id)
        REFERENCES transactional.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;
-- Index: station_assignment_created_by

-- DROP INDEX transactional.station_assignment_created_by;

CREATE INDEX station_assignment_created_by
    ON transactional.station_assignment USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_assignment_modified_by

-- DROP INDEX transactional.station_assignment_modified_by;

CREATE INDEX station_assignment_modified_by
    ON transactional.station_assignment USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_assignment_record_id

-- DROP INDEX transactional.station_assignment_record_id;

CREATE INDEX station_assignment_record_id
    ON transactional.station_assignment USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_assignment_station_record_id

-- DROP INDEX transactional.station_assignment_station_record_id;

CREATE INDEX station_assignment_station_record_id
    ON transactional.station_assignment USING btree
    (station_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_assignment_user_record_id

-- DROP INDEX transactional.station_assignment_user_record_id;

CREATE INDEX station_assignment_user_record_id
    ON transactional.station_assignment USING btree
    (user_record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: transactional.station_medias

-- DROP TABLE transactional.station_medias;

CREATE TABLE IF NOT EXISTS transactional.station_medias
(
    id integer NOT NULL DEFAULT nextval('transactional.station_medias_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    station_record_id uuid NOT NULL,
    image bytea NOT NULL,
    image_rank integer NOT NULL,
    CONSTRAINT station_medias_pkey PRIMARY KEY (id),
    CONSTRAINT station_medias_station_record_id_fkey FOREIGN KEY (station_record_id)
        REFERENCES transactional.stations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: station_medias_created_by

-- DROP INDEX transactional.station_medias_created_by;

CREATE INDEX station_medias_created_by
    ON transactional.station_medias USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_medias_modified_by

-- DROP INDEX transactional.station_medias_modified_by;

CREATE INDEX station_medias_modified_by
    ON transactional.station_medias USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_medias_station_record_id

-- DROP INDEX transactional.station_medias_station_record_id;

CREATE INDEX station_medias_station_record_id
    ON transactional.station_medias USING btree
    (station_record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: transactional.station_operation_break_details

-- DROP TABLE transactional.station_operation_break_details;

CREATE TABLE IF NOT EXISTS transactional.station_operation_break_details
(
    id bigint NOT NULL DEFAULT nextval('transactional.station_operation_break_details_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    station_record_id uuid NOT NULL,
    break_days bigint NOT NULL,
    break_start_time time without time zone NOT NULL,
    break_end_time time without time zone NOT NULL,
    description character varying(500) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT station_operation_break_details_pkey PRIMARY KEY (id),
    CONSTRAINT station_operation_break_details_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES transactional.station_operation_break_details (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT station_operation_break_details_station_record_id_fkey FOREIGN KEY (station_record_id)
        REFERENCES transactional.stations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;
-- Index: station_operation_break_details_created_by

-- DROP INDEX transactional.station_operation_break_details_created_by;

CREATE INDEX station_operation_break_details_created_by
    ON transactional.station_operation_break_details USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_operation_break_details_modified_by

-- DROP INDEX transactional.station_operation_break_details_modified_by;

CREATE INDEX station_operation_break_details_modified_by
    ON transactional.station_operation_break_details USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_operation_break_details_record_id

-- DROP INDEX transactional.station_operation_break_details_record_id;

CREATE INDEX station_operation_break_details_record_id
    ON transactional.station_operation_break_details USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_operation_break_details_station_record_id

-- DROP INDEX transactional.station_operation_break_details_station_record_id;

CREATE INDEX station_operation_break_details_station_record_id
    ON transactional.station_operation_break_details USING btree
    (station_record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: transactional.station_operation_details

-- DROP TABLE transactional.station_operation_details;

CREATE TABLE IF NOT EXISTS transactional.station_operation_details
(
    id bigint NOT NULL DEFAULT nextval('transactional.station_operation_details_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    station_record_id uuid NOT NULL,
    operating_days bigint NOT NULL,
    operation_start_time time without time zone NOT NULL,
    operation_end_time time without time zone NOT NULL,
    timezone character varying(5) COLLATE pg_catalog."default",
    CONSTRAINT station_operation_details_pkey PRIMARY KEY (id),
    CONSTRAINT station_operation_details_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES transactional.station_operation_details (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT station_operation_details_station_record_id_fkey FOREIGN KEY (station_record_id)
        REFERENCES transactional.stations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;
-- Index: station_operation_details_created_by

-- DROP INDEX transactional.station_operation_details_created_by;

CREATE INDEX station_operation_details_created_by
    ON transactional.station_operation_details USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_operation_details_modified_by

-- DROP INDEX transactional.station_operation_details_modified_by;

CREATE INDEX station_operation_details_modified_by
    ON transactional.station_operation_details USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_operation_details_record_id

-- DROP INDEX transactional.station_operation_details_record_id;

CREATE INDEX station_operation_details_record_id
    ON transactional.station_operation_details USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_operation_details_station_record_id

-- DROP INDEX transactional.station_operation_details_station_record_id;

CREATE INDEX station_operation_details_station_record_id
    ON transactional.station_operation_details USING btree
    (station_record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: transactional.station_services

-- DROP TABLE transactional.station_services;

CREATE TABLE IF NOT EXISTS transactional.station_services
(
    id bigint NOT NULL DEFAULT nextval('transactional.station_services_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    station_record_id uuid NOT NULL,
    service_master_record_id bigint NOT NULL,
    custom_service_rate_record_id bigint,
    CONSTRAINT station_services_pkey PRIMARY KEY (id),
    CONSTRAINT station_services_custom_service_rate_record_id_fkey FOREIGN KEY (custom_service_rate_record_id)
        REFERENCES master.service_rates (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT station_services_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES transactional.station_services (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT station_services_service_master_record_id_fkey FOREIGN KEY (service_master_record_id)
        REFERENCES master.service_masters (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT station_services_station_record_id_fkey FOREIGN KEY (station_record_id)
        REFERENCES transactional.stations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: station_services_created_by

-- DROP INDEX transactional.station_services_created_by;

CREATE INDEX station_services_created_by
    ON transactional.station_services USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_services_custom_service_rate_record_id

-- DROP INDEX transactional.station_services_custom_service_rate_record_id;

CREATE INDEX station_services_custom_service_rate_record_id
    ON transactional.station_services USING btree
    (custom_service_rate_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_services_modified_by

-- DROP INDEX transactional.station_services_modified_by;

CREATE INDEX station_services_modified_by
    ON transactional.station_services USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_services_record_id

-- DROP INDEX transactional.station_services_record_id;

CREATE INDEX station_services_record_id
    ON transactional.station_services USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_services_service_master_record_id

-- DROP INDEX transactional.station_services_service_master_record_id;

CREATE INDEX station_services_service_master_record_id
    ON transactional.station_services USING btree
    (service_master_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_services_station_record_id

-- DROP INDEX transactional.station_services_station_record_id;

CREATE INDEX station_services_station_record_id
    ON transactional.station_services USING btree
    (station_record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------



CREATE TABLE IF NOT EXISTS auth.auth_attempts
(
    txn_id uuid NOT NULL,
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    phone_number character varying(12) COLLATE pg_catalog."default" NOT NULL,
    country_code character varying(4) COLLATE pg_catalog."default",
    device_token character varying(100) COLLATE pg_catalog."default" NOT NULL,
    otp character varying(6) COLLATE pg_catalog."default",
    state character varying(50) COLLATE pg_catalog."default" NOT NULL,
    state_desc character varying(100) COLLATE pg_catalog."default" NOT NULL,
    verification_attempt_count integer NOT NULL,
    gateway_send_otp_res_status character varying(10) COLLATE pg_catalog."default",
    gateway_send_otp_res_body jsonb,
    claims_issued character varying(100) COLLATE pg_catalog."default",
    backing_txn_id uuid,
    CONSTRAINT auth_attempts_pkey PRIMARY KEY (txn_id)
)

TABLESPACE pg_default;


-- Index: auth_attempts_created_by

-- DROP INDEX auth.auth_attempts_created_by;

CREATE INDEX auth_attempts_created_by
    ON auth.auth_attempts USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: auth_attempts_gateway_send_otp_res_body

-- DROP INDEX auth.auth_attempts_gateway_send_otp_res_body;

CREATE INDEX auth_attempts_gateway_send_otp_res_body
    ON auth.auth_attempts USING gin
    (gateway_send_otp_res_body)
    TABLESPACE pg_default;
-- Index: auth_attempts_modified_by

-- DROP INDEX auth.auth_attempts_modified_by;

CREATE INDEX auth_attempts_modified_by
    ON auth.auth_attempts USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;

--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------

-- Table: auth.groups

-- DROP TABLE auth.groups;

CREATE TABLE IF NOT EXISTS auth.groups
(
    id bigint NOT NULL DEFAULT nextval('auth.groups_id_seq'::regclass),
    name character varying(50) COLLATE pg_catalog."default" NOT NULL,
    description character varying(100) COLLATE pg_catalog."default",
    CONSTRAINT groups_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;


-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------


-- Table: auth.permissions

-- DROP TABLE auth.permissions;

CREATE TABLE IF NOT EXISTS auth.permissions
(
    id bigint NOT NULL DEFAULT nextval('auth.permissions_id_seq'::regclass),
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    description character varying(100) COLLATE pg_catalog."default",
    resource_name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    can_retrieve boolean NOT NULL,
    can_search boolean NOT NULL,
    can_create boolean NOT NULL,
    can_update boolean NOT NULL,
    can_delete boolean NOT NULL,
    CONSTRAINT permissions_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

-- Index: permissions_name

-- DROP INDEX auth.permissions_name;

CREATE UNIQUE INDEX permissions_name
    ON auth.permissions USING btree
    (name COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

----------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------

-- Table: auth.roles

-- DROP TABLE auth.roles;

CREATE TABLE IF NOT EXISTS auth.roles
(
    id bigint NOT NULL DEFAULT nextval('auth.roles_id_seq'::regclass),
    name character varying(50) COLLATE pg_catalog."default" NOT NULL,
    description character varying(100) COLLATE pg_catalog."default",
    CONSTRAINT roles_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

-- Index: roles_name

-- DROP INDEX auth.roles_name;

CREATE UNIQUE INDEX roles_name
    ON auth.roles USING btree
    (name COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;


-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------

-- Table: auth.group_role_rel

-- DROP TABLE auth.group_role_rel;

CREATE TABLE IF NOT EXISTS auth.group_role_rel
(
    group_id bigint NOT NULL,
    role_id bigint NOT NULL,
    CONSTRAINT group_role_rel_pkey PRIMARY KEY (group_id, role_id),
    CONSTRAINT group_role_rel_group_id_fkey FOREIGN KEY (group_id)
        REFERENCES auth.groups (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT group_role_rel_role_id_fkey FOREIGN KEY (role_id)
        REFERENCES auth.roles (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

-- Index: group_role_rel_group_id

-- DROP INDEX auth.group_role_rel_group_id;

CREATE INDEX group_role_rel_group_id
    ON auth.group_role_rel USING btree
    (group_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: group_role_rel_role_id

-- DROP INDEX auth.group_role_rel_role_id;

CREATE INDEX group_role_rel_role_id
    ON auth.group_role_rel USING btree
    (role_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------



-- Table: auth.role_permission_rel

-- DROP TABLE auth.role_permission_rel;

CREATE TABLE IF NOT EXISTS auth.role_permission_rel
(
    role_id bigint NOT NULL,
    permission_id bigint NOT NULL,
    CONSTRAINT role_permission_rel_pkey PRIMARY KEY (role_id, permission_id),
    CONSTRAINT role_permission_rel_permission_id_fkey FOREIGN KEY (permission_id)
        REFERENCES auth.permissions (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT role_permission_rel_role_id_fkey FOREIGN KEY (role_id)
        REFERENCES auth.roles (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

-- Index: role_permission_rel_permission_id

-- DROP INDEX auth.role_permission_rel_permission_id;

CREATE INDEX role_permission_rel_permission_id
    ON auth.role_permission_rel USING btree
    (permission_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: role_permission_rel_role_id

-- DROP INDEX auth.role_permission_rel_role_id;

CREATE INDEX role_permission_rel_role_id
    ON auth.role_permission_rel USING btree
    (role_id ASC NULLS LAST)
    TABLESPACE pg_default;

-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------


-- Table: auth.user_group_rel

-- DROP TABLE auth.user_group_rel;

CREATE TABLE IF NOT EXISTS auth.user_group_rel
(
    id bigint NOT NULL DEFAULT nextval('auth.user_group_rel_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    user_record_id uuid NOT NULL,
    group_id bigint NOT NULL,
    record_id bigint NOT NULL DEFAULT nextval('auth.user_group_rel_id_seq'::regclass),
    CONSTRAINT user_group_rel_pkey PRIMARY KEY (id),
    CONSTRAINT user_group_rel_group_id_fkey FOREIGN KEY (group_id)
        REFERENCES auth.groups (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT user_group_rel_user_record_id_fkey FOREIGN KEY (user_record_id)
        REFERENCES transactional.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

-- Index: user_group_rel_created_by

-- DROP INDEX auth.user_group_rel_created_by;

CREATE INDEX user_group_rel_created_by
    ON auth.user_group_rel USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: user_group_rel_group_id

-- DROP INDEX auth.user_group_rel_group_id;

CREATE INDEX user_group_rel_group_id
    ON auth.user_group_rel USING btree
    (group_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: user_group_rel_modified_by

-- DROP INDEX auth.user_group_rel_modified_by;

CREATE INDEX user_group_rel_modified_by
    ON auth.user_group_rel USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: user_group_rel_user_record_id

-- DROP INDEX auth.user_group_rel_user_record_id;

CREATE INDEX user_group_rel_user_record_id
    ON auth.user_group_rel USING btree
    (user_record_id ASC NULLS LAST)
    TABLESPACE pg_default;

--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------


-- Table: payment.orders

-- DROP TABLE payment.orders;

CREATE TABLE IF NOT EXISTS payment.orders
(
    order_id character varying(50) COLLATE pg_catalog."default" NOT NULL,
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    order_summary character varying(100) COLLATE pg_catalog."default",
    total numeric(10,5) NOT NULL,
    order_status character varying(10) COLLATE pg_catalog."default" NOT NULL,
    order_type character varying(100) COLLATE pg_catalog."default",
    CONSTRAINT orders_pkey PRIMARY KEY (order_id)
)

TABLESPACE pg_default;


-- Index: orders_created_by

-- DROP INDEX payment.orders_created_by;

CREATE INDEX orders_created_by
    ON payment.orders USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: orders_modified_by

-- DROP INDEX payment.orders_modified_by;

CREATE INDEX orders_modified_by
    ON payment.orders USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-- Table: transactional.equipments

-- DROP TABLE transactional.equipments;

CREATE TABLE IF NOT EXISTS transactional.equipments
(
    id bigint NOT NULL DEFAULT nextval('transactional.equipments_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    type character varying(50) COLLATE pg_catalog."default" NOT NULL,
    status character varying(50) COLLATE pg_catalog."default" DEFAULT 'ACTIVE'::character varying,
    serial_id character varying COLLATE pg_catalog."default",
    product_id character varying COLLATE pg_catalog."default",
    model_id character varying COLLATE pg_catalog."default",
    asset_id character varying COLLATE pg_catalog."default",
    CONSTRAINT equipments_pkey PRIMARY KEY (id),
    CONSTRAINT equipments_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES transactional.equipments (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: equipments_created_by

-- DROP INDEX transactional.equipments_created_by;

CREATE INDEX equipments_created_by
    ON transactional.equipments USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: equipments_modified_by

-- DROP INDEX transactional.equipments_modified_by;

CREATE INDEX equipments_modified_by
    ON transactional.equipments USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: equipments_record_id

-- DROP INDEX transactional.equipments_record_id;

CREATE INDEX equipments_record_id
    ON transactional.equipments USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: payment.payments

-- DROP TABLE payment.payments;

CREATE TABLE IF NOT EXISTS payment.payments
(
    id uuid NOT NULL,
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    order_id character varying(50) COLLATE pg_catalog."default" NOT NULL,
    sender uuid NOT NULL,
    receiver uuid NOT NULL,
    order_amount numeric(10,5) NOT NULL,
    order_date date NOT NULL,
    payment_status character varying(50) COLLATE pg_catalog."default" NOT NULL,
    gateway_response jsonb,
    client_response jsonb,
    device_id bigint,
    gateway_name character varying(50) COLLATE pg_catalog."default",
    comment character varying(120) COLLATE pg_catalog."default",
    CONSTRAINT payments_pkey PRIMARY KEY (id),
    CONSTRAINT payments_device_id_fkey FOREIGN KEY (device_id)
        REFERENCES transactional.equipments (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT payments_order_id_fkey FOREIGN KEY (order_id)
        REFERENCES payment.orders (order_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT payments_receiver_fkey FOREIGN KEY (receiver)
        REFERENCES transactional.accounts (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT payments_sender_fkey FOREIGN KEY (sender)
        REFERENCES transactional.accounts (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: payments_client_response

-- DROP INDEX payment.payments_client_response;

CREATE INDEX payments_client_response
    ON payment.payments USING gin
    (client_response)
    TABLESPACE pg_default;
-- Index: payments_created_by

-- DROP INDEX payment.payments_created_by;

CREATE INDEX payments_created_by
    ON payment.payments USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: payments_device_id

-- DROP INDEX payment.payments_device_id;

CREATE INDEX payments_device_id
    ON payment.payments USING btree
    (device_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: payments_gateway_response

-- DROP INDEX payment.payments_gateway_response;

CREATE INDEX payments_gateway_response
    ON payment.payments USING gin
    (gateway_response)
    TABLESPACE pg_default;
-- Index: payments_modified_by

-- DROP INDEX payment.payments_modified_by;

CREATE INDEX payments_modified_by
    ON payment.payments USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: payments_order_id

-- DROP INDEX payment.payments_order_id;

CREATE INDEX payments_order_id
    ON payment.payments USING btree
    (order_id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: payments_receiver

-- DROP INDEX payment.payments_receiver;

CREATE INDEX payments_receiver
    ON payment.payments USING btree
    (receiver ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: payments_sender

-- DROP INDEX payment.payments_sender;

CREATE INDEX payments_sender
    ON payment.payments USING btree
    (sender ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: payment.invoices

-- DROP TABLE payment.invoices;

CREATE TABLE IF NOT EXISTS payment.invoices
(
    id bigint NOT NULL DEFAULT nextval('payment.invoices_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    invoice_number uuid NOT NULL,
    order_id character varying(50) COLLATE pg_catalog."default" NOT NULL,
    comment character varying(50) COLLATE pg_catalog."default",
    payment_id uuid NOT NULL,
    attrs hstore,
    CONSTRAINT invoices_pkey PRIMARY KEY (id),
    CONSTRAINT invoices_order_id_fkey FOREIGN KEY (order_id)
        REFERENCES payment.orders (order_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT invoices_payment_id_fkey FOREIGN KEY (payment_id)
        REFERENCES payment.payments (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

-- Index: invoices_attrs

-- DROP INDEX payment.invoices_attrs;

CREATE INDEX invoices_attrs
    ON payment.invoices USING gin
    (attrs)
    TABLESPACE pg_default;
-- Index: invoices_created_by

-- DROP INDEX payment.invoices_created_by;

CREATE INDEX invoices_created_by
    ON payment.invoices USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: invoices_invoice_number

-- DROP INDEX payment.invoices_invoice_number;

CREATE UNIQUE INDEX invoices_invoice_number
    ON payment.invoices USING btree
    (invoice_number ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: invoices_modified_by

-- DROP INDEX payment.invoices_modified_by;

CREATE INDEX invoices_modified_by
    ON payment.invoices USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: invoices_order_id

-- DROP INDEX payment.invoices_order_id;

CREATE INDEX invoices_order_id
    ON payment.invoices USING btree
    (order_id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: invoices_payment_id

-- DROP INDEX payment.invoices_payment_id;

CREATE INDEX invoices_payment_id
    ON payment.invoices USING btree
    (payment_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: payment.order_items

-- DROP TABLE payment.order_items;

CREATE TABLE IF NOT EXISTS payment.order_items
(
    id bigint NOT NULL DEFAULT nextval('payment.order_items_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    item character varying(100) COLLATE pg_catalog."default" NOT NULL,
    item_rate numeric(10,5) NOT NULL,
    applied_token_rate integer,
    quantity numeric(10,5) NOT NULL,
    total numeric(10,5) NOT NULL,
    order_id character varying(50) COLLATE pg_catalog."default" NOT NULL,
    attrs hstore,
    CONSTRAINT order_items_pkey PRIMARY KEY (id),
    CONSTRAINT order_items_applied_token_rate_fkey FOREIGN KEY (applied_token_rate)
        REFERENCES master.token_conversion_rates (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id)
        REFERENCES payment.orders (order_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: order_items_applied_token_rate

-- DROP INDEX payment.order_items_applied_token_rate;

CREATE INDEX order_items_applied_token_rate
    ON payment.order_items USING btree
    (applied_token_rate ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: order_items_attrs

-- DROP INDEX payment.order_items_attrs;

CREATE INDEX order_items_attrs
    ON payment.order_items USING gin
    (attrs)
    TABLESPACE pg_default;
-- Index: order_items_created_by

-- DROP INDEX payment.order_items_created_by;

CREATE INDEX order_items_created_by
    ON payment.order_items USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: order_items_modified_by

-- DROP INDEX payment.order_items_modified_by;

CREATE INDEX order_items_modified_by
    ON payment.order_items USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: order_items_order_id

-- DROP INDEX payment.order_items_order_id;

CREATE INDEX order_items_order_id
    ON payment.order_items USING btree
    (order_id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------



-- Table: payment.wallets

-- DROP TABLE payment.wallets;

CREATE TABLE IF NOT EXISTS payment.wallets
(
    id uuid NOT NULL,
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id uuid NOT NULL,
    account_id uuid NOT NULL,
    name character varying(255) COLLATE pg_catalog."default",
    balance numeric(10,5) NOT NULL,
    in_transit numeric(10,5),
    CONSTRAINT wallets_pkey PRIMARY KEY (id),
    CONSTRAINT wallets_account_id_fkey FOREIGN KEY (account_id)
        REFERENCES transactional.accounts (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT wallets_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES payment.wallets (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT check_balance_positive CHECK (balance >= 0::numeric)
)

TABLESPACE pg_default;


-- Index: wallets_account_id

-- DROP INDEX payment.wallets_account_id;

CREATE INDEX wallets_account_id
    ON payment.wallets USING btree
    (account_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: wallets_created_by

-- DROP INDEX payment.wallets_created_by;

CREATE INDEX wallets_created_by
    ON payment.wallets USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: wallets_modified_by

-- DROP INDEX payment.wallets_modified_by;

CREATE INDEX wallets_modified_by
    ON payment.wallets USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: wallets_record_id

-- DROP INDEX payment.wallets_record_id;

CREATE INDEX wallets_record_id
    ON payment.wallets USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: support.faqs

-- DROP TABLE support.faqs;

CREATE TABLE IF NOT EXISTS support.faqs
(
    id bigint NOT NULL DEFAULT nextval('support.faqs_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    content_type character varying(50) COLLATE pg_catalog."default" NOT NULL,
    content_text character varying COLLATE pg_catalog."default" NOT NULL,
    content_format character varying(50) COLLATE pg_catalog."default" NOT NULL,
    additional_text character varying(600) COLLATE pg_catalog."default",
    parent_id integer,
    rank integer NOT NULL,
    CONSTRAINT faqs_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;
-- Index: faqs_created_by

-- DROP INDEX support.faqs_created_by;

CREATE INDEX faqs_created_by
    ON support.faqs USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: faqs_modified_by

-- DROP INDEX support.faqs_modified_by;

CREATE INDEX faqs_modified_by
    ON support.faqs USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: support.support_queries

-- DROP TABLE support.support_queries;

CREATE TABLE IF NOT EXISTS support.support_queries
(
    id uuid NOT NULL,
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    status character varying(50) COLLATE pg_catalog."default" NOT NULL,
    query_text character varying(600) COLLATE pg_catalog."default" NOT NULL,
    customer_user uuid,
    customer_phone character varying(20) COLLATE pg_catalog."default" NOT NULL,
    customer_email character varying(50) COLLATE pg_catalog."default",
    customer_device_token character varying(255) COLLATE pg_catalog."default" NOT NULL,
    customer_device_os_version character varying(255) COLLATE pg_catalog."default" NOT NULL,
    customer_app_version character varying(50) COLLATE pg_catalog."default" NOT NULL,
    session_token character varying(5000) COLLATE pg_catalog."default",
    response_date date,
    response_by uuid,
    response_comment character varying(600) COLLATE pg_catalog."default",
    CONSTRAINT support_queries_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;
-- Index: support_queries_created_by

-- DROP INDEX support.support_queries_created_by;

CREATE INDEX support_queries_created_by
    ON support.support_queries USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: support_queries_modified_by

-- DROP INDEX support.support_queries_modified_by;

CREATE INDEX support_queries_modified_by
    ON support.support_queries USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: telemetry.energy_consumption

-- DROP TABLE telemetry.energy_consumption;

CREATE TABLE IF NOT EXISTS telemetry.energy_consumption
(
    id bigint NOT NULL DEFAULT nextval('telemetry.energy_consumption_id_seq'::regclass),
    active boolean,
    created_on timestamp without time zone,
    modified_on timestamp without time zone,
    created_by uuid,
    modified_by uuid,
    reading_date date NOT NULL,
    reading_time time without time zone NOT NULL,
    station_client_code character varying(50) COLLATE pg_catalog."default",
    grid_power double precision NOT NULL,
    solar_power double precision NOT NULL,
    diesel_generated_power double precision NOT NULL,
    total_power double precision NOT NULL,
    battery_charge double precision,
    battery_discharge double precision,
    reading_duration bigint,
    charger_code character varying(255) COLLATE pg_catalog."default",
    battery_soc real,
    CONSTRAINT energy_consumption_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;


-- Index: energy_consumption_created_by

-- DROP INDEX telemetry.energy_consumption_created_by;

CREATE INDEX energy_consumption_created_by
    ON telemetry.energy_consumption USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: energy_consumption_modified_by

-- DROP INDEX telemetry.energy_consumption_modified_by;

CREATE INDEX energy_consumption_modified_by
    ON telemetry.energy_consumption USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: telemetry.station_mapping

-- DROP TABLE telemetry.station_mapping;

CREATE TABLE IF NOT EXISTS telemetry.station_mapping
(
    id bigint NOT NULL DEFAULT nextval('telemetry.station_mapping_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid,
    modified_by uuid,
    record_id bigint NOT NULL,
    station_record_id uuid NOT NULL,
    station_client_code character varying(50) COLLATE pg_catalog."default",
    CONSTRAINT station_mapping_pkey PRIMARY KEY (id),
    CONSTRAINT station_mapping_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES telemetry.station_mapping (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT station_mapping_station_record_id_fkey FOREIGN KEY (station_record_id)
        REFERENCES transactional.stations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: station_mapping_created_by

-- DROP INDEX telemetry.station_mapping_created_by;

CREATE INDEX station_mapping_created_by
    ON telemetry.station_mapping USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_mapping_modified_by

-- DROP INDEX telemetry.station_mapping_modified_by;

CREATE INDEX station_mapping_modified_by
    ON telemetry.station_mapping USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_mapping_record_id

-- DROP INDEX telemetry.station_mapping_record_id;

CREATE INDEX station_mapping_record_id
    ON telemetry.station_mapping USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: station_mapping_station_record_id

-- DROP INDEX telemetry.station_mapping_station_record_id;

CREATE INDEX station_mapping_station_record_id
    ON telemetry.station_mapping USING btree
    (station_record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------



CREATE TABLE IF NOT EXISTS transactional.mobile_devices
(
    id bigint NOT NULL DEFAULT nextval('transactional.mobile_devices_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    device_token character varying(150) COLLATE pg_catalog."default" NOT NULL,
    os character varying(20) COLLATE pg_catalog."default",
    os_version character varying(20) COLLATE pg_catalog."default",
    brand character varying COLLATE pg_catalog."default",
    app_version character varying(10) COLLATE pg_catalog."default",
    fcm_token character varying COLLATE pg_catalog."default",
    type character varying(50) COLLATE pg_catalog."default" NOT NULL,
    status character varying(50) COLLATE pg_catalog."default" DEFAULT 'ACTIVE'::character varying,
    serial_id character varying COLLATE pg_catalog."default",
    product_id character varying COLLATE pg_catalog."default",
    model_id character varying COLLATE pg_catalog."default",
    asset_id character varying COLLATE pg_catalog."default",
    CONSTRAINT mobile_devices_pkey PRIMARY KEY (id),
    CONSTRAINT mobile_devices_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES transactional.mobile_devices (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: mobile_devices_created_by

-- DROP INDEX transactional.mobile_devices_created_by;

CREATE INDEX mobile_devices_created_by
    ON transactional.mobile_devices USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: mobile_devices_modified_by

-- DROP INDEX transactional.mobile_devices_modified_by;

CREATE INDEX mobile_devices_modified_by
    ON transactional.mobile_devices USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: mobile_devices_record_id

-- DROP INDEX transactional.mobile_devices_record_id;

CREATE INDEX mobile_devices_record_id
    ON transactional.mobile_devices USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Table: transactional.chargers

-- DROP TABLE transactional.chargers;

CREATE TABLE IF NOT EXISTS transactional.chargers
(
    id bigint NOT NULL DEFAULT nextval('transactional.chargers_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    type character varying(50) COLLATE pg_catalog."default" NOT NULL,
    station_record_id uuid NOT NULL,
    rank integer NOT NULL DEFAULT 1,
    name character varying(150) COLLATE pg_catalog."default",
    status character varying(50) COLLATE pg_catalog."default" DEFAULT 'ACTIVE'::character varying,
    serial_id character varying COLLATE pg_catalog."default",
    product_id character varying COLLATE pg_catalog."default",
    model_id character varying COLLATE pg_catalog."default",
    asset_id character varying COLLATE pg_catalog."default",
    CONSTRAINT chargers_pkey PRIMARY KEY (id),
    CONSTRAINT chargers_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES transactional.chargers (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT chargers_station_record_id_fkey FOREIGN KEY (station_record_id)
        REFERENCES transactional.stations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: chargers_created_by

-- DROP INDEX transactional.chargers_created_by;

CREATE INDEX chargers_created_by
    ON transactional.chargers USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: chargers_modified_by

-- DROP INDEX transactional.chargers_modified_by;

CREATE INDEX chargers_modified_by
    ON transactional.chargers USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: chargers_record_id

-- DROP INDEX transactional.chargers_record_id;

CREATE INDEX chargers_record_id
    ON transactional.chargers USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: chargers_station_record_id

-- DROP INDEX transactional.chargers_station_record_id;

CREATE INDEX chargers_station_record_id
    ON transactional.chargers USING btree
    (station_record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------


-- Table: transactional.mobile_devices

-- DROP TABLE transactional.mobile_devices;


-- Table: transactional.nozzles

-- DROP TABLE transactional.nozzles;

CREATE TABLE IF NOT EXISTS transactional.nozzles
(
    id bigint NOT NULL DEFAULT nextval('transactional.nozzles_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id bigint NOT NULL,
    charger_record_id bigint NOT NULL,
    charging_connector_record_id bigint NOT NULL,
    rated_power_record_id bigint NOT NULL,
    asset_id character varying(100) COLLATE pg_catalog."default",
    serial_id character varying COLLATE pg_catalog."default",
    CONSTRAINT nozzles_pkey PRIMARY KEY (id),
    CONSTRAINT nozzles_charger_record_id_fkey FOREIGN KEY (charger_record_id)
        REFERENCES transactional.chargers (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT nozzles_charging_connector_record_id_fkey FOREIGN KEY (charging_connector_record_id)
        REFERENCES master.charging_connectors (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT nozzles_rated_power_record_id_fkey FOREIGN KEY (rated_power_record_id)
        REFERENCES master.rated_powers (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT nozzles_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES transactional.nozzles (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


-- Index: nozzles_charger_record_id

-- DROP INDEX transactional.nozzles_charger_record_id;

CREATE INDEX nozzles_charger_record_id
    ON transactional.nozzles USING btree
    (charger_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: nozzles_charging_connector_record_id

-- DROP INDEX transactional.nozzles_charging_connector_record_id;

CREATE INDEX nozzles_charging_connector_record_id
    ON transactional.nozzles USING btree
    (charging_connector_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: nozzles_created_by

-- DROP INDEX transactional.nozzles_created_by;

CREATE INDEX nozzles_created_by
    ON transactional.nozzles USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: nozzles_modified_by

-- DROP INDEX transactional.nozzles_modified_by;

CREATE INDEX nozzles_modified_by
    ON transactional.nozzles USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: nozzles_rated_power_record_id

-- DROP INDEX transactional.nozzles_rated_power_record_id;

CREATE INDEX nozzles_rated_power_record_id
    ON transactional.nozzles USING btree
    (rated_power_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: nozzles_record_id

-- DROP INDEX transactional.nozzles_record_id;

CREATE INDEX nozzles_record_id
    ON transactional.nozzles USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

CREATE EXTENSION btree_gist;

-- Table: transactional.slots

-- DROP TABLE transactional.slots;

CREATE TABLE IF NOT EXISTS transactional.slots
(
    id integer NOT NULL DEFAULT nextval('transactional.slots_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    nozzle_record_id bigint NOT NULL,
    date date NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    slot_number character varying(15) COLLATE pg_catalog."default",
    status character varying(15) COLLATE pg_catalog."default",
    CONSTRAINT slots_pkey PRIMARY KEY (id),
    CONSTRAINT slots_nozzle_record_id_fkey FOREIGN KEY (nozzle_record_id)
        REFERENCES transactional.nozzles (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT slots_unique EXCLUDE USING gist (
        tsrange(date + start_time, date + end_time) WITH &&,
        date WITH =,
        nozzle_record_id WITH =,
        status WITH =)

)

TABLESPACE pg_default;

-- Index: slots_created_by

-- DROP INDEX transactional.slots_created_by;

CREATE INDEX slots_created_by
    ON transactional.slots USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: slots_modified_by

-- DROP INDEX transactional.slots_modified_by;

CREATE INDEX slots_modified_by
    ON transactional.slots USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: slots_nozzle_record_id

-- DROP INDEX transactional.slots_nozzle_record_id;

CREATE INDEX slots_nozzle_record_id
    ON transactional.slots USING btree
    (nozzle_record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-- Table: auth.authenticated_sessions

-- DROP TABLE auth.authenticated_sessions;

CREATE TABLE IF NOT EXISTS auth.authenticated_sessions
(
    id uuid NOT NULL,
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    validity_start timestamp without time zone NOT NULL,
    validity_end timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    record_id uuid NOT NULL,
    user_record_id uuid NOT NULL,
    device_record_id bigint NOT NULL,
    group_id bigint NOT NULL,
    auth_attempt_id uuid NOT NULL,
    CONSTRAINT authenticated_sessions_pkey PRIMARY KEY (id),
    CONSTRAINT authenticated_sessions_auth_attempt_id_fkey FOREIGN KEY (auth_attempt_id)
        REFERENCES auth.auth_attempts (txn_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT authenticated_sessions_device_record_id_fkey FOREIGN KEY (device_record_id)
        REFERENCES transactional.mobile_devices (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT authenticated_sessions_group_id_fkey FOREIGN KEY (group_id)
        REFERENCES auth.groups (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT authenticated_sessions_record_id_fkey FOREIGN KEY (record_id)
        REFERENCES auth.authenticated_sessions (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT authenticated_sessions_user_record_id_fkey FOREIGN KEY (user_record_id)
        REFERENCES transactional.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

-- Index: authenticated_sessions_auth_attempt_id

-- DROP INDEX auth.authenticated_sessions_auth_attempt_id;

CREATE INDEX authenticated_sessions_auth_attempt_id
    ON auth.authenticated_sessions USING btree
    (auth_attempt_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: authenticated_sessions_created_by

-- DROP INDEX auth.authenticated_sessions_created_by;

CREATE INDEX authenticated_sessions_created_by
    ON auth.authenticated_sessions USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: authenticated_sessions_device_record_id

-- DROP INDEX auth.authenticated_sessions_device_record_id;

CREATE INDEX authenticated_sessions_device_record_id
    ON auth.authenticated_sessions USING btree
    (device_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: authenticated_sessions_group_id

-- DROP INDEX auth.authenticated_sessions_group_id;

CREATE INDEX authenticated_sessions_group_id
    ON auth.authenticated_sessions USING btree
    (group_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: authenticated_sessions_modified_by

-- DROP INDEX auth.authenticated_sessions_modified_by;

CREATE INDEX authenticated_sessions_modified_by
    ON auth.authenticated_sessions USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: authenticated_sessions_record_id

-- DROP INDEX auth.authenticated_sessions_record_id;

CREATE INDEX authenticated_sessions_record_id
    ON auth.authenticated_sessions USING btree
    (record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: authenticated_sessions_user_record_id

-- DROP INDEX auth.authenticated_sessions_user_record_id;

CREATE INDEX authenticated_sessions_user_record_id
    ON auth.authenticated_sessions USING btree
    (user_record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: engagement.notifications

-- DROP TABLE engagement.notifications;

CREATE TABLE IF NOT EXISTS engagement.notifications
(
    id bigint NOT NULL DEFAULT nextval('engagement.notifications_id_seq'::regclass),
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    event character varying(50) COLLATE pg_catalog."default" NOT NULL,
    event_time timestamp without time zone,
    data jsonb,
    user_record_id uuid NOT NULL,
    mobile_record_id bigint,
    linked_resource hstore,
    generated_on timestamp without time zone,
    sent_on timestamp without time zone,
    received_on timestamp without time zone,
    displayed_on timestamp without time zone,
    engaged_on timestamp without time zone,
    cancelled_on timestamp without time zone,
    engaged_action character varying(255) COLLATE pg_catalog."default",
    engaged_source character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT notifications_pkey PRIMARY KEY (id),
    CONSTRAINT notifications_mobile_record_id_fkey FOREIGN KEY (mobile_record_id)
        REFERENCES transactional.mobile_devices (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT notifications_user_record_id_fkey FOREIGN KEY (user_record_id)
        REFERENCES transactional.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;
-- Index: notifications_created_by

-- DROP INDEX engagement.notifications_created_by;

CREATE INDEX notifications_created_by
    ON engagement.notifications USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: notifications_data

-- DROP INDEX engagement.notifications_data;

CREATE INDEX notifications_data
    ON engagement.notifications USING gin
    (data)
    TABLESPACE pg_default;
-- Index: notifications_linked_resource

-- DROP INDEX engagement.notifications_linked_resource;

CREATE INDEX notifications_linked_resource
    ON engagement.notifications USING gin
    (linked_resource)
    TABLESPACE pg_default;
-- Index: notifications_mobile_record_id

-- DROP INDEX engagement.notifications_mobile_record_id;

CREATE INDEX notifications_mobile_record_id
    ON engagement.notifications USING btree
    (mobile_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: notifications_modified_by

-- DROP INDEX engagement.notifications_modified_by;

CREATE INDEX notifications_modified_by
    ON engagement.notifications USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: notifications_user_record_id

-- DROP INDEX engagement.notifications_user_record_id;

CREATE INDEX notifications_user_record_id
    ON engagement.notifications USING btree
    (user_record_id ASC NULLS LAST)
    TABLESPACE pg_default;

--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
-- Table: transactional.bookings

-- DROP TABLE transactional.bookings;

CREATE TABLE IF NOT EXISTS transactional.bookings
(
    active boolean NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    modified_by uuid NOT NULL,
    consumer_user_record_id uuid NOT NULL,
    vehicle_record_id uuid NOT NULL,
    station_record_id uuid NOT NULL,
    slot_id integer NOT NULL,
    booking_date date NOT NULL,
    service_date date NOT NULL,
    booking_status character varying(50) COLLATE pg_catalog."default" NOT NULL,
    otp character varying(10) COLLATE pg_catalog."default" NOT NULL,
    qr_code_data character varying(255) COLLATE pg_catalog."default" NOT NULL,
    total_charges numeric(10,5) NOT NULL,
    cancellation_charges numeric(10,5),
    deferred_txn_invoice_id bigint,
    final_txn_invoice_id bigint,
    booking_id uuid NOT NULL,
    charging_type character varying(50) COLLATE pg_catalog."default",
    CONSTRAINT bookings_pkey PRIMARY KEY (booking_id),
    CONSTRAINT bookings_consumer_user_record_id_fkey FOREIGN KEY (consumer_user_record_id)
        REFERENCES transactional.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT bookings_deferred_txn_invoice_id_fkey FOREIGN KEY (deferred_txn_invoice_id)
        REFERENCES payment.invoices (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT bookings_final_txn_invoice_id_fkey FOREIGN KEY (final_txn_invoice_id)
        REFERENCES payment.invoices (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT bookings_slot_id_fkey FOREIGN KEY (slot_id)
        REFERENCES transactional.slots (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT bookings_station_record_id_fkey FOREIGN KEY (station_record_id)
        REFERENCES transactional.stations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT bookings_vehicle_record_id_fkey FOREIGN KEY (vehicle_record_id)
        REFERENCES transactional.vehicles (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

-- Index: bookings_consumer_user_record_id

-- DROP INDEX transactional.bookings_consumer_user_record_id;

CREATE INDEX bookings_consumer_user_record_id
    ON transactional.bookings USING btree
    (consumer_user_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: bookings_created_by

-- DROP INDEX transactional.bookings_created_by;

CREATE INDEX bookings_created_by
    ON transactional.bookings USING btree
    (created_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: bookings_deferred_txn_invoice_id

-- DROP INDEX transactional.bookings_deferred_txn_invoice_id;

CREATE INDEX bookings_deferred_txn_invoice_id
    ON transactional.bookings USING btree
    (deferred_txn_invoice_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: bookings_final_txn_invoice_id

-- DROP INDEX transactional.bookings_final_txn_invoice_id;

CREATE INDEX bookings_final_txn_invoice_id
    ON transactional.bookings USING btree
    (final_txn_invoice_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: bookings_modified_by

-- DROP INDEX transactional.bookings_modified_by;

CREATE INDEX bookings_modified_by
    ON transactional.bookings USING btree
    (modified_by ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: bookings_slot_id

-- DROP INDEX transactional.bookings_slot_id;

CREATE INDEX bookings_slot_id
    ON transactional.bookings USING btree
    (slot_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: bookings_station_record_id

-- DROP INDEX transactional.bookings_station_record_id;

CREATE INDEX bookings_station_record_id
    ON transactional.bookings USING btree
    (station_record_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: bookings_vehicle_record_id

-- DROP INDEX transactional.bookings_vehicle_record_id;

CREATE INDEX bookings_vehicle_record_id
    ON transactional.bookings USING btree
    (vehicle_record_id ASC NULLS LAST)
    TABLESPACE pg_default;

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
