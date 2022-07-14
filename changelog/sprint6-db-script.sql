--new columns to charger table
ALTER TABLE CHARGERS
ADD COLUMN "rank" INTEGER NOT NULL default 1,
ADD COLUMN "name" VARCHAR(150);

--new columns to equipments, chargers, mobile_devices
ALTER TABLE EQUIPMENTS
ADD status VARCHAR(50) DEFAULT 'ACTIVE',
ADD serial_id VARCHAR,
ADD product_id VARCHAR,
ADD model_id VARCHAR,
ADD asset_id VARCHAR;

ALTER TABLE CHARGERS
ADD status VARCHAR(50) DEFAULT 'ACTIVE',
ADD serial_id VARCHAR,
ADD product_id VARCHAR,
ADD model_id VARCHAR,
ADD asset_id VARCHAR;

ALTER TABLE MOBILE_DEVICES
ADD status VARCHAR(50) DEFAULT 'ACTIVE',
ADD serial_id VARCHAR,
ADD product_id VARCHAR,
ADD model_id VARCHAR,
ADD asset_id VARCHAR;

--changes to mobile_devices columns
ALTER TABLE MOBILE_DEVICES
DROP model,
ALTER brand TYPE VARCHAR,
ALTER fcm_token TYPE VARCHAR;

--changes to nozzles columns
ALTER TABLE nozzles
ADD serial_id VARCHAR

--added new table
CREATE TABLE IF NOT EXISTS "equipment_type_master" ("id" BIGSERIAL NOT NULL PRIMARY KEY, "active" BOOLEAN NOT NULL, "created_on" TIMESTAMP NOT NULL, "modified_on" TIMESTAMP NOT NULL, "validity_start" TIMESTAMP NOT NULL, "validity_end" TIMESTAMP NOT NULL, "created_by" UUID NOT NULL, "modified_by" UUID NOT NULL, "record_id" BIGINT NOT NULL, "name" VARCHAR(100) NOT NULL, "type" VARCHAR(50) NOT NULL, "icon_image" BYTEA NOT NULL, "rank" INTEGER NOT NULL, "description" VARCHAR(255), FOREIGN KEY ("record_id") REFERENCES "equipment_type_master" ("id"));
CREATE INDEX IF NOT EXISTS "equipment_type_master_created_by" ON "equipment_type_master" ("created_by");
CREATE INDEX IF NOT EXISTS "equipment_type_master_modified_by" ON "equipment_type_master" ("modified_by");
CREATE INDEX IF NOT EXISTS "equipment_type_master_record_id" ON "equipment_type_master" ("record_id");

--insert ev charger
INSERT INTO public.equipment_type_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id,
	name, type, icon_image, rank, description)
	VALUES (
		default, true, now(), now(), now(), 'infinity'::timestamp,
		'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
		currval('equipment_type_masters_id_seq'::regclass),
		'EV Charger', 'EV_CHARGER',
		decode('89504e470d0a1a0a0000000d494844520000001b0000001808060000000b4086fb000000097048597300000b1300000b1301009a9c18000000017352474200aece1ce90000000467414d410000b18f0bfc6105000003c1494441547801ad564d4edb50109e99e792ee9a23b8db4a6d63682b754538017082c2a21264133801e104c0821f8945e004c00908ab4aa560e704a43760831412fca633cf71b08d5381da91c0f69bf7e6e79b79df04a14456c2cb3a18f229061f5e280c70cb60a383e073a7a8c3bc93d03706dacc5c877f15c4a3a918d6b783e0365df2b27a223e61966c2c6f5a181c1d045f7bf042590bc3ea3dd82524d81a18d6a5e5279b1add70a3d1bde64678b504ff41c44eab68cfc1a8f0495637c078b4570b7291ac86bf1690cc16a38d2a312d6761496197425563db5f2c22b11a5d9f23426dcae25b3d47ba480636f469b9bf598c90d034a5ec3e322ef4e1a196d3095c5a5f06ae114dad15cf32c76acfc19aec4f56ebd6c259598d98edc5e855327ac8e92dd84ee6232a9ed58e941ee880c179e7ac11fed4687d023e8512d90b665ad6c6730a4531183566657d681f02d97754761e99bbc850d7c6f118c8d7c20d812298206577e65117f4e02f22107710b079270979f2e2ea701804ce994630f0a0895af4b8bf53cc6645ba8b906641e02d66a36440e87d0303d1defb602771662294ffafc0d6a818c900a5bb2cb7a4f04b449573759e7344d8166c16a473da8e69c63aed6873ee7496b71bddab56d136b12b7c92915bd1cdc03b528b75f9f287157e936e1614d4784f74813b0c54cfd872ef52df45294b8488b3c99e617504e7ad3823e74c31758bda3d82b1dcbb2d35bcfb6efaf7a33d56a8933ba986856552cd6b006db05bc9ee4412a80932178913f2c7cee4d9d10f0fac8bacc2b8682d2f0b14c7d6decf652287fd60667ba4dbd40ecdd6532fadcb58cec9dff2dec79956060dd7648e4184aa6e18b9b7ff613a673ca9c5651d0d562bb1e964d9231585bf6fec02c4834ed93d15caba1116e9ed8aeda441ac3dd6bbb012fef0f38eb421cc39329d0c88c36cb324fad0d775626c4b33dd641b263d2f0f9f63c916460c3205b4ad78a3a9b4b39b0d61538b2df0285ffa6574a5eb0aa99e776d9fd5132a0df6d22be29c293c2c75d0ec56c3ab31c731624f8aed1b8266b292a72b4e1a068cf1d46855a8adfb085fa86b6e5c3d0637122dbe7622126ea57058197e2c9c29467a12cc7ab126fbc1a75367cc72559f6a63e448c9bba557287bf17393dab187d4c0e12cc6d3c32f912423210580e3fd8fd34b591d1637bb498b7c221d54d7d16ee3fee67326b6a2a1702623e7a9a35267e30865d20a2569c17d717a0ab13d1b421c1d065fc61c7a0743df03532743f3a3df2daef6931099e82c8956f84e3b2e753a41b463c5c9997675d95dccec7b9e7c97b9e7b971944c09f793cd08af4eb8cc65f207a6bc1945aae197010000000049454e44ae426082', 'hex'),
		1, 'ev charger');

