
---- This function verifies the user
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
	
---- This function verifies the vehicle
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


---- This function verifies the verification table entry for either user or station
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



---- This function verifies the station
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


---- This function updates the wallet balance to 2000
create or replace function fn_update_wallets() returns trigger as $update_wallet$
begin
        UPDATE payment.wallets
                SET balance = 2000.0
                WHERE id=new.id;
        return new;
end;
$update_wallet$
language plpgsql;

create trigger update_wallet after insert or update of modified_on on payment.wallets
for each row execute procedure fn_update_wallets();


---- This function updates the OTP for number starting from 00 to 123456
create or replace function fn_update_otp() returns trigger as $update_otp$
begin
        UPDATE auth.auth_attempts
                SET otp = '123456'
                WHERE txn_id=new.txn_id;
        return new;
end;
$update_otp$
language plpgsql;

create trigger update_otp after insert or update of modified_on on auth.auth_attempts
for each row execute procedure fn_update_otp();



--drop trigger if exists update_user_verification on "transactional"."users";
--drop trigger if exists update_station_verification on "transactional"."stations";


---- This function Updates the booking status to FULFILLED when the date matches the endDate and time of a Booked slot
create or replace function fn_update_booking_status() returns trigger as $update_booking$
begin
        with result as (
                select s.id
                from transactional.slots s 
                where to_char(s.date, 'yyyy-mm-dd') = to_char(now(), 'yyyy-mm-dd') 
                and to_char(s.end_time, 'hh24:mi:00') = to_char(now(), 'hh24:mi:00')
        )
        update transactional.bookings
                SET status = 'FULFILLED', modified_on = now()
                FROM result 
                where slot_id in (result.id)
        return new;
end;
$update_booking$
language plpgsql;


