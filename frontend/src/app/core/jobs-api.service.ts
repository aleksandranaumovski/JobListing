import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { Job, JobFilters, JobPage, JobQuery, JobStatus, JobSubmission, ModeratedJob, ModeratedJobPage } from './models';

@Injectable({ providedIn: 'root' })
export class JobsApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api';

  list(query: JobQuery): Observable<JobPage> {
    let params = new HttpParams();
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, String(value));
      }
    });
    return this.http.get<JobPage>(`${this.baseUrl}/jobs`, { params });
  }

  filters(): Observable<JobFilters> {
    return this.http.get<JobFilters>(`${this.baseUrl}/jobs/filters`);
  }

  detail(id: string): Observable<Job> {
    return this.http.get<Job>(`${this.baseUrl}/jobs/${id}`);
  }

  submit(job: JobSubmission): Observable<Job> {
    return this.http.post<Job>(`${this.baseUrl}/jobs`, job);
  }

  mine(page = 1, pageSize = 50): Observable<JobPage> {
    const params = new HttpParams().set('page', page).set('page_size', pageSize);
    return this.http.get<JobPage>(`${this.baseUrl}/jobs/mine`, { params });
  }

  moderationQueue(status: JobStatus | 'all' = 'pending', page = 1, pageSize = 50): Observable<ModeratedJobPage> {
    const params = new HttpParams().set('status', status).set('page', page).set('page_size', pageSize);
    return this.http.get<ModeratedJobPage>(`${this.baseUrl}/admin/jobs`, { params });
  }

  approve(id: string): Observable<ModeratedJob> {
    return this.http.post<ModeratedJob>(`${this.baseUrl}/admin/jobs/${id}/approve`, {});
  }

  reject(id: string): Observable<ModeratedJob> {
    return this.http.post<ModeratedJob>(`${this.baseUrl}/admin/jobs/${id}/reject`, {});
  }
}
