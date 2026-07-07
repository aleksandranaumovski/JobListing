import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { AuthResponse, User } from './models';

const STORAGE_KEY = 'nvd_auth';

interface StoredAuth {
  token: string;
  user: User;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api/auth';

  private readonly state = signal<StoredAuth | null>(restore());

  readonly user = computed(() => this.state()?.user ?? null);
  readonly isLoggedIn = computed(() => this.state() !== null);
  readonly isAdmin = computed(() => this.state()?.user.role === 'admin');

  get token(): string | null {
    return this.state()?.token ?? null;
  }

  login(email: string, password: string): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${this.baseUrl}/login`, { email, password })
      .pipe(tap((res) => this.persist(res)));
  }

  register(fullName: string, email: string, password: string): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${this.baseUrl}/register`, { full_name: fullName, email, password })
      .pipe(tap((res) => this.persist(res)));
  }

  logout(): void {
    this.state.set(null);
    localStorage.removeItem(STORAGE_KEY);
  }

  private persist(res: AuthResponse): void {
    const stored: StoredAuth = { token: res.access_token, user: res.user };
    this.state.set(stored);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(stored));
  }
}

function restore(): StoredAuth | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw) as StoredAuth;
    return parsed.token && parsed.user ? parsed : null;
  } catch {
    return null;
  }
}
