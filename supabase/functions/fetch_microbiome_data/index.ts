// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

// Setup type definitions for built-in Supabase Runtime APIs
import { Hono } from 'hono'; // Import Hono framework for routing
import { createClient } from '@supabase/supabase-js'; // Import Supabase client

// Initialize Supabase client with environment variables
const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
const supabaseKey = Deno.env.get('SUPABASE_KEY')!;
const supabase = createClient(supabaseUrl, supabaseKey);

// Create a new Hono application
const app = new Hono();

// Add this new endpoint to your existing code
app.get('/fetch_microbiome_data', async (c) => {
  // Fetch data from the first table
  const { data: table1Data, error: error1 } = await supabase
    .from('table1') // Replace with your first table name
    .select('*');

  // Fetch data from the second table
  const { data: table2Data, error: error2 } = await supabase
    .from('table2') // Replace with your second table name
    .select('*');

  if (error1 || error2) {
    return c.json({ error: error1?.message || error2?.message }, 500);
  }

  // Combine the data
  const combinedData = [...(table1Data || []), ...(table2Data || [])];

  return c.json(combinedData);
});

// Start the Deno server for handling requests
Deno.serve(app.fetch);

/* To invoke locally:

  1. Run `supabase start` (see: https://supabase.com/docs/reference/cli/supabase-start)
  2. Make an HTTP request:

  curl -i --location --request POST 'http://127.0.0.1:54321/functions/v1/fetch_microbiome_data' \
    --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0' \
    --header 'Content-Type: application/json' \
    --data '{"name":"Functions"}'

*/
