import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, RouterLink],
  template: `
    <section class="auth">
      <form class="auth-card" (ngSubmit)="submit()">
        <p class="eyebrow">Создади профил</p>
        <h1 class="auth-title">Регистрирај се</h1>
        @if (error()) {
          <div class="state state--error">{{ error() }}</div>
        }
        <label>
          Име и презиме
          <input name="fullName" [(ngModel)]="fullName" required autocomplete="name" placeholder="Пример: Ана Анастасова">
        </label>
        <label>
          Е-пошта
          <input name="email" type="email" [(ngModel)]="email" required autocomplete="email" placeholder="ime@primer.mk">
        </label>
        <label>
          Лозинка
          <input name="password" type="password" [(ngModel)]="password" required minlength="8" autocomplete="new-password" placeholder="Најмалку 8 карактери">
        </label>
        <button type="submit" [disabled]="loading()">{{ loading() ? 'Се регистрира...' : 'Регистрирај се' }}</button>
        <p class="auth-switch">Веќе имаш профил? <a routerLink="/login">Најави се</a></p>
      </form>
    </section>
  `
})
export class RegisterComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  fullName = '';
  email = '';
  password = '';
  loading = signal(false);
  error = signal<string | null>(null);

  submit(): void {
    if (this.fullName.trim().length < 2) {
      this.error.set('Внеси име и презиме.');
      return;
    }
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(this.email)) {
      this.error.set('Внеси валидна е-пошта.');
      return;
    }
    if (this.password.length < 8) {
      this.error.set('Лозинката мора да има најмалку 8 карактери.');
      return;
    }
    this.loading.set(true);
    this.error.set(null);
    this.auth.register(this.fullName.trim(), this.email, this.password).subscribe({
      next: () => this.router.navigate(['/']),
      error: (err) => {
        this.loading.set(false);
        this.error.set(err?.status === 409 ? 'Веќе постои профил со оваа е-пошта.' : 'Регистрацијата не успеа. Обиди се повторно.');
      }
    });
  }
}
