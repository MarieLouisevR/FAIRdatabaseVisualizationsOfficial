import { Hono } from 'https://deno.land/x/hono@v3.11.7/mod.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.3';
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';

const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
const supabaseKey = Deno.env.get('SUPABASE_KEY')!; 
const supabase = createClient(supabaseUrl, supabaseKey);

const app = new Hono();

app.get('/fetch_tables', async (c) => {
    try {
        const { data, error } = await supabase.rpc('get_tables');

        if (error) {
            console.error("Supabase error:", error);
            return c.json({ error: error.message }, 500);
        }

        if (!data || data.length === 0) {
            console.warn("No tables found");
            return c.json([], 200);
        }

        return c.json(data);
    } catch (error) {
        console.error("Unexpected error:", error);
        return c.json({ error: error.message }, 500);
    }
});


serve(app.fetch);
