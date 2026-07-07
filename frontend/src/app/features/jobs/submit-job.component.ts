import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { JobsApiService } from '../../core/jobs-api.service';
import { JobSubmission } from '../../core/models';

@Component({
  selector: 'app-submit-job',
  standalone: true,
  imports: [FormsModule],
  template: `
    <section class="auth">
      <form class="auth-card auth-card--wide" (ngSubmit)="submit()">
        <p class="eyebrow">Нов оглас</p>
        <h1 class="auth-title">Додади оглас за вработување</h1>
        <p class="auth-note">Огласот ќе биде објавен откако ќе го одобри администратор.</p>
        @if (error()) {
          <div class="state state--error">{{ error() }}</div>
        }
        <div class="form-grid">
          <label class="span-2">
            Наслов на позицијата *
            <input name="title" [(ngModel)]="form.title" required placeholder="Пример: Софтверски инженер">
          </label>
          <label>
            Компанија *
            <input name="company" [(ngModel)]="form.company" required placeholder="Име на компанијата">
          </label>
          <label>
            Град
            <input name="city" [(ngModel)]="form.city" placeholder="Пример: Скопје">
          </label>
          <label>
            Категорија
            <input name="category" [(ngModel)]="form.category" placeholder="Пример: Информатичка технологија">
          </label>
          <label>
            Вид на работа
            <select name="employment_type" [(ngModel)]="form.employment_type">
              <option value="">Избери</option>
              <option value="Полно работно време">Полно работно време</option>
              <option value="Скратено работно време">Скратено работно време</option>
              <option value="Пракса">Пракса</option>
              <option value="Хонорарно">Хонорарно</option>
            </select>
          </label>
          <label>
            Плата
            <input name="salary" [(ngModel)]="form.salary" placeholder="Пример: 40.000 - 60.000 МКД">
          </label>
          <label>
            Активен до
            <input name="active_until" type="date" [(ngModel)]="form.active_until">
          </label>
          <label class="span-2">
            Линк за аплицирање
            <input name="url" type="url" [(ngModel)]="form.url" placeholder="https://...">
          </label>
          <label class="span-2">
            Опис на огласот
            <textarea name="description" [(ngModel)]="form.description" rows="8" placeholder="Опиши ги обврските, условите и потребните квалификации"></textarea>
          </label>
        </div>
        <button type="submit" [disabled]="loading()">{{ loading() ? 'Се испраќа...' : 'Испрати оглас' }}</button>
      </form>
    </section>
  `
})
export class SubmitJobComponent {
  private readonly api = inject(JobsApiService);
  private readonly router = inject(Router);

  form: JobSubmission = { title: '', company: '' };
  loading = signal(false);
  error = signal<string | null>(null);

  submit(): void {
    if (this.form.title.trim().length < 3) {
      this.error.set('Внеси наслов на позицијата (најмалку 3 карактери).');
      return;
    }
    if (!this.form.company.trim()) {
      this.error.set('Внеси име на компанијата.');
      return;
    }
    this.loading.set(true);
    this.error.set(null);
    const payload = Object.fromEntries(
      Object.entries(this.form).filter(([, value]) => value !== '' && value !== undefined && value !== null)
    ) as unknown as JobSubmission;
    this.api.submit(payload).subscribe({
      next: () => this.router.navigate(['/my-jobs'], { queryParams: { submitted: 1 } }),
      error: () => {
        this.loading.set(false);
        this.error.set('Огласот не можеше да се испрати. Обиди се повторно.');
      }
    });
  }
}