--insert battery charger
INSERT INTO public.equipment_type_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id,
	name, type, icon_image, rank, description)
	VALUES (
		default, true, now(), now(), now(), now(),
		'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
		currval('equipment_type_masters_id_seq'::regclass),
		'Battery Charger', 'BATTERY_CHARGER',
		decode('89504e470d0a1a0a0000000d49484452000000280000002208060000002d659b0b000000097048597300000b1300000b1301009a9c18000000017352474200aece1ce90000000467414d410000b18f0bfc6105000002cf494441547801ed57c1521a4110ed9e11f526fec17af5a0ac5652e549fc02cd1f989b9083e60bd02f801c44aa72087c41922f104fb94406fc01d73f20375cd9eef440ad515c616525e5615fd5d64c4ff5cc744fbf9ee905489122c5dbc59131d903f3cb191db35f28639c457ad0cffd1be97b3577cb8ba35b73df3561ccbabe6223dd2e1337cedccdca81318e527c3e50203ea9ba9bf53998005f435993b69b76adcca81d59dcadb86ef789ae6ca8597ba15cb86a95ced63676a2d6ed016435821704c189d6ba244315f9f2b24193182e14b063f5220dfc7465ce9961a0002c8af3e09cae6edc58b1d831d7be02236dc44c86d3dcd0a0c169305f5b7d2ba3189309e0439463e3f0c4c082f9bd470123c3edbde7b5d5ad9bb04fd4db8118a8b9ae27fc5a0965858b651f684fba7578019e70503cdf5708dbd59cfb115e1105d3aa2370d3f2eac05cee6ba50e59c28880dea0456c330fc37a6f1ca2379183b380189527a20683ff639c9e520bd751063601b92c3c74e01521a79323f28f4319159610160f27ccea465e33c374074977fa09042f227524c49879c2e58709f230e451536c7255d7dd95c8105b82db2cc50c96c3ec4d8262a7557a69f68650f0c6317592dcd380a11927e38be6b232e868b54441ef042682b3890c147ee685ea8e90bf13475bb87664dba1630bdf09f90b32968a6db33daa8b0a645d6ad8fed421565aed0e3a1a7765936f71e7597e33414705f6d2c71de27e0391737273ecdb8f145df8c1dde7eafad0a1a94f10891d96e74b9e9cbc083142166dac345ec15c36e4dab1efbd575b7b9cd5539fa0bcb92e5160b9e789b7c79000b6929170373123ce8e205116cb8b90b56511cc10899e3a86bbf6d933b5e16b21d109d6666c9cc55803fddbfe3224c4c3f27d1a3c1f62a936326a4e0ad31624812f4410323ce2a9bcc11e6bb51ecaf66e940a343b7f8b7f46e74ffc2799156c4d68cb2eb90397c4879b3b08ea5fddf76d489122458aff8bbfc21a4332a84884e00000000049454e44ae426082', 'hex'),
		2, 'battery charger --todo correct validity_end once available on app');

--insert battery
INSERT INTO public.equipment_type_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id,
	name, type, icon_image, rank, description)
	VALUES (
		default, true, now(), now(), now(), now(),
		'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
		currval('equipment_type_masters_id_seq'::regclass),
		'Battery', 'BATTERY',
		decode('89504e470d0a1a0a0000000d494844520000001a000000150806000000581cfe1b000000097048597300000b1300000b1301009a9c18000000017352474200aece1ce90000000467414d410000b18f0bfc6105000001a6494441547801d596cd4d03311085df7817b82e1da482b056c48113500150015c90f8b9241d4005c081901ba102a082842b1298d000db017b2451ec611cb2518436105012c177588f47b37a96673c36e11387cfe68499cb43aec4b9f67a4daf24c861cf9882526cc48c321f3bae5ce8d2e9701cf940046e2d7328a6cb79478ba75aa77ebe6f1eeb14103bb8bb3c210236c8a255d5a5233f3f30f73154d870c4954190ed3443594d034e3587fead6722bdd5819be4685541ad229f94619fb2c93ce6920ee34616dc8f7711070bdb38683d32a688df31d178519811a1ffeccabe06b029a642b700046908c7c773923cd18c301d12a9c233f296ece38ea47d136897314102b5706d9dadd4f47233cc9c8ae8b51ae79f95df72f86406e99859314c44a86c4cb4f7fcb083690bbd49fbf11de5ab9830cfe9fb9d0cf1b0efbca8d747c436a47d44dcb7654cab45bd359690b5dd5b299916c6c0c25d49e946048a3f6cce3d8fb942be1c3126b562a9eedb0c293ef1f6a8b81013a0a675825e231fcdff2aef3f25d4cb11f9ce4d2afeeed0fd14791214d0bfed0609dc370f6522b58409c2ec5ad9dbe11dfee1a88dc2ee30270000000049454e44ae426082', 'hex'),
		3, 'battery --todo correct validity_end once available on app');

