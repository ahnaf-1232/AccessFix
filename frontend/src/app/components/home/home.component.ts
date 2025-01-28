import { Component } from "@angular/core"
import { AnalysisService } from "../../services/analysis.service"
import type { Analysis } from "src/app/models/analysis"
import { HttpClient } from "@angular/common/http"
import { trigger, transition, style, animate } from "@angular/animations"

@Component({
  selector: "app-home",
  templateUrl: "./home.component.html",
  styleUrls: ["./home.component.css"],
  animations: [
    trigger("fadeIn", [transition(":enter", [style({ opacity: 0 }), animate("300ms", style({ opacity: 1 }))])]),
    trigger("slideInRight", [
      transition(":enter", [
        style({ transform: "translateX(100%)", opacity: 0 }),
        animate("500ms ease-out", style({ transform: "translateX(0)", opacity: 1 })),
      ]),
    ]),
  ],
})
export class HomeComponent {
  report: Analysis | null = null
  title = "AccessFix"
  code = ""
  url = ""
  fileContent: File | null = null
  errorMessage = ""
  selectedFileName = "Select a file"
  loading = false

  showChat = false
  messages: { text: string; sender: string }[] = []
  userInput = ""
  cardStates: boolean[] = []

  constructor(
    private codeAnalysisService: AnalysisService,
    private http: HttpClient,
  ) { }

  chartOptions = {
    title: 'Severity Levels',
    is3D: true,
  };

  levelChartData: any[] = [];

  toggleCard(index: number) {
    this.cardStates[index] = !this.cardStates[index]
  }

  calculateLevelChartData(): void {
    if (!this.report || !this.report.csv_file_path) {
      return;
    }
    const levels = this.report.csv_file_path.reduce((acc: { [key: string]: number }, item) => {
      acc[item.level] = (acc[item.level] || 0) + 1;
      return acc;
    }, {});

    this.levelChartData = Object.entries(levels).map(([key, value]) => [key, value]);
  }

  copyCodeToClipboard() {
    if (this.report && this.report.corrected_html) {
      navigator.clipboard.writeText(this.report.corrected_html).then(
        () => {
          // You can add a notification here to inform the user that the code was copied
          console.log("Code copied to clipboard")
        },
        (err) => {
          console.error("Could not copy text: ", err)
        },
      )
    }
  }

  handleSubmit(): void {
    this.errorMessage = ""
    this.loading = true
    this.report = null

    if (this.code) {
      this.codeAnalysisService.analyzeCode(this.code).subscribe(
        response => {
          console.log('Received response:', response); 
          this.report = response;
          console.log(this.report?.csv_file_path); 
          this.loading = false;
        },
        error => {
          console.error('Error during code analysis:', error);
          this.loading = false;
        }
      );

    } else if (this.url) {
      this.codeAnalysisService.analyzeUrl(this.url).subscribe(
        (response) => {
          this.report = response
          // this.clearFields();
          this.loading = false
        },
        (error) => {
          this.errorMessage = "Error analyzing URL."
          this.loading = false
        },
      )
    } else if (this.fileContent) {
      const file = this.fileContent // Directly use the file here, not FormData

      // Send file object to analyzeFile method
      this.codeAnalysisService.analyzeFile(file).subscribe(
        (response) => {
          this.report = response
          // this.clearFields();
          this.loading = false
        },
        (error) => {
          this.errorMessage = "Error analyzing file."
          this.loading = false
        },
      )
    } else {
      this.errorMessage = "Please enter code, select a file, or enter a URL."
      this.loading = false
    }
  }

  handleFileChange(input: any): void {
    const file = input.files[0]
    if (file) {
      this.fileContent = file
      this.code = "" // Clear code if file is selected
      this.selectedFileName = file.name
    } else {
      this.errorMessage = "Please select a valid file."
      this.selectedFileName = "Select a file"
    }
  }

  toggleChat() {
    this.showChat = !this.showChat
    if (!this.showChat) {
      this.messages = [] // Clean chat when closed
    }
  }

  sendMessage() {
    if (this.userInput.trim()) {
      const userInput = this.userInput.trim()
      this.messages.push({ text: userInput, sender: "user" })

      this.codeAnalysisService.chatResponse(userInput).subscribe(
        (response) => {
          this.messages.push({ text: response.text, sender: "bot" })
          this.userInput = ""
        },
        (error) => {
          console.error(`Error fetching response: ${error}`) // Debug error
          this.errorMessage = "Error fetching response."
        },
      )
    }
  }

  downloadReport() {
    if (!this.report || !this.report.csv_file_path) {
      console.error("No report data available")
      return
    }

    let reportContent = "Accessibility Analysis Report\n\n"
    reportContent += `Total Initial Severity Score: ${this.report.total_initial_severity_score}\n`
    reportContent += `Total Final Severity Score: ${this.report.total_final_severity_score}\n`
    reportContent += `Total Improvement: ${this.report.total_improvement.toFixed(2)}%\n\n`

    reportContent += "Guideline Details:\n\n"

    this.report.csv_file_path.forEach((detail, index) => {
      reportContent += `${index + 1}. Error: ${detail.error}\n`
      reportContent += `   Level: ${detail.level}\n`
      reportContent += `   Reference: ${detail.reference}\n`
      reportContent += `   Fix: ${detail.fix}\n`
      reportContent += `   Description: ${detail.description}\n\n`
    })

    reportContent += "Corrected HTML:\n\n"
    reportContent += this.report.corrected_html

    const blob = new Blob([reportContent], { type: "text/plain" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "accessibility_report.txt"
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }


  clearFields(): void {
    this.code = ""
    this.url = ""
    this.fileContent = null
    this.selectedFileName = "Select a file"
  }
}

