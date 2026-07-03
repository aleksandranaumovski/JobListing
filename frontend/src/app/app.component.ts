import { Component } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';

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
      </nav>
    </header>
    <main>
      <router-outlet />
    </main>
  `
})
export class AppComponent {}
