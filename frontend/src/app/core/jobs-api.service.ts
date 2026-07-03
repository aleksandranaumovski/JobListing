import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { Job, JobFilters, JobPage, JobQuery } from './models';

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
}
