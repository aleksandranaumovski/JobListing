import { Component, Input } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';

import { Job } from '../../core/models';
import { slugify } from '../../shared/slug';

@Component({
  selector: 'app-job-card',
  standalone: true,
  imports: [DatePipe, RouterLink],
  template: `
    <article class="job-card">
      <a class="job-card__link" [routerLink]="['/jobs', job.id, slug(job.title)]" [attr.aria-label]="job.title"></a>

      <header class="job-card__head">
        <span class="pill pill--source">{{ job.source }}</span>
        @if (job.is_new) {
          <span class="pill pill--new"><span class="dot"></span>Ново</span>
        }
      </header>

      <h2 class="job-card__title">
        <a [routerLink]="['/jobs', job.id, slug(job.title)]">{{ job.title }}</a>
      </h2>

      <ul class="job-card__meta">
        @if (job.company) {
          <li>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 21h18M6 21V7l6-4 6 4v14M10 9h.01M14 9h.01M10 13h.01M14 13h.01M10 17h.01M14 17h.01"/></svg>
            <span>{{ job.company }}</span>
          </li>
        }
        @if (job.city) {
          <li>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-6.2-7-11a7 7 0 1 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>
            <span>{{ job.city }}</span>
          </li>
        }
        @if (job.category) {
          <li>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.6 13.4 11 3.8a2 2 0 0 0-1.4-.6H4v5.6a2 2 0 0 0 .6 1.4l9.6 9.6a2 2 0 0 0 2.8 0l3.6-3.6a2 2 0 0 0 0-2.8z"/><path d="M7.5 7.5h.01"/></svg>
            <span>{{ job.category }}</span>
          </li>
        }
      </ul>

      @if (job.employment_type || job.salary) {
        <div class="job-card__badges">
          @if (job.employment_type) { <span class="tag">{{ job.employment_type }}</span> }
          @if (job.salary) { <span class="tag tag--salary">{{ job.salary }}</span> }
        </div>
      }

      <footer class="job-card__foot">
        @if (job.posted_at) {
          <span class="stamp">
            <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4.5" width="18" height="16" rx="2"/><path d="M3 9h18M8 2.5v4M16 2.5v4"/></svg>
            Објавено {{ job.posted_at | date: 'mediumDate' }}
          </span>
        } @else if (job.scraped_at) {
          <span class="stamp">
            <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4.5" width="18" height="16" rx="2"/><path d="M3 9h18M8 2.5v4M16 2.5v4"/></svg>
            Внесено {{ job.scraped_at | date: 'mediumDate' }}
          </span>
        }
        @if (job.active_until) {
          <span class="stamp stamp--until">Важи до {{ job.active_until | date: 'mediumDate' }}</span>
        }
      </footer>
    </article>
  `
})
export class JobCardComponent {
  @Input({ required: true }) job!: Job;
  slug = slugify;
}
