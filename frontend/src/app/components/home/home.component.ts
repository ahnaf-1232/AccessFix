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

  constructor(private codeAnalysisService: AnalysisService) { } 

  handleSubmit(): void {
    this.errorMessage = ''; 

    if (this.code) {
      this.codeAnalysisService.analyzeCode(this.code).subscribe(
        response => this.report = response,
        error => this.report = 'Error analyzing code.'
      );
    } else if (this.url) {
      this.codeAnalysisService.analyzeUrl(this.url).subscribe(
        response => this.report = response,
        error => this.report = 'Error analyzing URL.'
      );
    } else if (this.fileContent) {
      this.codeAnalysisService.analyzeFile(this.fileContent).subscribe(
        response => this.report = response,
        error => this.report = 'Error analyzing file.'
      );
    } else {
      this.errorMessage = 'Please enter code, select a file, or enter a URL.';
    }
  }

  handleFileChange(input: any): void {
    const file = input.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.fileContent = e.target.result; // Load the file content
        this.code = ''; // Clear the code input if file is loaded
      };
      reader.readAsText(file);
      this.selectedFileName = file.name; // Update the file name to display
    }
  }
}
