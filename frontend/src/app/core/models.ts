export interface Job {
  id: string;
  source: string;
  title: string;
  company?: string | null;
  city?: string | null;
  location?: string | null;
  category?: string | null;
  employment_type?: string | null;
  url?: string | null;
  posted_at?: string | null;
  active_until?: string | null;
  salary?: string | null;
  is_new: boolean;
  scraped_at?: string | null;
  raw_text?: string | null;
  source_payload?: Record<string, unknown>;
}

export interface PageMeta {
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface JobPage {
  items: Job[];
  meta: PageMeta;
}

export interface JobFilters {
  cities: string[];
  companies: string[];
  categories: string[];
  employment_types: string[];
}

export interface JobQuery {
  page?: number;
  page_size?: number;
  q?: string;
  company?: string;
  city?: string;
  category?: string;
  employment_type?: string;
  sort?: 'newest' | 'oldest';
}
