
---- This function and sequence is used to update the hygge box number for stations 
create sequence transactional.hygge_box_number start 1000 increment 1;

update transactional.stations set hygge_box_number = nextval('transactional.hygge_box_number')::varchar(150)
where contact_number not in ('9082412504','9082414954');

update transactional.stations set has_hygge_box = false, hygge_box_number = null where verified = false;

create or replace function fn_station_hygge_box_addition() returns trigger as $update_station_hygge_box$
begin
      UPDATE transactional.stations
        SET has_hygge_box=true, hygge_box_number = nextval('transactional.hygge_box_number')::varchar(150)
        WHERE id=new.id and validity_end  = 'infinity'::timestamp and verified = true;
        return new;
end;
$update_station_hygge_box$
language plpgsql;

create trigger update_station_hygge_box after insert or update of verified on transactional.stations
for each row execute procedure fn_station_hygge_box_addition();