--insert nozzle count app config
INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id, key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('app_configs_id_seq'::regclass),
			'max_nozzle_guns_in_one_charger', '4');

INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id,
	key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('app_configs_id_seq'::regclass),
			'max_chargers_in_one_station', 10);

--permission correction
insert into role_permission_rel(role_id, permission_id)
values(3, (select id from permissions where name = 'can-retrieve-search-vehicle_masters'))


--privacy policy app configs
ALTER TABLE public.app_configs
    ALTER COLUMN value TYPE character varying(255) COLLATE pg_catalog."default";

INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('app_configs_id_seq'::regclass),
			'doc.terms_login_en', '{"title":"Terms of Use","showTitle":true,"href":"/static-contents/login-terms-en.html"}');


INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('app_configs_id_seq'::regclass),
			'doc.privacy_policy_login_en', '{"title":"Privacy Policy","showTitle":true,"href":"/static-contents/login-privacy-policy-en.html"}');


INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('app_configs_id_seq'::regclass),
			'doc.terms_transaction_en', '{"title":"Terms of Use","showTitle":true,"href":"/static-contents/transaction-terms-and-conditions-en.html"}');


INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('app_configs_id_seq'::regclass),
			'doc.terms_app_en', '{"title":"Terms of Use","showTitle":true,"href":"/static-contents/app-terms-en.html"}');


INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('app_configs_id_seq'::regclass),
			'doc.guide_account_verification_evo_en', '{"title":"Verification Guide","showTitle":true,"href":"/static-contents/guide-account-verification-en.html"}');

INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('app_configs_id_seq'::regclass),
			'doc.guide_account_verification_evso_en', '{"title":"Verification Guide","showTitle":true,"href":"/static-contents/guide-account-verification-en.html"}');


--encashment app config
INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('app_configs_id_seq'::regclass),
			'message.successful_token_encashment', '{$amount.value.inr} ₹ will be credited to your account within 4-5 working days.');

ALTER TABLE public.nozzles
    ADD COLUMN serial_id character varying COLLATE pg_catalog."default";


-- Column: public.service_rate_table.covered_rated_powers

-- ALTER TABLE public.service_rate_table DROP COLUMN covered_rated_powers;

ALTER TABLE public.service_rate_table ADD COLUMN covered_rated_powers integer[];


-- Column: public.service_rate_table.days_of_week

-- ALTER TABLE public.service_rate_table DROP COLUMN days_of_week;

ALTER TABLE public.service_rate_table ADD COLUMN days_of_week bigint NOT NULL DEFAULT 127;


-- Column: public.service_rate_table.segments_of_day

-- ALTER TABLE public.service_rate_table DROP COLUMN segments_of_day;

ALTER TABLE public.service_rate_table ADD COLUMN segments_of_day integer[];


-- Column: public.service_rate_table.service_rate_id

-- ALTER TABLE public.service_rate_table DROP COLUMN service_rate_id;

ALTER TABLE public.service_rate_table ADD COLUMN service_rate_id bigint;


-- drop Column: public.service_rates.consumption_rate_record_id

ALTER TABLE public.service_rates DROP COLUMN consumption_rate_record_id;


-- drop Column: public.service_rates.day_segment_rates

ALTER TABLE public.service_rates DROP COLUMN day_segment_rates;

-------------  Sprint 6 Changelog queries  ---------------

-- add type column to accounts
ALTER TABLE accounts
ADD COLUMN type VARCHAR(50);

-- add type column to users
ALTER TABLE users
ADD COLUMN type VARCHAR(50);

-- add type column to stations
ALTER TABLE stations
ADD COLUMN type VARCHAR(50);

-- update type column in accounts
UPDATE accounts
SET type = 'STATION'
FROM stations
WHERE stations.record_id = accounts.id;

UPDATE accounts
SET type = 'USER'
WHERE type IS NULL;

-- update type column in users
UPDATE users
SET type = 'USER';

-- update type column in stations
UPDATE stations
SET type = 'STATION';

-----------------------------------------------------------------------------

