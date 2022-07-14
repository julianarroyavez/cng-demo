

create or replace function fn_user_verification() returns trigger as $update_user_verification$
begin
	UPDATE transactional.users
        SET verified=true
        WHERE id=new.id and validity_end  = 'infinity'::timestamp;
	return new;
end;
$update_user_verification$
language plpgsql;

create trigger update_user_verification after insert or update of record_id on transactional.users
for each row execute procedure fn_user_verification();


create or replace function fn_vehicle_verification() returns trigger as $update_vehicle_verification$
begin
        update transactional.vehicles
        set verified=true
        WHERE record_id=new.record_id;
        return new;
end;
$update_vehicle_verification$
language plpgsql;

create trigger update_vehicle_verification after insert or update of record_id on transactional.vehicles
for each row execute procedure fn_vehicle_verification();



create or replace function fn_verification() returns trigger as $update_verification$
begin
        UPDATE transactional.verifications
                SET verified_by='000000ad-ac99-44c8-9a6b-ca1214a60000',
                verification_time=now(), verification_status='VERIFIED',
                verification_expiry='infinity'::timestamp
                WHERE id=new.id;
        return new;
end;
$update_verification$
language plpgsql;

create trigger update_verification after insert or update of modified_on on transactional.verifications
for each row execute procedure fn_verification();



create or replace function fn_station_verification() returns trigger as $update_station_verification$
begin
      UPDATE transactional.stations
        SET verified=true
        WHERE id=new.id and validity_end  = 'infinity'::timestamp;
        return new;
end;
$update_station_verification$
language plpgsql;

create trigger update_station_verification after insert or update of record_id on transactional.stations
for each row execute procedure fn_station_verification();



create or replace function fn_update_wallets() returns trigger as $update_wallet$
begin
        UPDATE payment.wallets
                SET balance = 3000.0
                WHERE id=new.id;
        return new;
end;
$update_wallet$
language plpgsql;

create trigger update_wallet after insert or update of id on payment.wallets
for each row execute procedure fn_update_wallets();


create or replace function fn_update_otp() returns trigger as $update_otp$
begin
        UPDATE auth.auth_attempts
                SET otp = '123456'
                WHERE txn_id=new.txn_id and new.phone_number like '00%';
        return new;
end;
$update_otp$
language plpgsql;

create trigger update_otp after insert or update of modified_on on auth.auth_attempts
for each row execute procedure fn_update_otp();


create or replace function fn_update_station_hygge_box() returns trigger as $update_hygge_box$
begin
        UPDATE transactional.stations
                SET has_hygge_box = true, modified_on = now(), hygge_box_number = '008'
                WHERE id=new.id;
        return new;
end;
$update_hygge_box$
language plpgsql;

create trigger update_station_hygge_box after insert or update of id on transactional.stations
for each row execute procedure fn_update_station_hygge_box();



--drop trigger if exists update_user_verification on "transactional"."users";
--drop trigger if exists update_station_verification on "transactional"."stations";

