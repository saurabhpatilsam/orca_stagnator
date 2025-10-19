-- Reload PostgREST schema cache to expose orca schema tables to API
NOTIFY pgrst, 'reload schema';
