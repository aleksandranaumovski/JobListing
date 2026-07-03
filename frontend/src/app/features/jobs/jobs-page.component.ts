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
        <input name="q" [(ngModel)]="query.q" placeholder="Пребарај по позиција, компанија или клучен збор" aria-label="Пребарај огласи">
        <button type="submit">Пребарај</button>
      </form>
    </section>

    <section class="layout">
      <aside class="filters">
        <label>
          Град
          <select name="city" [(ngModel)]="query.city" (change)="applyFilters(true)">
            <option value="">Сите градови</option>
            @for (city of filters()?.cities ?? []; track city) { <option [value]="city">{{ city }}</option> }
          </select>
        </label>
        <label>
          Компанија
          <select name="company" [(ngModel)]="query.company" (change)="applyFilters(true)">
            <option value="">Сите компании</option>
            @for (company of filters()?.companies ?? []; track company) { <option [value]="company">{{ company }}</option> }
          </select>
        </label>
        <label>
          Категорија
          <select name="category" [(ngModel)]="query.category" (change)="applyFilters(true)">
            <option value="">Сите категории</option>
            @for (category of filters()?.categories ?? []; track category) { <option [value]="category">{{ category }}</option> }
          </select>
        </label>
        <label>
          Вид на работа
          <select name="employment_type" [(ngModel)]="query.employment_type" (change)="applyFilters(true)">
            <option value="">Сите видови</option>
            @for (type of filters()?.employment_types ?? []; track type) { <option [value]="type">{{ type }}</option> }
          </select>
        </label>
        <label>
          Подредување
          <select name="sort" [(ngModel)]="query.sort" (change)="applyFilters(true)">
            <option value="newest">Најнови</option>
            <option value="oldest">Најстари</option>
          </select>
        </label>
        <button type="button" class="secondary" (click)="reset()">Ресетирај</button>
      </aside>

      <div class="results">
        @if (loading()) {
          <div class="state">Се вчитуваат огласи...</div>
        } @else if (error()) {
          <div class="state state--error">{{ error() }}</div>
        } @else {
          <div class="result-count">{{ page()?.meta?.total ?? 0 }} пронајдени огласи</div>
          <div class="cards">
            @for (job of page()?.items ?? []; track job.id) {
              <app-job-card [job]="job" />
            } @empty {
              <div class="state">Нема огласи според избраните филтри.</div>
            }
          </div>
          @if ((page()?.meta?.pages ?? 0) > 1) {
            <nav class="pagination" aria-label="Навигација по страници">
              <button type="button" (click)="changePage((page()?.meta?.page ?? 1) - 1)" [disabled]="(page()?.meta?.page ?? 1) <= 1">Претходна</button>
              <span>Страница {{ page()?.meta?.page }} од {{ page()?.meta?.pages }}</span>
              <button type="button" (click)="changePage((page()?.meta?.page ?? 1) + 1)" [disabled]="(page()?.meta?.page ?? 1) >= (page()?.meta?.pages ?? 1)">Следна</button>
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
        this.error.set('Не може да се вчитаат огласите. Обидете се повторно.');
        this.loading.set(false);
      }
    });
  }

  private cleanQuery(query: JobQuery): JobQuery {
    return Object.fromEntries(Object.entries(query).filter(([, value]) => value !== '' && value !== undefined && value !== null)) as JobQuery;
  }
}