INSERT INTO public.notifications(
	id, active, created_on, modified_on,
	created_by, modified_by,
	event, event_time, data,
	user_record_id, mobile_record_id,
	linked_resource,
	generated_on, sent_on, received_on,
	displayed_on, engaged_on, cancelled_on,
	engaged_action, engaged_source)
	VALUES (default, 'TRUE', '2021-07-19 10:22:32.854254', '2021-07-19 10:22:32.854254',
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'TXN_TRANSFER_TOKEN', '2021-07-19 10:22:32.854254', '{"id": 1,"event": "USER_LOGIN","eventTime": "2019-08-24T14:15:22Z","title": "Hygge EV Activity","message": "log into Hygge EV app"}',
			'b74b24fc-4639-46df-b67a-7572fcd95911', 126,
			'"resource_key"=>"Users", "resource_id"=>"b74b24fc-4639-46df-b67a-7572fcd95911"',
			'2021-07-19 10:22:32.854254', '2021-07-19 10:22:32.854254', '2021-07-19 10:22:32.854254',
			'2021-07-19 10:22:32.854254', '2021-07-19 10:22:32.854254', '2021-07-19 10:22:32.854254',
			'CLICK', 'Payments');

INSERT INTO public.notifications(
	id, active, created_on, modified_on,
	created_by, modified_by,
	event, event_time, data,
	user_record_id, mobile_record_id,
	linked_resource,
	generated_on, sent_on, received_on,
	displayed_on, engaged_on, cancelled_on,
	engaged_action, engaged_source)
	VALUES (default, 'TRUE', '2021-07-19 10:22:32.854254', '2021-07-19 10:22:32.854254',
			'09e06548-7bfe-4419-b4d0-3b350ee0e5af', '09e06548-7bfe-4419-b4d0-3b350ee0e5af',
			'TXN_TRANSFER_TOKEN', '2021-07-19 10:22:32.854254', '{"id": 1,"event": "USER_LOGIN","eventTime": "2019-08-24T14:15:22Z","title": "Hygge EV Activity","message": "log into Hygge EV app", "actions":[{"action": "CLICK", "actionDeepLink": "https://ev.hygge.energy/app/myev?source=notification&action=CLICK&id=vehicle-uuid"}]}',
			'09e06548-7bfe-4419-b4d0-3b350ee0e5af', 126,
			'"resource_key"=>"Users", "resource_id"=>"09e06548-7bfe-4419-b4d0-3b350ee0e5af"',
			'2021-07-19 10:22:32.854254', '2021-07-19 10:22:32.854254', '2021-07-19 10:22:32.854254',
			'2021-07-19 10:22:32.854254', '2021-07-19 10:22:32.854254', '2021-07-19 10:22:32.854254',
			'CLICK', 'Payments');



	INSERT INTO public.permissions(
	id, name, description, resource_name,
	can_retrieve, can_search, can_create, can_update, can_delete)
	VALUES (default, 'can-retrieve-search-create-update-delete-notifications' , NULL, 'notifications',
			true, true, true, true, true);

	INSERT INTO public.role_permission_rel(
	role_id, permission_id)
	VALUES (1, 18);

INSERT INTO public.role_permission_rel(
	role_id, permission_id)
	VALUES (2, 18);

INSERT INTO public.role_permission_rel(
	role_id, permission_id)
	VALUES (3, 18);

INSERT INTO public.role_permission_rel(
	role_id, permission_id)
	VALUES (4, 18);

INSERT INTO public.role_permission_rel(
	role_id, permission_id)
	VALUES (5, 18);

INSERT INTO public.role_permission_rel(
	role_id, permission_id)
	VALUES (6, 18);

INSERT INTO public.role_permission_rel(
	role_id, permission_id)
	VALUES (7, 18);

INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id, key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			currval('app_configs_id_seq'::regclass),
			'NOTIFICATION_BELL_ICON', '[TXN_TRANSFER_TOKEN,TXN_TRANSFER_TOKEN_FAILED,BOOKING_CONFIRMATION,BOOKING_CANCELLATION,BOOKING_REJECTION,USER_VERIFICATION,VEHICLE_ADDITION,VEHICLE_VERIFICATION,USER_LOGIN,TXN_ADDITION_TOKEN]');

INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id, key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			currval('app_configs_id_seq'::regclass),
			'NOTIFICATION_BAR', '[BOOKING_REMINDER_FIRST,BOOKING_REMINDER_SECOND,USER_VERIFICATION,VEHICLE_VERIFICATION,USER_LOGIN]');

INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id, key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			currval('app_configs_id_seq'::regclass),
			'NOTIFICATION_ALL', '[TXN_TRANSFER_TOKEN,TXN_TRANSFER_TOKEN_FAILED,BOOKING_CONFIRMATION,BOOKING_CANCELLATION,BOOKING_REJECTION,USER_VERIFICATION,VEHICLE_ADDITION,VEHICLE_VERIFICATION,BOOKING_REMINDER_FIRST,BOOKING_REMINDER_SECOND,USER_LOGIN,TXN_ADDITION_TOKEN]');

-------------------------------------------------------- demo dev data for android testing --------------------------------------------------------

INSERT INTO public.notifications(
	id, active, created_on, modified_on,
	created_by, modified_by,
	event, event_time, data,
	user_record_id, mobile_record_id,
	linked_resource,
	generated_on, sent_on, received_on,
	displayed_on, engaged_on, cancelled_on,
	engaged_action, engaged_source)
	VALUES (default, 'TRUE', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'TXN_TRANSFER_TOKEN', '2021-07-21 21:22:32.854254', '{"id": 5,"event": "TXN_TRANSFER_TOKEN","eventTime": "2021-06-17 12:44:37.226485Z","title": "Token transaction","message": "Token has been transfered successfully"}',
			'871964bc-b8f3-43ba-9da0-4dd8e4185297', 94,
			'"resource_key"=>"Payments", "resource_id"=>"ee4f3d68-6a71-4672-bf80-6208748dc533"',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'CLICK', 'Payments');

