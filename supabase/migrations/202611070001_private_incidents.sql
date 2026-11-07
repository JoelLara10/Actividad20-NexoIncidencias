-- Actividad 20: ejecutar en un proyecto Supabase dedicado.
-- No contiene contraseñas ni claves administrativas.
begin;
create extension if not exists pgcrypto;
create table if not exists public.incidents (
 id uuid primary key default gen_random_uuid(),
 owner_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
 title text not null check(char_length(btrim(title)) between 5 and 100),
 description text not null check(char_length(btrim(description)) between 10 and 1200),
 location text not null check(char_length(btrim(location)) between 2 and 120),
 category text not null check(category in ('Electricidad','Agua y sanitarios','Infraestructura','Limpieza','Seguridad','Otro')),
 priority text not null default 'medium' check(priority in ('low','medium','high','critical')),
 status text not null default 'open' check(status in ('open','in_progress','resolved')),
 photo_path text not null,
 photo_state text not null default 'pending' check(photo_state in ('pending','ready','failed')),
 photo_mime text not null check(photo_mime in ('image/jpeg','image/png','image/webp')),
 photo_bytes integer not null check(photo_bytes between 1 and 5242880),
 photo_sha256 text not null check(photo_sha256 ~ '^[a-f0-9]{64}$'),
 archived boolean not null default false,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now(),
 check(split_part(photo_path,'/',1)=owner_id::text and split_part(photo_path,'/',2)=id::text)
);
create table if not exists public.incident_events (
 id uuid primary key default gen_random_uuid(),
 incident_id uuid not null references public.incidents(id) on delete cascade,
 owner_id uuid not null references auth.users(id) on delete cascade,
 message text not null,
 created_at timestamptz not null default now()
);
create index if not exists incidents_owner_date_idx on public.incidents(owner_id,created_at desc);
create index if not exists incident_events_owner_incident_idx on public.incident_events(owner_id,incident_id,created_at desc);
alter table public.incidents enable row level security;
alter table public.incident_events enable row level security;
revoke all on public.incidents,public.incident_events from anon;
grant select,insert,update on public.incidents to authenticated;
grant select on public.incident_events to authenticated;
create policy "incidents_select_own" on public.incidents for select to authenticated using(owner_id=(select auth.uid()));
create policy "incidents_insert_own" on public.incidents for insert to authenticated with check(owner_id=(select auth.uid()));
create policy "incidents_update_own" on public.incidents for update to authenticated using(owner_id=(select auth.uid())) with check(owner_id=(select auth.uid()));
create policy "events_select_own" on public.incident_events for select to authenticated using(owner_id=(select auth.uid()));
create or replace function public.track_incident_changes() returns trigger language plpgsql security definer set search_path=public,pg_temp as $$
begin
 if NEW.photo_state='ready' and not exists(select 1 from storage.objects where bucket_id='incidence-photos' and name=NEW.photo_path) then raise exception 'La fotografía todavía no está almacenada en el contenedor privado'; end if;
 if TG_OP='INSERT' then
  insert into public.incident_events(incident_id,owner_id,message) values(NEW.id,NEW.owner_id,'Incidencia registrada; transferencia de foto pendiente.');
 else
  NEW.updated_at=now();
  if NEW.owner_id<>OLD.owner_id then raise exception 'El propietario no se puede cambiar'; end if;
  if NEW.photo_state='ready' and OLD.photo_state<>'ready' then
   insert into public.incident_events(incident_id,owner_id,message) values(NEW.id,NEW.owner_id,'Fotografía guardada en el almacenamiento privado.');
  end if;
  if NEW.status<>OLD.status then
   insert into public.incident_events(incident_id,owner_id,message) values(NEW.id,NEW.owner_id,'Estado actualizado a '||case NEW.status when 'open' then 'Abierta' when 'in_progress' then 'En atención' else 'Resuelta' end);
  end if;
  if NEW.archived and not OLD.archived then
   insert into public.incident_events(incident_id,owner_id,message) values(NEW.id,NEW.owner_id,'Reporte archivado.');
  end if;
 end if;
 return NEW;
end $$;
revoke all on function public.track_incident_changes() from public;
create or replace function public.touch_incident() returns trigger language plpgsql set search_path=public,pg_temp as $$ begin NEW.updated_at=now();return NEW;end $$;
create trigger incidents_touch before update on public.incidents for each row execute function public.touch_incident();
create trigger incidents_track after insert or update on public.incidents for each row execute function public.track_incident_changes();
-- Bucket privado, límites también en el servidor.
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
values('incidence-photos','incidence-photos',false,5242880,array['image/jpeg','image/png','image/webp'])
on conflict(id) do update set public=false,file_size_limit=5242880,allowed_mime_types=array['image/jpeg','image/png','image/webp'];
create policy "photos_select_own" on storage.objects for select to authenticated using(bucket_id='incidence-photos' and (storage.foldername(name))[1]=(select auth.uid())::text);
create policy "photos_insert_own" on storage.objects for insert to authenticated with check(bucket_id='incidence-photos' and (storage.foldername(name))[1]=(select auth.uid())::text);
create policy "photos_update_own" on storage.objects for update to authenticated using(bucket_id='incidence-photos' and (storage.foldername(name))[1]=(select auth.uid())::text) with check(bucket_id='incidence-photos' and (storage.foldername(name))[1]=(select auth.uid())::text);
commit;


