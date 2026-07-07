import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterOutlet } from '@angular/router';

import { AuthService } from './core/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterLink, RouterOutlet],
  template: `
    <header class="topbar">
      <a routerLink="/" class="brand">ОГЛАСИ ЗА ВРАБОТУВАЊЕ</a>
      <nav>
        <a routerLink="/">Најнови</a>
        <a routerLink="/search">Пребарај</a>
        @if (auth.isLoggedIn()) {
          <a routerLink="/submit">Додади оглас</a>
          <a routerLink="/my-jobs">Мои огласи</a>
          @if (auth.isAdmin()) {
            <a routerLink="/admin/approvals">Одобрување</a>
          }
        }
      </nav>
      <div class="topbar__auth">
        @if (auth.isLoggedIn()) {
          <span class="topbar__user">{{ auth.user()?.full_name }}</span>
          <button type="button" class="secondary topbar__logout" (click)="logout()">Одјави се</button>
        } @else {
          <a routerLink="/login" class="topbar__login">Најава</a>
          <a routerLink="/register" class="apply topbar__register">Регистрација</a>
        }
      </div>
    </header>
    <main>
      <router-outlet />
    </main>
  `
})
export class AppComponent {
  readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/']);
  }
}
