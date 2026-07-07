import { Routes } from '@angular/router';

import { adminGuard, authGuard } from './core/auth.guard';
import { AdminJobsComponent } from './features/admin/admin-jobs.component';
import { LoginComponent } from './features/auth/login.component';
import { RegisterComponent } from './features/auth/register.component';
import { JobDetailComponent } from './features/jobs/job-detail.component';
import { JobsPageComponent } from './features/jobs/jobs-page.component';
import { MyJobsComponent } from './features/jobs/my-jobs.component';
import { SubmitJobComponent } from './features/jobs/submit-job.component';

export const routes: Routes = [
  { path: '', component: JobsPageComponent, title: 'ТвојПознаник' },
  { path: 'search', component: JobsPageComponent, title: 'Патоказ' },
  { path: 'login', component: LoginComponent, title: 'Најава | ТвојПознаник' },
  { path: 'register', component: RegisterComponent, title: 'Регистрација | ТвојПознаник' },
  { path: 'submit', component: SubmitJobComponent, canActivate: [authGuard], title: 'Додади оглас | ТвојПознаник' },
  { path: 'my-jobs', component: MyJobsComponent, canActivate: [authGuard], title: 'Мои огласи | ТвојПознаник' },
  { path: 'admin/approvals', component: AdminJobsComponent, canActivate: [adminGuard], title: 'Одобрување | ТвојПознаник' },
  { path: 'jobs/:id/:slug', component: JobDetailComponent, title: 'Job details | ТвојПознаник' },
  { path: '**', redirectTo: '' }
];