INSERT INTO public.notifications(
	id, active, created_on, modified_on,
	created_by, modified_by,
	event, event_time, data,
	user_record_id, mobile_record_id,
	linked_resource,
	generated_on, sent_on, received_on,
	displayed_on, engaged_on, cancelled_on,
	engaged_action, engaged_source)
	VALUES (default, 'TRUE', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'BOOKING_CONFIRMATION', '2021-07-21 21:22:32.854254', '{"id": 6,"event": "BOOKING_CONFIRMATION","eventTime": "2021-06-17 12:44:37.226485Z","title": "Booking Confirmation","message": "Your booking has been confirmed"}',
			'871964bc-b8f3-43ba-9da0-4dd8e4185297', 94,
			'"resource_key"=>"Bookings", "resource_id"=>"ee4f3d68-6a71-4672-bf80-6208748dc533"',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'CLICK', 'Bookings');

INSERT INTO public.notifications(
	id, active, created_on, modified_on,
	created_by, modified_by,
	event, event_time, data,
	user_record_id, mobile_record_id,
	linked_resource,
	generated_on, sent_on, received_on,
	displayed_on, engaged_on, cancelled_on,
	engaged_action, engaged_source)
	VALUES (default, 'TRUE', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'BOOKING_CANCELLATION', '2021-07-21 21:22:32.854254', '{"id": 7,"event": "BOOKING_CANCELLATION","eventTime": "2021-06-17 15:23:37.226485Z","title": "Booking Cancellation","message":"our booking has been cancelled successfully"}',
			'871964bc-b8f3-43ba-9da0-4dd8e4185297', 94,
			'"resource_key"=>"Booking", "resource_id"=>"ee4f3d68-6a71-4672-bf80-6208748dc533"',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'CLICK', 'Bookings');

INSERT INTO public.notifications(
	id, active, created_on, modified_on,
	created_by, modified_by,
	event, event_time, data,
	user_record_id, mobile_record_id,
	linked_resource,
	generated_on, sent_on, received_on,
	displayed_on, engaged_on, cancelled_on,
	engaged_action, engaged_source)
	VALUES (default, 'TRUE', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'TXN_TRANSFER_TOKEN', '2021-07-21 21:22:32.854254', '{"id": 8,"event": "TXN_TRANSFER_TOKEN","eventTime": "2021-06-18 12:44:37.226485Z","title": "Token transaction","message": "Token has been transfered successfully"}',
			'871964bc-b8f3-43ba-9da0-4dd8e4185297', 94,
			'"resource_key"=>"Payments", "resource_id"=>"ee4f3d68-6a71-4672-bf80-6208748dc533"',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'CLICK', 'Payments');

INSERT INTO public.notifications(
	id, active, created_on, modified_on,
	created_by, modified_by,
	event, event_time, data,
	user_record_id, mobile_record_id,
	linked_resource,
	generated_on, sent_on, received_on,
	displayed_on, engaged_on, cancelled_on,
	engaged_action, engaged_source)
	VALUES (default, 'TRUE', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'TXN_TRANSFER_TOKEN', '2021-07-21 21:22:32.854254', '{"id": 9,"event": "TXN_TRANSFER_TOKEN","eventTime": "2021-06-17 12:44:37.226485Z","title": "Token transaction","message": "Token has been transfered successfully"}',
			'871964bc-b8f3-43ba-9da0-4dd8e4185297', 94,
			'"resource_key"=>"Payments", "resource_id"=>"ee4f3d68-6a71-4672-bf80-6208748dc533"',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'CLICK', 'Payments');

INSERT INTO public.notifications(
	id, active, created_on, modified_on,
	created_by, modified_by,
	event, event_time, data,
	user_record_id, mobile_record_id,
	linked_resource,
	generated_on, sent_on, received_on,
	displayed_on, engaged_on, cancelled_on,
	engaged_action, engaged_source)
	VALUES (default, 'TRUE', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'VEHICLE_VERIFICATION', '2021-07-21 21:22:32.854254', '{"id": 10,"event": "VEHICLE_VERIFICATION","eventTime": "2021-06-17 12:44:37.226485Z","title": "Vehicle Confimation","message": "Your vehicle has been verified"}',
			'871964bc-b8f3-43ba-9da0-4dd8e4185297', 94,
			'"resource_key"=>"Vehicles", "resource_id"=>"ee4f3d68-6a71-4672-bf80-6208748dc533"',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'CLICK', 'Vehicles');

