import { DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { JobsApiService } from '../../core/jobs-api.service';
import { Job, JobStatus } from '../../core/models';
import { slugify } from '../../shared/slug';

@Component({
  selector: 'app-my-jobs',
  standalone: true,
  imports: [DatePipe, RouterLink],
  template: `
    <section class="detail">
      <div class="page-head">
        <div>
          <p class="eyebrow">Мои огласи</p>
          <h1 class="auth-title">Моите објавени огласи</h1>
        </div>
        <a routerLink="/submit" class="apply">Додади нов оглас</a>
      </div>

      @if (justSubmitted()) {
        <div class="state state--success">Огласот е успешно испратен и чека одобрување од администратор.</div>
      }

      @if (loading()) {
        <div class="state">Се вчитуваат твоите огласи...</div>
      } @else if (error()) {
        <div class="state state--error">{{ error() }}</div>
      } @else {
        <div class="moderation-list">
          @for (job of jobs(); track job.id) {
            <article class="moderation-card">
              <div class="moderation-card__main">
                <span class="pill" [class]="'pill pill--' + (job.status ?? 'pending')">{{ statusLabel(job.status) }}</span>
                <h2><a [routerLink]="['/jobs', job.id, slug(job)]">{{ job.title }}</a></h2>
                <p class="moderation-card__meta">
                  {{ job.company }}@if (job.city) { · {{ job.city }} }
                  @if (job.posted_at) { · Објавен {{ job.posted_at | date: 'dd.MM.yyyy' }} }
                </p>
              </div>
            </article>
          } @empty {
            <div class="state">Немаш испратено огласи. <a routerLink="/submit">Додади го првиот оглас</a>.</div>
          }
        </div>
      }
    </section>
  `
})
export class MyJobsComponent implements OnInit {
  private readonly api = inject(JobsApiService);
  private readonly route = inject(ActivatedRoute);

  jobs = signal<Job[]>([]);
  loading = signal(true);
  error = signal<string | null>(null);
  justSubmitted = signal(false);

  ngOnInit(): void {
    this.justSubmitted.set(this.route.snapshot.queryParamMap.has('submitted'));
    this.api.mine().subscribe({
      next: (page) => {
        this.jobs.set(page.items);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Не може да се вчитаат твоите огласи.');
        this.loading.set(false);
      }
    });
  }

  slug(job: Job): string {
    return slugify(job.title);
  }

  statusLabel(status?: JobStatus): string {
    switch (status) {
      case 'approved':
        return 'Одобрен';
      case 'rejected':
        return 'Одбиен';
      default:
        return 'Чека одобрување';
    }
  }
}
