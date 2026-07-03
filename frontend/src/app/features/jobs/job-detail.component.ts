import { DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Title } from '@angular/platform-browser';

import { JobsApiService } from '../../core/jobs-api.service';
import { Job } from '../../core/models';

@Component({
  selector: 'app-job-detail',
  standalone: true,
  imports: [DatePipe, RouterLink],
  template: `
    <section class="detail">
      <a routerLink="/search" class="back">Back to jobs</a>
      @if (loading()) {
        <div class="state">Loading job...</div>
      } @else if (error()) {
        <div class="state state--error">{{ error() }}</div>
      } @else if (job()) {
        <article>
          <p class="eyebrow">{{ job()?.source }}</p>
          <h1>{{ job()?.title }}</h1>
          <div class="meta meta--large">
            @if (job()?.company) { <span>{{ job()?.company }}</span> }
            @if (job()?.city) { <span>{{ job()?.city }}</span> }
            @if (job()?.category) { <span>{{ job()?.category }}</span> }
            @if (job()?.employment_type) { <span>{{ job()?.employment_type }}</span> }
          </div>
          <dl>
            @if (job()?.salary) { <div><dt>Salary</dt><dd>{{ job()?.salary }}</dd></div> }
            @if (job()?.posted_at) { <div><dt>Posted</dt><dd>{{ job()?.posted_at | date: 'longDate' }}</dd></div> }
            @if (job()?.active_until) { <div><dt>Active until</dt><dd>{{ job()?.active_until | date: 'longDate' }}</dd></div> }
          </dl>
          @if (job()?.raw_text) {
            <h2>Scraped description</h2>
            <p class="raw">{{ job()?.raw_text }}</p>
          }
          @if (job()?.url) {
            <a class="apply" [href]="job()?.url" target="_blank" rel="noopener">Open original advertisement</a>
          }
        </article>
      }
    </section>
  `
})
export class JobDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(JobsApiService);
  private readonly title = inject(Title);

  job = signal<Job | null>(null);
  loading = signal(true);
  error = signal<string | null>(null);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.error.set('Missing job id.');
      this.loading.set(false);
      return;
    }
    this.api.detail(id).subscribe({
      next: (job) => {
        this.job.set(job);
        this.title.setTitle(`${job.title} | NVD Jobs`);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Job advertisement was not found.');
        this.loading.set(false);
      }
    });
  }
}