INSERT INTO public.notifications(
	id, active, created_on, modified_on,
	created_by, modified_by,
	event, event_time, data,
	user_record_id, mobile_record_id,
	linked_resource,
	generated_on, sent_on, received_on,
	displayed_on, engaged_on, cancelled_on,
	engaged_action, engaged_source)
	VALUES (default, 'TRUE', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'USER_LOGIN', '2021-07-21 21:22:32.854254', '{"id": 11,"event": "USER_LOGIN","eventTime": "2021-06-17 12:44:37.226485Z","title": "User Login","message": "You have been logged in by mobile {}"}',
			'871964bc-b8f3-43ba-9da0-4dd8e4185297', 94,
			'"resource_key"=>"Users", "resource_id"=>"ee4f3d68-6a71-4672-bf80-6208748dc533"',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'CLICK', 'Users');

INSERT INTO public.notifications(
	id, active, created_on, modified_on,
	created_by, modified_by,
	event, event_time, data,
	user_record_id, mobile_record_id,
	linked_resource,
	generated_on, sent_on, received_on,
	displayed_on, engaged_on, cancelled_on,
	engaged_action, engaged_source)
	VALUES (default, 'TRUE', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'TXN_TRANSFER_TOKEN', '2021-07-21 21:22:32.854254', '{"id": 12,"event": "TXN_TRANSFER_TOKEN","eventTime": "2021-06-17 12:44:37.226485Z","title": "Payment Completion","message": "Your payment is completed"}',
			'871964bc-b8f3-43ba-9da0-4dd8e4185297', 94,
			'"resource_key"=>"Payments", "resource_id"=>"ee4f3d68-6a71-4672-bf80-6208748dc533"',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'CLICK', 'Payments');

INSERT INTO public.notifications(
	id, active, created_on, modified_on,
	created_by, modified_by,
	event, event_time, data,
	user_record_id, mobile_record_id,
	linked_resource,
	generated_on, sent_on, received_on,
	displayed_on, engaged_on, cancelled_on,
	engaged_action, engaged_source)
	VALUES (default, 'TRUE', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'BOOKING_CONFIRMATION', '2021-07-21 21:22:32.854254', '{"id": 13,"event": "BOOKING_CONFIRMATION","eventTime": "2021-07-21 09:00:37.226485Z","title": "Booking Confirmation","message": "Your booking has been confirmed"}',
			'871964bc-b8f3-43ba-9da0-4dd8e4185297', 94,
			'"resource_key"=>"Bookings", "resource_id"=>"ee4f3d68-6a71-4672-bf80-6208748dc533"',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'CLICK', 'Bookings');

INSERT INTO public.notifications(
	id, active, created_on, modified_on,
	created_by, modified_by,
	event, event_time, data,
	user_record_id, mobile_record_id,
	linked_resource,
	generated_on, sent_on, received_on,
	displayed_on, engaged_on, cancelled_on,
	engaged_action, engaged_source)
	VALUES (default, 'TRUE', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'BOOKING_REJECTION', '2021-07-21 21:22:32.854254', '{"id": 14,"event": "BOOKING_REJECTION","eventTime": "2021-05-18 12:00:37.226485Z","title": "Booking Rejection","message": "Your booking has been rejected by {}"}',
			'871964bc-b8f3-43ba-9da0-4dd8e4185297', 94,
			'"resource_key"=>"Bookings", "resource_id"=>"ee4f3d68-6a71-4672-bf80-6208748dc533"',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254', '2021-07-21 21:22:32.854254',
			'CLICK', 'Bookings');

	update notifications set engaged_source = 'notification';



INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id, key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			currval('app_configs_id_seq'::regclass),
			'NOTIFICATION_DEEP_LINK', '{"myev":"[VEHICLE_VERIFICATION]","booking":"[BOOKING_REMINDER_FIRST,BOOKING_REMINDER_SECOND,BOOKING_CANCELLATION,BOOKING_REJECTION]","profile":"[USER_VERIFICATION]"}');


INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id, key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			currval('app_configs_id_seq'::regclass),
			'NOTIFICATION_SCHEDULED', '[BOOKING_REMINDER_FIRST,BOOKING_REMINDER_SECOND');


	alter table app_configs add visibility varchar(50);
    update app_configs set visibility = 'public' where visibility is NULL;
    update app_configs set visibility = 'private' where key like 'NOTIFICATION%';


INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id, key, value, visibility)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			currval('app_configs_id_seq'::regclass),
			'slot_durations', '15,30,60', 'private');




INSERT INTO dashboard.energy_consumption(
	id, active, created_on, modified_on, created_by, modified_by,
	consumed_date, station_record_id, grid, solar,
	diesel_generated)
	VALUES (default, true, now(), now(), '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
	 '2021-08-30', '5c1db7bb-39f3-4c38-8508-524058f2e7a9', 160, 120, 10);


INSERT INTO public.permissions(
	id, name, description, resource_name,
	can_retrieve, can_search, can_create, can_update, can_delete)
	VALUES (default, 'can-retrieve-search-dashboard' , NULL, 'dashboard',
			true, true, false, false, false);

INSERT INTO public.permissions(
	id, name, description, resource_name,
	can_retrieve, can_search, can_create, can_update, can_delete)
	VALUES (default, 'can-retrieve-search-station-overview-kpi' , NULL, 'station-overview-kpi',
			true, true, false, false, false);

INSERT INTO public.permissions(
	id, name, description, resource_name,
	can_retrieve, can_search, can_create, can_update, can_delete)
	VALUES (default, 'can-retrieve-search-station-service-price' , NULL, 'station-service-price',
			true, true, false, false, false);

