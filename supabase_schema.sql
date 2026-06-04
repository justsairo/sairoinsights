-- SQL for creating Supabase tables and RLS policies

-- Enable pgcrypto for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Table: public.datasets
-- Stores metadata for user-uploaded datasets
CREATE TABLE IF NOT EXISTS public.datasets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) NOT NULL,
  token text NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

-- Enable Row Level Security (RLS) on the datasets table
ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own datasets
CREATE POLICY "Users can view their own datasets" ON public.datasets
  FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own datasets
CREATE POLICY "Users can insert their own datasets" ON public.datasets
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own datasets
CREATE POLICY "Users can delete their own datasets" ON public.datasets
  FOR DELETE USING (auth.uid() = user_id);

-- Table: public.news_articles
-- Stores collected news articles
CREATE TABLE IF NOT EXISTS public.news_articles (
  id text PRIMARY KEY, -- Hash of the URL
  timestamp timestamp with time zone NOT NULL,
  pub_date timestamp with time zone NOT NULL,
  source text NOT NULL,
  category text NOT NULL,
  headline text NOT NULL,
  summary text,
  url text NOT NULL,
  market_snapshot jsonb, -- Stores associated market data at time of collection
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

-- Enable Row Level Security (RLS) on the news_articles table
ALTER TABLE public.news_articles ENABLE ROW LEVEL SECURITY;

-- Policy: All authenticated users can read news articles
CREATE POLICY "All authenticated users can read news_articles" ON public.news_articles
  FOR SELECT TO authenticated USING (true);

-- Policy: Admin can insert news articles (requires additional check if news collection is admin-only)
-- For now, allow service role to insert
CREATE POLICY "Admin/service role can insert news_articles" ON public.news_articles
  FOR INSERT WITH CHECK (true); -- Or add a more specific condition if admin user ID is known

-- Table: public.market_snapshots
-- Stores periodic market data snapshots
CREATE TABLE IF NOT EXISTS public.market_snapshots (
  timestamp timestamp with time zone PRIMARY KEY NOT NULL,
  sp500 numeric,
  nasdaq numeric,
  ftse100 numeric,
  dax numeric,
  eur_usd numeric,
  gbp_usd numeric,
  usd_jpy numeric,
  us_10y_yield numeric,
  us_2y_yield numeric,
  gold_usd numeric,
  wti_oil numeric,
  brent_oil numeric,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

-- Enable Row Level Security (RLS) on the market_snapshots table
ALTER TABLE public.market_snapshots ENABLE ROW LEVEL SECURITY;

-- Policy: All authenticated users can read market snapshots
CREATE POLICY "All authenticated users can read market_snapshots" ON public.market_snapshots
  FOR SELECT TO authenticated USING (true);

-- Policy: Admin can insert market snapshots
CREATE POLICY "Admin/service role can insert market_snapshots" ON public.market_snapshots
  FOR INSERT WITH CHECK (true); -- Or add a more specific condition if admin user ID is known
