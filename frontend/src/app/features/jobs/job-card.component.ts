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
      <div class="job-card__source">{{ job.source }}</div>
      <h2><a [routerLink]="['/jobs', job.id, slug(job.title)]">{{ job.title }}</a></h2>
      <div class="meta">
        @if (job.company) { <span>{{ job.company }}</span> }
        @if (job.city) { <span>{{ job.city }}</span> }
        @if (job.category) { <span>{{ job.category }}</span> }
      </div>
      <div class="badges">
        @if (job.employment_type) { <span>{{ job.employment_type }}</span> }
        @if (job.salary) { <span>{{ job.salary }}</span> }
        @if (job.is_new) { <span>Ново</span> }
      </div>
      <footer>
        @if (job.posted_at) {
          <span>Објавено {{ job.posted_at | date: 'mediumDate' }}</span>
        } @else if (job.scraped_at) {
          <span>Внесено {{ job.scraped_at | date: 'mediumDate' }}</span>
        }
        @if (job.active_until) { <span>Важи до {{ job.active_until | date: 'mediumDate' }}</span> }
      </footer>
    </article>
  `
})
export class JobCardComponent {
  @Input({ required: true }) job!: Job;
  slug = slugify;
}
