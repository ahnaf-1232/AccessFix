import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AnalysisService {

  constructor(private http: HttpClient) { }

  analyzeCode(code: string): Observable<any> {
    return this.http.post('/api/analyzeCode', { code });
  }

  analyzeUrl(url: string): Observable<any> {
    return this.http.post('/api/analyzeUrl', { url });
  }
  
  analyzeFile(fileContent: string): Observable<any> {
    return this.http.post('/api/analyzeFile', { content: fileContent });
  }
}
