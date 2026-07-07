import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, RouterLink],
  template: `
    <section class="auth">
      <form class="auth-card" (ngSubmit)="submit()">
        <p class="eyebrow">Добредојде назад</p>
        <h1 class="auth-title">Најави се</h1>
        @if (error()) {
          <div class="state state--error">{{ error() }}</div>
        }
        <label>
          Е-пошта
          <input name="email" type="email" [(ngModel)]="email" required autocomplete="email" placeholder="ime@primer.mk">
        </label>
        <label>
          Лозинка
          <input name="password" type="password" [(ngModel)]="password" required autocomplete="current-password" placeholder="Твојата лозинка">
        </label>
        <button type="submit" [disabled]="loading()">{{ loading() ? 'Се најавува...' : 'Најави се' }}</button>
        <p class="auth-switch">Немаш профил? <a routerLink="/register">Регистрирај се</a></p>
      </form>
    </section>
  `
})
export class LoginComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  email = '';
  password = '';
  loading = signal(false);
  error = signal<string | null>(null);

  submit(): void {
    if (!this.email || !this.password) {
      this.error.set('Внеси е-пошта и лозинка.');
      return;
    }
    this.loading.set(true);
    this.error.set(null);
    this.auth.login(this.email, this.password).subscribe({
      next: () => {
        const redirect = this.route.snapshot.queryParamMap.get('redirect');
        this.router.navigateByUrl(redirect && redirect.startsWith('/') ? redirect : '/');
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err?.status === 401 ? 'Погрешна е-пошта или лозинка.' : 'Најавата не успеа. Обиди се повторно.');
      }
    });
  }
}
