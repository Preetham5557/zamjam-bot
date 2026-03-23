import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY

// Use supabaseAnonKey here, NOT supabaseKey
export const supabase = createClient(supabaseUrl, supabaseAnonKey)