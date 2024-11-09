import { Component } from '@angular/core';
import { AnalysisService } from '../../services/analysis.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  report: any;
  title: string = 'AccessFix';
  code: string = '';
  url: string = '';
  fileContent: string = '';
  errorMessage: string = '';
  selectedFileName: string = 'Select a file';
  loading: boolean = false;

  constructor(private codeAnalysisService: AnalysisService) {}

  handleSubmit(): void {
    this.errorMessage = '';
    this.loading = true;
    this.report = null;

    if (this.code) {
      this.codeAnalysisService.analyzeCode(this.code).subscribe(
        response => {
          this.report = JSON.stringify(response, null, 2);
          this.clearFields();
          this.loading = false;
        },
        error => {
          this.errorMessage = 'Error analyzing code.';
          this.loading = false;
        }
      );
    } else if (this.url) {
      this.codeAnalysisService.analyzeUrl(this.url).subscribe(
        response => {
          this.report = JSON.stringify(response, null, 2);
          this.clearFields();
          this.loading = false;
        },
        error => {
          this.errorMessage = 'Error analyzing URL.';
          this.loading = false;
        }
      );
    } else if (this.fileContent) {
      this.codeAnalysisService.analyzeFile(this.fileContent).subscribe(
        response => {
          this.report = JSON.stringify(response, null, 2);
          this.clearFields();
          this.loading = false;
        },
        error => {
          this.errorMessage = 'Error analyzing file.';
          this.loading = false;
        }
      );
    } else {
      this.errorMessage = 'Please enter code, select a file, or enter a URL.';
      this.loading = false;
    }
  }

  handleFileChange(input: any): void {
    const file = input.files[0];
    if (file ) { // Check for plain text files
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.fileContent = e.target.result;
        this.code = '';
      };
      reader.readAsText(file);
      this.selectedFileName = file.name;
    } else {
      this.errorMessage = 'Please select a valid text file.';
      this.selectedFileName = 'Select a file';
    }
  }

  clearFields(): void {
    this.code = '';
    this.url = '';
    this.fileContent = '';
    this.selectedFileName = 'Select a file';
  }
}
