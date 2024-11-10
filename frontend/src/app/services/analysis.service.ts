import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

const baseUrl = environment.apiUrl;

@Injectable({
  providedIn: 'root'
})
export class AnalysisService {

  constructor(private http: HttpClient) { }



  analyzeCode(code: string): Observable<any> {
    return this.http.post(`${baseUrl}/analyzeCode`, { code });
  }

  analyzeUrl(url: string): Observable<any> {
    return this.http.post(`${baseUrl}/analyzeUrl`, { url });
  }

  analyzeFile(fileContent: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', fileContent, fileContent.name);  
    return this.http.post(`${baseUrl}/analyzeFile`, formData);
  }
  

}
