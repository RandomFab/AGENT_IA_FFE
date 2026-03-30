import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { inject, Injectable } from "@angular/core";


@Injectable({ providedIn: 'root' })
export class ApiService {
    private http = inject(HttpClient);
    private readonly BASE_URL = 'http://localhost:8000/api/v1';
    post<T, U>(endpoint: string, data: U): Observable<T> {
        return this.http.post<T>(`${this.BASE_URL}/${endpoint}`, data);
    }
}