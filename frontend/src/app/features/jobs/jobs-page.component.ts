import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { JobsApiService } from '../../core/jobs-api.service';
import { JobFilters, JobPage, JobQuery } from '../../core/models';
import { JobCardComponent } from './job-card.component';

@Component({
  selector: 'app-jobs-page',
  standalone: true,
  imports: [FormsModule, JobCardComponent],
  template: `
    <section class="hero">
      <div>
        <p class="eyebrow">Македонски огласи за работа</p>
        <h1>Најнови огласи за работа</h1>
      </div>
      <form class="search" (ngSubmit)="applyFilters(true)">
        <input name="q" [(ngModel)]="query.q" placeholder="Search by title, company or keyword" aria-label="Search jobs">
        <button type="submit">Search</button>
      </form>
    </section>

    <section class="layout">
      <aside class="filters">
        <label>
          City
          <select name="city" [(ngModel)]="query.city" (change)="applyFilters(true)">
            <option value="">All cities</option>
            @for (city of filters()?.cities ?? []; track city) { <option [value]="city">{{ city }}</option> }
          </select>
        </label>
        <label>
          Company
          <select name="company" [(ngModel)]="query.company" (change)="applyFilters(true)">
            <option value="">All companies</option>
            @for (company of filters()?.companies ?? []; track company) { <option [value]="company">{{ company }}</option> }
          </select>
        </label>
        <label>
          Category
          <select name="category" [(ngModel)]="query.category" (change)="applyFilters(true)">
            <option value="">All categories</option>
            @for (category of filters()?.categories ?? []; track category) { <option [value]="category">{{ category }}</option> }
          </select>
        </label>
        <label>
          Employment
          <select name="employment_type" [(ngModel)]="query.employment_type" (change)="applyFilters(true)">
            <option value="">Any type</option>
            @for (type of filters()?.employment_types ?? []; track type) { <option [value]="type">{{ type }}</option> }
          </select>
        </label>
        <label>
          Sort
          <select name="sort" [(ngModel)]="query.sort" (change)="applyFilters(true)">
            <option value="newest">Newest</option>
            <option value="oldest">Oldest</option>
          </select>
        </label>
        <button type="button" class="secondary" (click)="reset()">Reset</button>
      </aside>

      <div class="results">
        @if (loading()) {
          <div class="state">Loading jobs...</div>
        } @else if (error()) {
          <div class="state state--error">{{ error() }}</div>
        } @else {
          <div class="result-count">{{ page()?.meta?.total ?? 0 }} jobs found</div>
          <div class="cards">
            @for (job of page()?.items ?? []; track job.id) {
              <app-job-card [job]="job" />
            } @empty {
              <div class="state">No jobs match the selected filters.</div>
            }
          </div>
          @if ((page()?.meta?.pages ?? 0) > 1) {
            <nav class="pagination" aria-label="Pagination">
              <button type="button" (click)="changePage((page()?.meta?.page ?? 1) - 1)" [disabled]="(page()?.meta?.page ?? 1) <= 1">Previous</button>
              <span>Page {{ page()?.meta?.page }} of {{ page()?.meta?.pages }}</span>
              <button type="button" (click)="changePage((page()?.meta?.page ?? 1) + 1)" [disabled]="(page()?.meta?.page ?? 1) >= (page()?.meta?.pages ?? 1)">Next</button>
            </nav>
          }
        }
      </div>
    </section>
  `
})
export class JobsPageComponent implements OnInit {
  private readonly api = inject(JobsApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  page = signal<JobPage | null>(null);
  filters = signal<JobFilters | null>(null);
  loading = signal(false);
  error = signal<string | null>(null);
  query: JobQuery = { page: 1, page_size: 12, sort: 'newest' };

  ngOnInit(): void {
    this.route.queryParamMap.subscribe((params) => {
      this.query = {
        page: Number(params.get('page') ?? 1),
        page_size: 12,
        q: params.get('q') ?? '',
        city: params.get('city') ?? '',
        company: params.get('company') ?? '',
        category: params.get('category') ?? '',
        employment_type: params.get('employment_type') ?? '',
        sort: (params.get('sort') as 'newest' | 'oldest') ?? 'newest'
      };
      this.load();
    });
    this.api.filters().subscribe({ next: (filters) => this.filters.set(filters) });
  }

  applyFilters(resetPage = false): void {
    if (resetPage) {
      this.query.page = 1;
    }
    this.router.navigate(['/search'], { queryParams: this.cleanQuery(this.query) });
  }

  changePage(page: number): void {
    this.query.page = page;
    this.applyFilters();
  }

  reset(): void {
    this.query = { page: 1, page_size: 12, sort: 'newest' };
    this.router.navigate(['/']);
  }

  private load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.list(this.query).subscribe({
      next: (page) => {
        this.page.set(page);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load jobs. Please try again.');
        this.loading.set(false);
      }
    });
  }

  private cleanQuery(query: JobQuery): JobQuery {
    return Object.fromEntries(Object.entries(query).filter(([, value]) => value !== '' && value !== undefined && value !== null)) as JobQuery;
  }
}
