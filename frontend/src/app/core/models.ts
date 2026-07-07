export type JobStatus = 'pending' | 'approved' | 'rejected';

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
  status?: JobStatus;
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

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'user' | 'admin';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface JobSubmission {
  title: string;
  company: string;
  city?: string;
  location?: string;
  category?: string;
  employment_type?: string;
  salary?: string;
  url?: string;
  description?: string;
  active_until?: string;
}

export interface ModeratedJob extends Job {
  status: JobStatus;
  submitted_by?: string | null;
  created_at?: string | null;
}

export interface ModeratedJobPage {
  items: ModeratedJob[];
  meta: PageMeta;
}