INSERT INTO public.permissions(
	id, name, description, resource_name,
	can_retrieve, can_search, can_create, can_update, can_delete)
	VALUES (default, 'can-retrieve-search-station-energy-consumption' , NULL, 'station-energy-consumption',
			true, true, false, false, false);


INSERT INTO public.role_permission_rel(
	role_id, permission_id)
	VALUES (3, 19);

INSERT INTO public.role_permission_rel(
	role_id, permission_id)
	VALUES (3, 20);

INSERT INTO public.role_permission_rel(
	role_id, permission_id)
	VALUES (3, 21);

INSERT INTO public.role_permission_rel(
	role_id, permission_id)
	VALUES (3, 22);

-------------------------- update date value for test data in energy consumption ----------------------------------
update telemetry.energy_consumption
set reading_date = reading_date + interval '1 month' * 3;
-------------------------------------------------------------------------------------------------------------------

INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('app_configs_id_seq'::regclass),
			'dashboard_cache_limit_in_mins', '3');



INSERT INTO support.query_category(
	id, active, created_on, modified_on,
	created_by, modified_by, category, rank)
	VALUES (1, true, now(), now(),
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911', 'Account', 1);
INSERT INTO support.query_category(
	id, active, created_on, modified_on,
	created_by, modified_by, category, rank)
	VALUES (2, true, now(), now(),
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911', 'Vehicle', 2);
INSERT INTO support.query_category(
	id, active, created_on, modified_on,
	created_by, modified_by, category, rank)
	VALUES (3, true, now(), now(),
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'Verification', 3);
INSERT INTO support.query_category(
	id, active, created_on, modified_on,
	created_by, modified_by, category, rank)
	VALUES (4, true, now(), now(),
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'Wallet', 4);
INSERT INTO support.query_category(
	id, active, created_on, modified_on,
	created_by, modified_by, category, rank)
	VALUES (5, true, now(), now(),
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'Booking and Cancellation', 5);
INSERT INTO support.query_category(
	id, active, created_on, modified_on,
	created_by, modified_by, category, rank)
	VALUES (6, true, now(), now(),
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'Refund', 6);

INSERT INTO support.query_category(
	id, active, created_on, modified_on,
	created_by, modified_by, category, rank)
	VALUES (7, true, now(), now(),
			'b74b24fc-4639-46df-b67a-7572fcd95911', 'b74b24fc-4639-46df-b67a-7572fcd95911',
			'Other Issues', 7);

INSERT INTO public.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	key, value)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('app_configs_id_seq'::regclass),
			'query_msg_character_limit', '250');


INSERT INTO public.charging_connectors(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id,
	name, standard_name, description, icon_image)
	VALUES (nextval('charging_connectors_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('charging_connectors_id_seq'),
			'Bharat AC', 'Bharat AC001', 'bharat ac charger', null);


INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'TATA', 'Tigor EV XM', '2018', null, 4,
			null, null, null, 2);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'TATA', 'Tigor EV XT', '2018', null, 4,
			null, null, null, 2);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'TATA', 'Tigor EV XE+', '2019', null, 4,
			null, null, null, 2);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'TATA', 'Tigor EV XM+', '2019', null, 4,
			null, null, null, 2);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'TATA', 'Tigor EV XT+', '2019', null, 4,
			null, null, null, 2);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'TATA', 'Tigor EV XM', '2021', null, 4,
			null, null, null, 2);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'TATA', 'Tigor EV XE', '2021', null, 4,
			null, null, null, 2);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'TATA', 'Tigor EV XZ+', '2021', null, 4,
			null, null, null, 2);


INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'TATA', 'X-Press T XM+', '2021', null, 4,
			null, null, null, 2);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'TATA', 'X-Press T XT+', '2021', null, 4,
			null, null, null, 2);


INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'AUDI', 'E-tron', '2021', null, 4,
			null, null, null, 1);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'AUDI', 'E-tron sportback', '2021', null, 4,
			null, null, null, 1);


INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'JAGUAR', 'I-Pace S', '2021', null, 4,
			null, null, null, 1);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'JAGUAR', 'I-Pace SE', '2021', null, 4,
			null, null, null, 1);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'JAGUAR', 'I-Pace HSE', '2021', null, 4,
			null, null, null, 1);


INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'MERCEDES', 'EQC 400 MATIC', '2020', null, 4,
			null, null, null, 1);


INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'MAHINDRA', 'D2', '2016', null, 4,
			null, null, null, 2);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'MAHINDRA', 'D6', '2016', null, 4,
			null, null, null, 2);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'MAHINDRA', 'Cargo', '2016', null, 4,
			null, null, null, 4);
INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'MAHINDRA', 'Passenger', '2016', null, 4,
			null, null, null, 4);


INSERT INTO public.vehicle_masters(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by, record_id,
	brand, model, manufacturing_year, image, wheels,
	swappable_battery, swappable_battery_count, class_of_vehicle, charging_connector_record_id)
	VALUES (nextval('vehicle_masters_id_seq'), true, now(), now(), now(), 'infinity'::timestamp,
			'000000ad-ac99-44c8-9a6b-ca1214a60000', '000000ad-ac99-44c8-9a6b-ca1214a60000',
			currval('vehicle_masters_id_seq'),
			'STORM MOTORS', 'R3', '2021', null, 4,
			null, null, null, 2);


