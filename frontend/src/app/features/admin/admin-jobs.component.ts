import { DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { JobsApiService } from '../../core/jobs-api.service';
import { JobStatus, ModeratedJob } from '../../core/models';
import { slugify } from '../../shared/slug';

type QueueFilter = JobStatus | 'all';

@Component({
  selector: 'app-admin-jobs',
  standalone: true,
  imports: [DatePipe, RouterLink],
  template: `
    <section class="detail detail--wide">
      <div class="page-head">
        <div>
          <p class="eyebrow">Администрација</p>
          <h1 class="auth-title">Одобрување на огласи</h1>
        </div>
        <div class="queue-tabs">
          @for (tab of tabs; track tab.value) {
            <button
              type="button"
              class="queue-tab"
              [class.queue-tab--active]="filter() === tab.value"
              (click)="setFilter(tab.value)"
            >{{ tab.label }}</button>
          }
        </div>
      </div>

      @if (loading()) {
        <div class="state">Се вчитуваат огласи...</div>
      } @else if (error()) {
        <div class="state state--error">{{ error() }}</div>
      } @else {
        <div class="moderation-list">
          @for (job of jobs(); track job.id) {
            <article class="moderation-card">
              <div class="moderation-card__main">
                <span class="pill" [class]="'pill pill--' + job.status">{{ statusLabel(job.status) }}</span>
                <h2><a [routerLink]="['/jobs', job.id, slug(job)]">{{ job.title }}</a></h2>
                <p class="moderation-card__meta">
                  {{ job.company }}@if (job.city) { · {{ job.city }} }
                  @if (job.submitted_by) { · Поднесен од {{ job.submitted_by }} }
                  @if (job.created_at) { · {{ job.created_at | date: 'dd.MM.yyyy HH:mm' }} }
                </p>
              </div>
              <div class="moderation-card__actions">
                @if (job.status !== 'approved') {
                  <button type="button" (click)="approve(job)" [disabled]="busy() === job.id">Одобри</button>
                }
                @if (job.status !== 'rejected') {
                  <button type="button" class="danger" (click)="reject(job)" [disabled]="busy() === job.id">Одбиј</button>
                }
              </div>
            </article>
          } @empty {
            <div class="state">Нема огласи во оваа листа.</div>
          }
        </div>
      }
    </section>
  `
})
export class AdminJobsComponent implements OnInit {
  private readonly api = inject(JobsApiService);

  readonly tabs: { value: QueueFilter; label: string }[] = [
    { value: 'pending', label: 'Чекаат' },
    { value: 'approved', label: 'Одобрени' },
    { value: 'rejected', label: 'Одбиени' },
    { value: 'all', label: 'Сите' }
  ];

  jobs = signal<ModeratedJob[]>([]);
  filter = signal<QueueFilter>('pending');
  loading = signal(true);
  error = signal<string | null>(null);
  busy = signal<string | null>(null);

  ngOnInit(): void {
    this.load();
  }

  setFilter(filter: QueueFilter): void {
    this.filter.set(filter);
    this.load();
  }

  approve(job: ModeratedJob): void {
    this.busy.set(job.id);
    this.api.approve(job.id).subscribe({
      next: () => {
        this.busy.set(null);
        this.load();
      },
      error: () => {
        this.busy.set(null);
        this.error.set('Одобрувањето не успеа. Обиди се повторно.');
      }
    });
  }

  reject(job: ModeratedJob): void {
    this.busy.set(job.id);
    this.api.reject(job.id).subscribe({
      next: () => {
        this.busy.set(null);
        this.load();
      },
      error: () => {
        this.busy.set(null);
        this.error.set('Одбивањето не успеа. Обиди се повторно.');
      }
    });
  }

  slug(job: ModeratedJob): string {
    return slugify(job.title);
  }

  statusLabel(status: JobStatus): string {
    switch (status) {
      case 'approved':
        return 'Одобрен';
      case 'rejected':
        return 'Одбиен';
      default:
        return 'Чека одобрување';
    }
  }

  private load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.moderationQueue(this.filter()).subscribe({
      next: (page) => {
        this.jobs.set(page.items);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Не може да се вчита листата на огласи.');
        this.loading.set(false);
      }
    });
  }
}
