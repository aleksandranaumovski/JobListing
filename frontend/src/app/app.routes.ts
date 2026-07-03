import { Routes } from '@angular/router';

import { JobDetailComponent } from './features/jobs/job-detail.component';
import { JobsPageComponent } from './features/jobs/jobs-page.component';

export const routes: Routes = [
  { path: '', component: JobsPageComponent, title: 'Latest jobs | NVD Jobs' },
  { path: 'search', component: JobsPageComponent, title: 'Патоказ' },
  { path: 'jobs/:id/:slug', component: JobDetailComponent, title: 'Job details | NVD Jobs' },
  { path: '**', redirectTo: '' }
];