------------------------------------------------- schema update queries ----------------------------------------------
alter table public.auth_attempts set schema authentication;
alter table public.accounts set schema authentication;
alter table public.authenticated_sessions set schema authentication;
alter table public.stations set schema authentication;
alter table public.users set schema authentication;
alter table public.user_group_rel set schema authentication;
alter table public.app_configs set schema master;
alter table public.equipment_type_masters set schema master;
alter table public.group_role_rel set schema master;
alter table public.groups set schema master;
alter table public.permissions set schema master;
alter table public.role_permission_rel set schema master;
alter table public.roles set schema master;
alter table public.segments_of_day set schema master;
alter table public.service_masters set schema master;
alter table public.vehicle_masters set schema master;
alter table public.bookings set schema payment;
alter table public.invoices set schema payment;
alter table public.order_items set schema payment;
alter table public.orders set schema payment;
alter table public.payments set schema payment;
alter table public.service_rate_table set schema payment;
alter table public.service_rates set schema payment;
alter table public.token_conversion_rates set schema payment;
alter table public.wallets set schema payment;
----------------------------------------------------------------------------------------------------------------------

INSERT INTO master.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id, key, value, visibility)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('master.app_configs_id_seq'::regclass),
			'slot_break_in_mins', '5', 'private');


----------------------------------------------------------------------------------------------------------------------
INSERT INTO auth.permissions(
	id, name, resource_name, can_retrieve, can_search, can_create, can_update, can_delete)
	VALUES (default, 'can-search-retrieve-update-support-queries', 'support-query', true, true, false, true, false);

INSERT INTO auth.role_permission_rel(
	role_id, permission_id)
	VALUES (6, 23);

---------------------------------------------------------------------------------------------------------------
alter table transactional.stations add column hygge_box_number varchar(150);

------------------------------------------------------------------------------------
alter table master.vehicle_masters add column connector_record_ids integer[];

UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 22 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 3 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 6 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 5 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{2}'	WHERE id = 25 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{2}'	WHERE id = 26 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{2}'	WHERE id = 29 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{4}'	WHERE id = 27 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{4}'	WHERE id = 28 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{2,4}'	WHERE id = 9 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{2,4}'	WHERE id = 10 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{2,4}'	WHERE id = 11 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{2,4}'	WHERE id = 17 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{2,4}'	WHERE id = 18 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{2,4}'	WHERE id = 12 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{2,4}'	WHERE id = 13 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{2,4}'	WHERE id = 14 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{2,4}'	WHERE id = 15 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{2,4}'	WHERE id = 16 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 23 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 2 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 19 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 21 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 1 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 8 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 4 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 24 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 7 ;
UPDATE master.vehicle_masters SET connector_record_ids = '{1}'	WHERE id = 20 ;


-----------------------------------------------------------------------------------------------------------------------
alter table transactional.stations add column station_rating double precision;

INSERT INTO master.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id, key, value, visibility)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('master.app_configs_id_seq'::regclass),
			'NOTIFICATION_POPUP', 'STATION_RATING', 'private');

update master.app_configs set value = 'BOOKING_REMINDER_FIRST,BOOKING_REMINDER_SECOND,STATION_RATING' where key = 'NOTIFICATION_SCHEDULED';

--- dev qa uat
INSERT INTO analytics.station_statistics(
	id, active,
	created_on, modified_on,
	created_by, modified_by,
	rated_station, average_rating_value, rating_count,
	min_rating, max_rating)
	select distinct nextval('analytics.station_statistics_id_seq'), true,
	now(), now(),
	uuid('000000ad-ac99-44c8-9a6b-ca1214a60000'),uuid('000000ad-ac99-44c8-9a6b-ca1214a60000'),
	record_id, 0.0, 0,
	1,5 from transactional.stations
	;

INSERT INTO auth.permissions(
	id, name, resource_name, can_retrieve, can_search, can_create, can_update, can_delete)
	VALUES (default, 'can-create-update-delete-rating', 'rating', false, false, true, true, true);

INSERT INTO auth.role_permission_rel(
	role_id, permission_id)
	VALUES (2, 24);


INSERT INTO master.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id, key, value, visibility)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('master.app_configs_id_seq'::regclass),
			'NOTIFICATION_POPUP_VALIDITY',
			'{"data":[{"value": 5, "duration_unit": "min", "validity_type": "start" }, {"value": 168, "duration_unit": "hour", "validity_type": "end"}]}', 'private');



INSERT INTO master.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id, key, value, visibility)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('master.app_configs_id_seq'::regclass),
			'hygge_box_simulator', 'active', 'private');


INSERT INTO master.app_configs(
	id, active, created_on, modified_on, validity_start, validity_end,
	created_by, modified_by,
	record_id, key, value, visibility)
	VALUES (default, true, now(), now(), now(), 'infinity'::timestamp,
			'51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00', '51f3fa8d-a1f1-4e3a-b23c-7f7ad8774f00',
			currval('master.app_configs_id_seq'::regclass),
			'mandatory_rating_count', '2', 'private');